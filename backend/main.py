import asyncio
import logging
import sys
from datetime import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from database import init_db, get_recent_trades, get_stats, save_ai_decision, save_balance
from deriv_ws import deriv_ws
from indicators import calculate_indicators
from ai_analyst import analyze
from executor import executor
from ws_server import start_server, broadcast, update_state, get_state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class BotController:
    def __init__(self):
        self.running = False
        self._task = None
        self.asset = settings.ASSET
        self.trade_value = settings.TRADE_VALUE
        self.mode = settings.MODE

    async def start(self):
        if self.running:
            return
        self.running = True
        update_state({"status": "RODANDO", "error": None})
        await broadcast()
        self._task = asyncio.create_task(self._loop())
        logger.info("Bot iniciado")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None
        update_state({"status": "PARADO"})
        await broadcast()
        logger.info("Bot parado")

    async def update_config(self, data: dict):
        if "asset" in data:
            self.asset = data["asset"]
            settings.ASSET = data["asset"]
        if "trade_value" in data:
            self.trade_value = float(data["trade_value"])
            settings.TRADE_VALUE = self.trade_value
        if "mode" in data:
            self.mode = data["mode"]
            settings.MODE = data["mode"]
        update_state({"asset": self.asset, "mode": self.mode})
        await broadcast()

    async def _loop(self):
        last_candle_time = None
        try:
            while self.running:
                candles = deriv_ws.candles
                balance = deriv_ws.balance

                if candles:
                    latest_time = candles[-1]["time"]
                    if latest_time != last_candle_time:
                        last_candle_time = latest_time
                        await self._on_new_candle(candles, balance)

                trades = await get_recent_trades(20)
                stats = await get_stats()
                update_state({
                    "candles": candles[-100:],
                    "recent_trades": trades,
                    "stats": stats,
                    "balance": balance,
                    "asset": self.asset,
                    "mode": self.mode,
                })
                await broadcast()
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}", exc_info=True)
            update_state({"status": "ERRO", "error": str(e)})
            await broadcast()

    async def _on_new_candle(self, candles: list, balance: float):
        indicators = calculate_indicators(candles)
        if not indicators:
            logger.info("Indicadores insuficientes, aguardando mais dados...")
            return

        logger.info(f"Candle fechado | Close: {indicators['close']} | RSI: {indicators['rsi_14']} | Trend: {indicators['trend']}")

        ai_result = await asyncio.get_event_loop().run_in_executor(
            None, analyze, indicators, self.asset
        )

        decision = ai_result["decision"]
        reason = ai_result["reason"]
        confidence = ai_result["confidence"]

        logger.info(f"IA: {decision} ({confidence}) - {reason}")

        await save_ai_decision(indicators, decision, reason)

        last_decision = {
            "decision": decision,
            "reason": reason,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "indicators": indicators,
        }
        update_state({"last_decision": last_decision})

        if decision in ("CALL", "PUT"):
            result = await executor.execute(
                decision=decision,
                reason=reason,
                asset=self.asset,
                amount=self.trade_value,
                balance=balance,
            )

            if result.get("result"):
                last_decision["result"] = result["result"]
                last_decision["pnl"] = result.get("pnl", 0)
                update_state({"last_decision": last_decision})

                new_balance = await deriv_ws.get_balance()
                await save_balance(new_balance)
                update_state({"balance": new_balance})


bot_controller = BotController()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Banco de dados inicializado")

    await deriv_ws.connect()
    await deriv_ws.subscribe_candles(settings.ASSET)
    balance = await deriv_ws.get_balance()
    await save_balance(balance)
    update_state({"balance": balance, "asset": settings.ASSET, "mode": settings.MODE})

    ws_server = await start_server()

    yield

    await bot_controller.stop()
    ws_server.close()
    if deriv_ws.ws:
        await deriv_ws.ws.close()


app = FastAPI(title="Trading Bot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConfigUpdate(BaseModel):
    asset: str = None
    trade_value: float = None
    mode: str = None


@app.get("/status")
async def get_status():
    return get_state()


@app.post("/start")
async def start_bot():
    await bot_controller.start()
    return {"status": "started"}


@app.post("/stop")
async def stop_bot():
    await bot_controller.stop()
    return {"status": "stopped"}


@app.post("/config")
async def update_config(config: ConfigUpdate):
    data = config.model_dump(exclude_none=True)
    await bot_controller.update_config(data)
    return {"status": "updated", "config": data}


@app.get("/trades")
async def get_trades():
    return await get_recent_trades(50)


@app.get("/stats")
async def get_statistics():
    return await get_stats()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

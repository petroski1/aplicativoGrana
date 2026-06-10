import asyncio
import json
import logging
from datetime import datetime
import websockets
from config import settings

logger = logging.getLogger(__name__)


class DerivWS:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.candles: list = []
        self.balance: float = 0.0
        self._req_id = 0
        self._pending: dict = {}
        self._listener_task = None
        self._subscribed_asset = None

    def _next_req_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def connect(self):
        retry_delay = 2
        while True:
            try:
                self.ws = await websockets.connect(settings.DERIV_WS_URL, ping_interval=20)
                self.connected = True
                logger.info("Conectado à Deriv API")
                self._listener_task = asyncio.create_task(self._listener())
                await self._authorize()
                return
            except Exception as e:
                logger.error(f"Falha ao conectar: {e}. Tentando em {retry_delay}s...")
                self.connected = False
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)

    async def _authorize(self):
        if not settings.DERIV_TOKEN or settings.DERIV_TOKEN == "your_deriv_token_here":
            logger.warning("DERIV_TOKEN não configurado, operando sem autenticação")
            return

        req_id = self._next_req_id()
        fut = asyncio.get_event_loop().create_future()
        self._pending[req_id] = fut
        await self._send({"authorize": settings.DERIV_TOKEN, "req_id": req_id})
        try:
            resp = await asyncio.wait_for(fut, timeout=10)
            if "authorize" in resp:
                self.balance = resp["authorize"].get("balance", 0.0)
                logger.info(f"Autorizado. Saldo: {self.balance}")
        except asyncio.TimeoutError:
            logger.error("Timeout na autorização")

    async def _listener(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                req_id = data.get("req_id")
                if req_id and req_id in self._pending:
                    self._pending.pop(req_id).set_result(data)
                elif "ohlc" in data:
                    self._handle_ohlc(data["ohlc"])
                elif "tick" in data:
                    pass
        except websockets.ConnectionClosed:
            logger.warning("Conexão fechada, reconectando...")
            self.connected = False
            asyncio.create_task(self._reconnect())
        except Exception as e:
            logger.error(f"Erro no listener: {e}")
            self.connected = False
            asyncio.create_task(self._reconnect())

    async def _reconnect(self):
        await asyncio.sleep(2)
        await self.connect()
        if self._subscribed_asset:
            await self.subscribe_candles(self._subscribed_asset)

    def _handle_ohlc(self, ohlc: dict):
        candle = {
            "time": ohlc.get("open_time", int(datetime.utcnow().timestamp())),
            "open": float(ohlc.get("open", 0)),
            "high": float(ohlc.get("high", 0)),
            "low": float(ohlc.get("low", 0)),
            "close": float(ohlc.get("close", 0)),
            "volume": 0,
        }
        if self.candles and self.candles[-1]["time"] == candle["time"]:
            self.candles[-1] = candle
        else:
            self.candles.append(candle)
            if len(self.candles) > 500:
                self.candles = self.candles[-500:]

    async def _send(self, data: dict):
        if self.ws and self.connected:
            await self.ws.send(json.dumps(data))

    async def subscribe_candles(self, asset: str, granularity: int = 60):
        self._subscribed_asset = asset
        await self.get_candles_history(asset, count=100, granularity=granularity)

        req_id = self._next_req_id()
        await self._send({
            "ticks_history": asset,
            "adjust_start_time": 1,
            "count": 10,
            "end": "latest",
            "granularity": granularity,
            "style": "candles",
            "subscribe": 1,
            "req_id": req_id,
        })
        logger.info(f"Subscrito em candles de {asset}")

    async def get_candles_history(self, asset: str, count: int = 100, granularity: int = 60):
        req_id = self._next_req_id()
        fut = asyncio.get_event_loop().create_future()
        self._pending[req_id] = fut
        await self._send({
            "ticks_history": asset,
            "adjust_start_time": 1,
            "count": count,
            "end": "latest",
            "granularity": granularity,
            "style": "candles",
            "req_id": req_id,
        })
        try:
            resp = await asyncio.wait_for(fut, timeout=15)
            if "candles" in resp:
                self.candles = [
                    {
                        "time": c["epoch"],
                        "open": float(c["open"]),
                        "high": float(c["high"]),
                        "low": float(c["low"]),
                        "close": float(c["close"]),
                        "volume": 0,
                    }
                    for c in resp["candles"]
                ]
                logger.info(f"Histórico carregado: {len(self.candles)} candles")
        except asyncio.TimeoutError:
            logger.error("Timeout ao buscar histórico")

    async def get_balance(self) -> float:
        if not settings.DERIV_TOKEN or settings.DERIV_TOKEN == "your_deriv_token_here":
            return self.balance

        req_id = self._next_req_id()
        fut = asyncio.get_event_loop().create_future()
        self._pending[req_id] = fut
        await self._send({"balance": 1, "req_id": req_id})
        try:
            resp = await asyncio.wait_for(fut, timeout=10)
            if "balance" in resp:
                self.balance = float(resp["balance"].get("balance", self.balance))
        except asyncio.TimeoutError:
            pass
        return self.balance

    async def buy_contract(self, asset: str, direction: str, amount: float, duration: int) -> dict:
        contract_type = "CALL" if direction == "CALL" else "PUT"
        req_id = self._next_req_id()
        fut = asyncio.get_event_loop().create_future()
        self._pending[req_id] = fut

        await self._send({
            "buy": 1,
            "price": amount,
            "parameters": {
                "amount": amount,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": duration,
                "duration_unit": "m",
                "symbol": asset,
            },
            "req_id": req_id,
        })

        try:
            resp = await asyncio.wait_for(fut, timeout=15)
            if "buy" in resp:
                contract_id = resp["buy"].get("contract_id")
                logger.info(f"Contrato comprado: {contract_id}")
                await asyncio.sleep(duration * 60 + 5)
                return await self._get_contract_result(contract_id)
            elif "error" in resp:
                return {"error": resp["error"].get("message", "Erro desconhecido")}
        except asyncio.TimeoutError:
            return {"error": "Timeout ao comprar contrato"}

        return {"error": "Resposta inválida"}

    async def _get_contract_result(self, contract_id: int) -> dict:
        req_id = self._next_req_id()
        fut = asyncio.get_event_loop().create_future()
        self._pending[req_id] = fut
        await self._send({"proposal_open_contract": 1, "contract_id": contract_id, "req_id": req_id})
        try:
            resp = await asyncio.wait_for(fut, timeout=10)
            if "proposal_open_contract" in resp:
                poc = resp["proposal_open_contract"]
                profit = float(poc.get("profit", 0))
                status = poc.get("status", "sold")
                result = "WIN" if profit > 0 else "LOSS"
                return {"result": result, "pnl": profit, "contract_id": contract_id}
        except asyncio.TimeoutError:
            pass
        return {"result": "UNKNOWN", "pnl": 0, "contract_id": contract_id}


deriv_ws = DerivWS()

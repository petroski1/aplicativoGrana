import asyncio
import json
import logging
import websockets
from config import settings

logger = logging.getLogger(__name__)

_clients: set = set()
_state: dict = {
    "status": "PARADO",
    "candles": [],
    "recent_trades": [],
    "stats": {},
    "last_decision": None,
    "balance": 0.0,
    "mode": settings.MODE,
    "asset": settings.ASSET,
    "error": None,
}


def get_state() -> dict:
    return _state


def update_state(updates: dict):
    _state.update(updates)


async def broadcast(data: dict = None):
    if not _clients:
        return
    payload = json.dumps(data if data is not None else _state)
    disconnected = set()
    for client in _clients:
        try:
            await client.send(payload)
        except websockets.ConnectionClosed:
            disconnected.add(client)
        except Exception as e:
            logger.error(f"Erro ao enviar para cliente: {e}")
            disconnected.add(client)
    _clients.difference_update(disconnected)


async def _handler(websocket):
    _clients.add(websocket)
    logger.info(f"Frontend conectado. Total: {len(_clients)}")
    try:
        from deriv_ws import deriv_ws
        current = dict(_state)
        if deriv_ws.candles:
            current["candles"] = deriv_ws.candles[-100:]
            current["balance"] = deriv_ws.balance
        await websocket.send(json.dumps(current))
        async for message in websocket:
            try:
                data = json.loads(message)
                await _handle_message(data)
            except json.JSONDecodeError:
                pass
    except websockets.ConnectionClosed:
        pass
    finally:
        _clients.discard(websocket)
        logger.info(f"Frontend desconectado. Total: {len(_clients)}")


async def _handle_message(data: dict):
    from main import bot_controller
    action = data.get("action")
    if action == "start":
        await bot_controller.start()
    elif action == "stop":
        await bot_controller.stop()
    elif action == "config":
        await bot_controller.update_config(data)


async def start_server():
    server = await websockets.serve(
        _handler,
        "0.0.0.0",
        settings.WS_PORT,
        ping_interval=30,
        ping_timeout=10,
    )
    logger.info(f"WebSocket server iniciado na porta {settings.WS_PORT}")
    return server

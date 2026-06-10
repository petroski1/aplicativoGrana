import aiosqlite
import json
from datetime import datetime
from config import settings


async def init_db():
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ativo TEXT NOT NULL,
                direcao TEXT NOT NULL,
                valor REAL NOT NULL,
                resultado TEXT,
                pnl REAL DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                indicadores TEXT NOT NULL,
                decisao TEXT NOT NULL,
                motivo TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                saldo REAL NOT NULL
            )
        """)
        await db.commit()


async def save_trade(ativo: str, direcao: str, valor: float, resultado: str = None, pnl: float = 0):
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute(
            "INSERT INTO trades (timestamp, ativo, direcao, valor, resultado, pnl) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), ativo, direcao, valor, resultado, pnl)
        )
        await db.commit()


async def update_trade_result(trade_id: int, resultado: str, pnl: float):
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute(
            "UPDATE trades SET resultado = ?, pnl = ? WHERE id = ?",
            (resultado, pnl, trade_id)
        )
        await db.commit()


async def save_ai_decision(indicadores: dict, decisao: str, motivo: str):
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute(
            "INSERT INTO ai_decisions (timestamp, indicadores, decisao, motivo) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), json.dumps(indicadores), decisao, motivo)
        )
        await db.commit()


async def save_balance(saldo: float):
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute(
            "INSERT INTO balance_history (timestamp, saldo) VALUES (?, ?)",
            (datetime.utcnow().isoformat(), saldo)
        )
        await db.commit()


async def get_recent_trades(n: int = 20) -> list:
    async with aiosqlite.connect(settings.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM trades ORDER BY id DESC LIMIT ?", (n,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_stats() -> dict:
    async with aiosqlite.connect(settings.DB_PATH) as db:
        today = datetime.utcnow().date().isoformat()

        cursor = await db.execute(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN resultado = 'WIN' THEN 1 ELSE 0 END) as wins, "
            "SUM(pnl) as total_pnl "
            "FROM trades"
        )
        row = await cursor.fetchone()
        total = row[0] or 0
        wins = row[1] or 0
        total_pnl = row[2] or 0.0

        cursor = await db.execute(
            "SELECT COUNT(*) FROM trades WHERE timestamp LIKE ?", (f"{today}%",)
        )
        row = await cursor.fetchone()
        trades_today = row[0] or 0

        win_rate = (wins / total * 100) if total > 0 else 0.0

        cursor = await db.execute(
            "SELECT MIN(pnl) FROM trades"
        )
        row = await cursor.fetchone()
        max_drawdown = row[0] or 0.0

        return {
            "total_trades": total,
            "wins": wins,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "trades_today": trades_today,
            "max_drawdown": round(max_drawdown, 2),
        }


async def get_daily_pnl() -> float:
    async with aiosqlite.connect(settings.DB_PATH) as db:
        today = datetime.utcnow().date().isoformat()
        cursor = await db.execute(
            "SELECT COALESCE(SUM(pnl), 0) FROM trades WHERE timestamp LIKE ?",
            (f"{today}%",)
        )
        row = await cursor.fetchone()
        return row[0] or 0.0


async def get_consecutive_losses() -> int:
    async with aiosqlite.connect(settings.DB_PATH) as db:
        cursor = await db.execute(
            "SELECT resultado FROM trades ORDER BY id DESC LIMIT 10"
        )
        rows = await cursor.fetchall()
        count = 0
        for row in rows:
            if row[0] == "LOSS":
                count += 1
            else:
                break
        return count

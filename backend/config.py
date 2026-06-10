from pydantic_settings import BaseSettings
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Settings(BaseSettings):
    DERIV_TOKEN: str = ""
    ANTHROPIC_API_KEY: str = ""
    ASSET: str = "frxEURUSD"
    TRADE_VALUE: float = 1.0
    MODE: Literal["demo", "real"] = "demo"
    DERIV_WS_URL: str = "wss://ws.derivws.com/websockets/v3?app_id=16929"
    TRADE_DURATION: int = 5
    MAX_CONSECUTIVE_LOSSES: int = 3
    MAX_DAILY_LOSS_PCT: float = 5.0
    TRADING_HOURS_START: int = 8
    TRADING_HOURS_END: int = 22
    DB_PATH: str = "trading.db"
    WS_PORT: int = 8765

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
print(f"[CONFIG] DERIV_TOKEN carregado: ...{settings.DERIV_TOKEN[-8:] if settings.DERIV_TOKEN else 'VAZIO'}")

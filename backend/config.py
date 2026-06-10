from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    DERIV_TOKEN: str = ""
    ANTHROPIC_API_KEY: str = ""
    ASSET: str = "frxEURUSD"
    TRADE_VALUE: float = 1.0
    MODE: Literal["demo", "real"] = "demo"
    DERIV_WS_URL: str = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    TRADE_DURATION: int = 5
    MAX_CONSECUTIVE_LOSSES: int = 3
    MAX_DAILY_LOSS_PCT: float = 5.0
    TRADING_HOURS_START: int = 8
    TRADING_HOURS_END: int = 22
    DB_PATH: str = "trading.db"
    WS_PORT: int = 8765

    class Config:
        env_file = ".env"


settings = Settings()

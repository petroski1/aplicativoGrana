import pandas as pd
import pandas_ta as ta
from typing import Optional


def calculate_indicators(candles: list) -> Optional[dict]:
    if len(candles) < 26:
        return None

    df = pd.DataFrame(candles)
    df.columns = [c.lower() for c in df.columns]

    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            df[col] = df.get(col, 0)
    df["volume"] = df.get("volume", pd.Series([0] * len(df)))

    df["open"] = pd.to_numeric(df["open"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"])

    if len(df) < 26:
        return None

    rsi = ta.rsi(df["close"], length=14)
    ema9 = ta.ema(df["close"], length=9)
    ema21 = ta.ema(df["close"], length=21)
    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    bb = ta.bbands(df["close"], length=20)

    def last(series):
        if series is None or len(series) == 0:
            return None
        val = series.iloc[-1]
        return round(float(val), 6) if pd.notna(val) else None

    result = {
        "rsi_14": last(rsi),
        "ema_9": last(ema9),
        "ema_21": last(ema21),
        "close": last(df["close"]),
        "open": last(df["open"]),
        "high": last(df["high"]),
        "low": last(df["low"]),
    }

    if macd is not None and not macd.empty:
        cols = macd.columns.tolist()
        macd_col = next((c for c in cols if "MACD_" in c and "s" not in c.lower()[-1] and "h" not in c.lower()[-1]), None)
        signal_col = next((c for c in cols if "MACDs_" in c), None)
        hist_col = next((c for c in cols if "MACDh_" in c), None)
        result["macd"] = last(macd[macd_col]) if macd_col else None
        result["macd_signal"] = last(macd[signal_col]) if signal_col else None
        result["macd_hist"] = last(macd[hist_col]) if hist_col else None

    if bb is not None and not bb.empty:
        cols = bb.columns.tolist()
        upper_col = next((c for c in cols if "BBU_" in c), None)
        mid_col = next((c for c in cols if "BBM_" in c), None)
        lower_col = next((c for c in cols if "BBL_" in c), None)
        result["bb_upper"] = last(bb[upper_col]) if upper_col else None
        result["bb_mid"] = last(bb[mid_col]) if mid_col else None
        result["bb_lower"] = last(bb[lower_col]) if lower_col else None

    trend = "NEUTRO"
    if result.get("ema_9") and result.get("ema_21"):
        if result["ema_9"] > result["ema_21"]:
            trend = "ALTA"
        elif result["ema_9"] < result["ema_21"]:
            trend = "BAIXA"
    result["trend"] = trend

    return result

"""
Stock data service — fetches live and historical stock data from Yahoo Finance.
Compatible with yfinance 1.x multi-level column format.
"""
import pandas as pd
import yfinance as yf
from app.utils.logger import setup_logger

logger = setup_logger("stock_service")


def fetch_live_data(ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch recent stock data for a ticker.
    Returns DataFrame with columns: Open, High, Low, Close, Volume
    """
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)

        if df.empty:
            logger.warning(f"No data returned for {ticker}")
            return pd.DataFrame()

        # Handle multi-level columns from yfinance 1.x
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Keep only OHLCV
        keep_cols = ["Open", "High", "Low", "Close", "Volume"]
        df = df[[c for c in keep_cols if c in df.columns]]

        return df

    except Exception as e:
        logger.error(f"Failed to fetch {ticker}: {e}")
        return pd.DataFrame()


def get_current_price(ticker: str) -> dict:
    """
    Get the current/latest price info for a ticker.
    Returns dict with: price, open, high, low, volume, change, change_pct
    """
    try:
        df = yf.download(ticker, period="2d", interval="1d", progress=False)

        if df.empty:
            return _empty_price()

        # Handle multi-level columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        latest = df.iloc[-1]
        current_price = float(latest["Close"])

        # Previous close for change calculation
        if len(df) >= 2:
            prev_close = float(df.iloc[-2]["Close"])
        else:
            prev_close = float(latest["Open"])

        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0

        return {
            "price": round(current_price, 2),
            "open": round(float(latest["Open"]), 2),
            "high": round(float(latest["High"]), 2),
            "low": round(float(latest["Low"]), 2),
            "volume": int(latest["Volume"]),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
        }

    except Exception as e:
        logger.error(f"Failed to get price for {ticker}: {e}")
        return _empty_price()


def _empty_price():
    return {"price": 0, "open": 0, "high": 0, "low": 0, "volume": 0, "change": 0, "change_pct": 0}

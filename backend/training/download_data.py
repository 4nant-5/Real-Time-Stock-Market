"""
Download historical OHLCV data from Yahoo Finance for model training.
"""
import os
import sys
import yfinance as yf
import pandas as pd

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.utils.logger import setup_logger

logger = setup_logger("download_data")

TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "historical")


def download_historical_data(tickers: list, period: str = "1y", interval: str = "1d"):
    """Download historical stock data for given tickers."""
    os.makedirs(DATA_DIR, exist_ok=True)

    for ticker in tickers:
        logger.info(f"Downloading {ticker} ({period}, {interval})...")
        try:
            df = yf.download(ticker, period=period, interval=interval)

            if df.empty:
                logger.warning(f"No data returned for {ticker}")
                continue

            # Handle multi-level columns from yfinance 1.x
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Keep only OHLCV columns
            keep_cols = ["Open", "High", "Low", "Close", "Volume"]
            df = df[[c for c in keep_cols if c in df.columns]]

            filepath = os.path.join(DATA_DIR, f"{ticker}.csv")
            df.to_csv(filepath)
            logger.info(f"  ✓ {ticker}: {len(df)} rows → {filepath}")

        except Exception as e:
            logger.error(f"  ✗ Failed to download {ticker}: {e}")

    logger.info("Download complete.")


if __name__ == "__main__":
    download_historical_data(TICKERS)

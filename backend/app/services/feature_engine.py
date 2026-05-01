"""
Feature engineering service — computes technical indicators.
Mirrors the exact features used during model training.
"""
import pandas as pd
import numpy as np


def compute_sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window, min_periods=1).mean()


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    rs = avg_gain / (avg_loss + 1e-10)  # Avoid division by zero
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD line and Signal line."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line


def compute_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators to a price dataframe.

    Expects columns: Open, High, Low, Close, Volume
    Returns dataframe with added: SMA_5, SMA_10, EMA_12, RSI_14, MACD, MACD_Signal
    """
    df = df.copy()

    df["SMA_5"] = compute_sma(df["Close"], 5)
    df["SMA_10"] = compute_sma(df["Close"], 10)
    df["EMA_12"] = compute_ema(df["Close"], 12)
    df["RSI_14"] = compute_rsi(df["Close"], 14)
    df["MACD"], df["MACD_Signal"] = compute_macd(df["Close"])

    return df


def prepare_prediction_input(df: pd.DataFrame, sentiment: float, scaler) -> np.ndarray:
    """
    Prepare a single prediction input vector from the latest row of data.

    Args:
        df: DataFrame with OHLCV + computed indicators
        sentiment: Current sentiment score (-1.0 to 1.0)
        scaler: Fitted StandardScaler from training

    Returns:
        Scaled feature array ready for model.predict()
    """
    latest = df.iloc[-1]

    features = np.array([[
        latest["Open"],
        latest["High"],
        latest["Low"],
        latest["Close"],
        latest["Volume"],
        latest["SMA_5"],
        latest["SMA_10"],
        latest["EMA_12"],
        latest["RSI_14"],
        latest["MACD"],
        latest["MACD_Signal"],
        sentiment,
    ]])

    # Replace any NaN/inf with 0
    features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

    # Scale using the training scaler
    features_scaled = scaler.transform(features)

    return features_scaled

"""
Train the stock price prediction model (RandomForestRegressor).

Pipeline:
  1. Load historical CSVs
  2. Feature engineering (SMA, EMA, RSI, MACD)
  3. Add sentiment placeholder
  4. Train/test split
  5. Train RandomForestRegressor
  6. Evaluate & save model
"""
import os
import sys
import warnings
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.utils.logger import setup_logger

logger = setup_logger("train_model")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "historical")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


# ── Feature Engineering ────────────────────────────────────

def compute_sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window).mean()


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD and Signal line."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add all technical indicators to a dataframe."""
    df = df.copy()

    # Moving Averages
    df["SMA_5"] = compute_sma(df["Close"], 5)
    df["SMA_10"] = compute_sma(df["Close"], 10)
    df["EMA_12"] = compute_ema(df["Close"], 12)

    # RSI
    df["RSI_14"] = compute_rsi(df["Close"], 14)

    # MACD
    df["MACD"], df["MACD_Signal"] = compute_macd(df["Close"])

    # Sentiment placeholder
    df["Sentiment"] = 0.0

    # Target: next day's close price
    df["Target"] = df["Close"].shift(-1)

    # Drop rows with NaN (from rolling windows + shift)
    df.dropna(inplace=True)

    return df


# ── Training ───────────────────────────────────────────────

def load_all_data() -> pd.DataFrame:
    """Load and combine all ticker CSVs."""
    all_dfs = []

    if not os.path.exists(DATA_DIR):
        logger.error(f"Data directory not found: {DATA_DIR}")
        logger.error("Run download_data.py first!")
        sys.exit(1)

    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if not csv_files:
        logger.error("No CSV files found. Run download_data.py first!")
        sys.exit(1)

    for filename in csv_files:
        ticker = filename.replace(".csv", "")
        filepath = os.path.join(DATA_DIR, filename)

        logger.info(f"Loading {ticker}...")
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        df["Ticker"] = ticker
        all_dfs.append(df)

    combined = pd.concat(all_dfs, ignore_index=True)
    logger.info(f"Loaded {len(combined)} total rows from {len(csv_files)} tickers")
    return combined


def train_model():
    """Main training pipeline."""
    logger.info("=" * 60)
    logger.info("PHASE 1: MODEL TRAINING")
    logger.info("=" * 60)

    # Step 1: Load data
    logger.info("\n📥 Step 1: Loading data...")
    raw_data = load_all_data()

    # Step 2: Feature engineering (per ticker)
    logger.info("\n🔧 Step 2: Feature engineering...")
    processed_dfs = []
    for ticker in raw_data["Ticker"].unique():
        ticker_df = raw_data[raw_data["Ticker"] == ticker].copy()
        ticker_df = ticker_df.sort_index()
        featured = add_features(ticker_df)
        processed_dfs.append(featured)
        logger.info(f"  {ticker}: {len(featured)} rows after feature engineering")

    data = pd.concat(processed_dfs, ignore_index=True)
    logger.info(f"  Total: {len(data)} training samples")

    # Step 3: Prepare features and target
    logger.info("\n📊 Step 3: Preparing features...")
    feature_cols = [
        "Open", "High", "Low", "Close", "Volume",
        "SMA_5", "SMA_10", "EMA_12",
        "RSI_14", "MACD", "MACD_Signal",
        "Sentiment",
    ]

    X = data[feature_cols].values
    y = data["Target"].values

    logger.info(f"  Feature matrix: {X.shape}")
    logger.info(f"  Features: {feature_cols}")

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Step 4: Train/test split
    logger.info("\n✂️ Step 4: Train/test split (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    logger.info(f"  Train: {len(X_train)} | Test: {len(X_test)}")

    # Step 5: Train model
    logger.info("\n🤖 Step 5: Training RandomForestRegressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    logger.info("  ✓ Model trained successfully")

    # Step 6: Evaluate
    logger.info("\n📈 Step 6: Evaluation...")
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    logger.info(f"  MAE:  ${mae:.2f}")
    logger.info(f"  RMSE: ${rmse:.2f}")
    logger.info(f"  R²:   {r2:.4f}")

    # Feature importance
    logger.info("\n🔍 Feature Importance:")
    importances = sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )
    for feat, imp in importances:
        bar = "█" * int(imp * 50)
        logger.info(f"  {feat:15s} {imp:.4f} {bar}")

    # Step 7: Save model and scaler
    logger.info("\n💾 Step 7: Saving model...")
    os.makedirs(MODELS_DIR, exist_ok=True)

    model_path = os.path.join(MODELS_DIR, "model.pkl")
    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    logger.info(f"  ✓ Model saved: {model_path}")
    logger.info(f"  ✓ Scaler saved: {scaler_path}")

    logger.info("\n" + "=" * 60)
    logger.info("✅ TRAINING COMPLETE")
    logger.info("=" * 60)

    return model, scaler


if __name__ == "__main__":
    train_model()

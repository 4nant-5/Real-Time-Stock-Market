"""
Configuration for the AntiGravity Stock Analytics pipeline.
Reads API keys from environment variables for security.
"""
import os
from dotenv import load_dotenv

load_dotenv()


# ── Stock Tickers ──────────────────────────────────────────
TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# ── API Keys ───────────────────────────────────────────────
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# ── Model ──────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "scaler.pkl")

# ── Pipeline Settings ──────────────────────────────────────
PREDICTION_INTERVAL_SECONDS = 5   # How often to refresh predictions
WEBSOCKET_PUSH_INTERVAL = 2       # How often to push to frontend (seconds)
HISTORY_WINDOW = 60               # Number of price history points to keep
SENTIMENT_HEADLINES_COUNT = 10    # Number of headlines for sentiment

# ── Feature columns (must match training order exactly) ────
FEATURE_COLUMNS = [
    "Open", "High", "Low", "Close", "Volume",
    "SMA_5", "SMA_10", "EMA_12",
    "RSI_14", "MACD", "MACD_Signal",
    "Sentiment",
]

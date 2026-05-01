"""
Live pipeline — orchestrates fetch → compute → predict → cache loop.
"""
import asyncio
from datetime import datetime
from collections import defaultdict
from app.config import TICKERS, PREDICTION_INTERVAL_SECONDS, HISTORY_WINDOW
from app.services.stock_service import fetch_live_data, get_current_price
from app.services.sentiment_service import get_sentiment_index
from app.services.feature_engine import compute_all_features, prepare_prediction_input
from app.models.predictor import predictor
from app.utils.logger import setup_logger

logger = setup_logger("pipeline")


class LivePipeline:
    def __init__(self):
        self.cache = {}
        self.price_history = defaultdict(list)
        self.prediction_history = defaultdict(list)
        self.sentiment_history = defaultdict(list)
        self._running = False

    async def start(self):
        logger.info("Starting live pipeline...")
        if not predictor.load():
            logger.error("Cannot start pipeline — model not loaded")
            return
        self._running = True
        logger.info(f"Pipeline running for: {TICKERS}")
        while self._running:
            try:
                await self._run_cycle()
            except Exception as e:
                logger.error(f"Pipeline cycle error: {e}", exc_info=True)
            await asyncio.sleep(PREDICTION_INTERVAL_SECONDS)

    def stop(self):
        self._running = False

    async def _run_cycle(self):
        for ticker in TICKERS:
            try:
                result = await asyncio.to_thread(self._process_ticker, ticker)
                if result:
                    self.cache[ticker] = result
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")

    def _process_ticker(self, ticker):
        timestamp = datetime.now().isoformat()
        price_info = get_current_price(ticker)
        current_price = price_info["price"]
        if current_price <= 0:
            return None

        hist_data = fetch_live_data(ticker, period="1mo", interval="1d")
        if hist_data.empty:
            return None

        featured_data = compute_all_features(hist_data)
        sentiment_data = get_sentiment_index(ticker)
        sentiment_score = sentiment_data["score"]

        features = prepare_prediction_input(featured_data, sentiment_score, predictor.scaler)
        predicted_price = predictor.predict(features)
        confidence = predictor.get_confidence(features)
        signal = predictor.generate_signal(predicted_price, current_price)
        change_pct = ((predicted_price - current_price) / current_price * 100) if current_price > 0 else 0

        self.price_history[ticker].append({"time": timestamp, "value": current_price})
        self.prediction_history[ticker].append({"time": timestamp, "value": round(predicted_price, 2)})
        self.sentiment_history[ticker].append({"time": timestamp, "value": round(sentiment_score, 4)})
        for h in [self.price_history, self.prediction_history, self.sentiment_history]:
            if len(h[ticker]) > HISTORY_WINDOW * 2:
                h[ticker] = h[ticker][-HISTORY_WINDOW:]

        indicators = {}
        if not featured_data.empty:
            row = featured_data.iloc[-1]
            indicators = {
                "sma_5": round(float(row.get("SMA_5", 0)), 2),
                "sma_10": round(float(row.get("SMA_10", 0)), 2),
                "ema_12": round(float(row.get("EMA_12", 0)), 2),
                "rsi": round(float(row.get("RSI_14", 0)), 2),
                "macd": round(float(row.get("MACD", 0)), 4),
                "macd_signal": round(float(row.get("MACD_Signal", 0)), 4),
            }

        result = {
            "ticker": ticker,
            "timestamp": timestamp,
            "current_price": current_price,
            "open": price_info["open"],
            "high": price_info["high"],
            "low": price_info["low"],
            "volume": price_info["volume"],
            "change": price_info["change"],
            "change_pct": price_info["change_pct"],
            "indicators": indicators,
            "sentiment": {
                "score": sentiment_data["score"],
                "label": sentiment_data["label"],
                "headline_count": sentiment_data["headline_count"],
                "headlines": sentiment_data.get("headlines", []),
            },
            "prediction": {
                "predicted_price": round(predicted_price, 2),
                "change_pct": round(change_pct, 2),
                "confidence": confidence,
            },
            "signal": signal,
            "price_history": self.price_history[ticker][-HISTORY_WINDOW:],
            "prediction_history": self.prediction_history[ticker][-HISTORY_WINDOW:],
            "sentiment_history": self.sentiment_history[ticker][-HISTORY_WINDOW:],
        }

        logger.info(f"{ticker}: ${current_price} → ${predicted_price:.2f} ({change_pct:+.2f}%) | {signal}")
        return result

    def get_cached(self, ticker):
        return self.cache.get(ticker)

    def get_all_cached(self):
        return dict(self.cache)


pipeline = LivePipeline()

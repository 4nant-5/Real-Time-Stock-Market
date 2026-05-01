"""
Sentiment analysis service — fetches news headlines and computes sentiment scores.
Uses NewsAPI for headlines and VADER for sentiment scoring.
"""
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from app.config import NEWSAPI_KEY, SENTIMENT_HEADLINES_COUNT
from app.utils.logger import setup_logger

logger = setup_logger("sentiment_service")

# Initialize VADER analyzer (singleton)
_analyzer = SentimentIntensityAnalyzer()

# Ticker → company name mapping for better news search
TICKER_NAMES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google Alphabet",
    "TSLA": "Tesla",
    "AMZN": "Amazon",
}


def fetch_news(ticker: str, count: int = SENTIMENT_HEADLINES_COUNT) -> list[dict]:
    """
    Fetch recent news headlines for a stock ticker from NewsAPI.

    Args:
        ticker: Stock symbol
        count: Number of headlines to fetch

    Returns:
        List of dicts with 'title', 'source', 'publishedAt'
    """
    if not NEWSAPI_KEY:
        logger.warning("No NewsAPI key set — using mock sentiment data")
        return _mock_headlines(ticker)

    query = TICKER_NAMES.get(ticker, ticker)

    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": "739944a26fac4696b9b64aba4eaec974",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": count,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        headlines = []
        for article in articles[:count]:
            headlines.append({
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "publishedAt": article.get("publishedAt", ""),
            })

        logger.info(f"Fetched {len(headlines)} headlines for {ticker}")
        return headlines

    except requests.exceptions.RequestException as e:
        logger.error(f"NewsAPI request failed for {ticker}: {e}")
        return _mock_headlines(ticker)


def compute_sentiment(headline: str) -> float:
    """
    Compute sentiment score for a single headline using VADER.

    Returns:
        Compound score from -1.0 (very negative) to +1.0 (very positive)
    """
    scores = _analyzer.polarity_scores(headline)
    return scores["compound"]


def get_sentiment_index(ticker: str) -> dict:
    """
    Compute aggregate sentiment index for a ticker.

    Returns dict with:
        - score: mean compound score of recent headlines
        - label: 'Positive', 'Negative', or 'Neutral'
        - headline_count: number of headlines analyzed
        - headlines: list of {title, sentiment} dicts
    """
    headlines = fetch_news(ticker)

    if not headlines:
        return {
            "score": 0.0,
            "label": "Neutral",
            "headline_count": 0,
            "headlines": [],
        }

    scored_headlines = []
    scores = []

    for h in headlines:
        title = h.get("title", "")
        if not title or title == "[Removed]":
            continue

        score = compute_sentiment(title)
        scores.append(score)
        scored_headlines.append({
            "title": title,
            "source": h.get("source", ""),
            "sentiment": round(score, 3),
        })

    if not scores:
        avg_score = 0.0
    else:
        avg_score = sum(scores) / len(scores)

    # Classify
    if avg_score > 0.05:
        label = "Positive"
    elif avg_score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "score": round(avg_score, 4),
        "label": label,
        "headline_count": len(scored_headlines),
        "headlines": scored_headlines[:5],  # Send top 5 to frontend
    }


def _mock_headlines(ticker: str) -> list[dict]:
    """Generate mock headlines when NewsAPI is unavailable."""
    company = TICKER_NAMES.get(ticker, ticker)
    return [
        {"title": f"{company} stock shows strong momentum in today's trading", "source": "Mock", "publishedAt": ""},
        {"title": f"{company} reports better-than-expected quarterly earnings", "source": "Mock", "publishedAt": ""},
        {"title": f"Analysts upgrade {company} price target amid growth outlook", "source": "Mock", "publishedAt": ""},
        {"title": f"{company} faces regulatory challenges in key markets", "source": "Mock", "publishedAt": ""},
        {"title": f"Market volatility impacts {company} shares in early trading", "source": "Mock", "publishedAt": ""},
        {"title": f"{company} announces new product line expansion strategy", "source": "Mock", "publishedAt": ""},
        {"title": f"Investors bullish on {company} after recent innovations", "source": "Mock", "publishedAt": ""},
        {"title": f"{company} CEO discusses future growth plans at conference", "source": "Mock", "publishedAt": ""},
        {"title": f"Competition heats up as {company} enters new sector", "source": "Mock", "publishedAt": ""},
        {"title": f"{company} maintains market leadership position despite headwinds", "source": "Mock", "publishedAt": ""},
    ]

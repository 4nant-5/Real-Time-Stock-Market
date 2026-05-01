"""
FastAPI backend — REST API + WebSocket for real-time stock analytics.
"""
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import TICKERS, WEBSOCKET_PUSH_INTERVAL
from app.services.pipeline import pipeline
from app.utils.logger import setup_logger

logger = setup_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the pipeline on app startup, stop on shutdown."""
    logger.info("🚀 Starting AntiGravity Stock Analytics...")
    pipeline_task = asyncio.create_task(pipeline.start())
    yield
    logger.info("Shutting down pipeline...")
    pipeline.stop()
    pipeline_task.cancel()


app = FastAPI(
    title="AntiGravity Stock Analytics",
    description="Real-time stock predictions with ML + sentiment analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REST Endpoints ──────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "AntiGravity Stock Analytics"}


@app.get("/api/stocks")
async def list_stocks():
    return {"tickers": TICKERS}


@app.get("/api/stock/{ticker}")
async def get_stock(ticker: str):
    ticker = ticker.upper()
    if ticker not in TICKERS:
        return {"error": f"Ticker {ticker} not tracked. Available: {TICKERS}"}
    data = pipeline.get_cached(ticker)
    if not data:
        return {"error": f"No data yet for {ticker}. Pipeline is initializing..."}
    return data


@app.get("/api/all")
async def get_all_stocks():
    return pipeline.get_all_cached()


# ── WebSocket ───────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ws: WebSocket, ticker: str):
        await ws.accept()
        if ticker not in self.connections:
            self.connections[ticker] = []
        self.connections[ticker].append(ws)
        logger.info(f"WebSocket connected: {ticker} (total: {len(self.connections[ticker])})")

    def disconnect(self, ws: WebSocket, ticker: str):
        if ticker in self.connections:
            self.connections[ticker] = [c for c in self.connections[ticker] if c != ws]
            logger.info(f"WebSocket disconnected: {ticker}")

    async def broadcast(self, ticker: str, data: dict):
        if ticker not in self.connections:
            return
        dead = []
        for ws in self.connections[ticker]:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.connections[ticker].remove(ws)


manager = ConnectionManager()


@app.websocket("/ws/{ticker}")
async def websocket_endpoint(ws: WebSocket, ticker: str):
    ticker = ticker.upper()
    await manager.connect(ws, ticker)
    try:
        while True:
            data = pipeline.get_cached(ticker)
            if data:
                await ws.send_json(data)
            await asyncio.sleep(WEBSOCKET_PUSH_INTERVAL)
    except WebSocketDisconnect:
        manager.disconnect(ws, ticker)
    except Exception as e:
        logger.error(f"WebSocket error ({ticker}): {e}")
        manager.disconnect(ws, ticker)


@app.websocket("/ws")
async def websocket_all(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = pipeline.get_all_cached()
            if data:
                await ws.send_json(data)
            await asyncio.sleep(WEBSOCKET_PUSH_INTERVAL)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error (all): {e}")

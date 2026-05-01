import React, { useState } from 'react';
import { Header } from './components/Header';
import { StockSelector } from './components/StockSelector';
import { LivePriceCard } from './components/LivePriceCard';
import { PredictionCard } from './components/PredictionCard';
import { SentimentGauge } from './components/SentimentGauge';
import { SignalBadge } from './components/SignalBadge';
import { PriceChart } from './components/PriceChart';
import { SentimentChart } from './components/SentimentChart';
import { useWebSocket } from './hooks/useWebSocket';
import './index.css';

const TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"];
const WS_URL = "ws://localhost:8000/ws";

function App() {
  const [selectedTicker, setSelectedTicker] = useState(TICKERS[0]);
  const { data, connected, error } = useWebSocket(WS_URL, selectedTicker);

  return (
    <div className="dashboard-grid">
      <Header 
        connected={connected} 
        lastUpdated={data?.timestamp} 
      />
      
      <StockSelector 
        tickers={TICKERS} 
        selectedTicker={selectedTicker} 
        onSelect={setSelectedTicker} 
      />

      {error ? (
        <div className="glass-card col-span-12" style={{ textAlign: 'center', padding: '40px', color: 'var(--signal-sell)' }}>
          <h2>Connection Error</h2>
          <p>{error}</p>
          <p style={{ color: 'var(--text-muted)', marginTop: '16px' }}>Make sure the FastAPI backend is running on port 8000</p>
        </div>
      ) : !data ? (
        <div className="glass-card col-span-12" style={{ textAlign: 'center', padding: '60px' }}>
          <div className="animate-pulse" style={{ width: '40px', height: '40px', border: '3px solid var(--accent-cyan)', borderTopColor: 'transparent', borderRadius: '50%', margin: '0 auto 20px', animation: 'spin 1s linear infinite' }}></div>
          <h2>Initializing Pipeline...</h2>
          <p style={{ color: 'var(--text-muted)' }}>Fetching live data and running ML models for {selectedTicker}</p>
          <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
        </div>
      ) : (
        <>
          <div className="col-span-3">
            <LivePriceCard 
              price={data.current_price} 
              change={data.change} 
              changePct={data.change_pct} 
              volume={data.volume} 
            />
          </div>
          
          <div className="col-span-3">
            <PredictionCard 
              prediction={data.prediction} 
              currentPrice={data.current_price} 
            />
          </div>
          
          <div className="col-span-3">
            <SentimentGauge sentiment={data.sentiment} />
          </div>
          
          <div className="col-span-3">
            <SignalBadge signal={data.signal} />
          </div>

          <PriceChart 
            history={data.price_history} 
            prediction={data.prediction} 
          />
          
          <SentimentChart history={data.sentiment_history} />
          
          {/* Headlines Card */}
          <div className="glass-card col-span-12">
            <h3 style={{ color: 'var(--text-muted)', fontSize: '1rem', fontWeight: 500, marginBottom: '16px' }}>
              Recent Headlines
            </h3>
            <div style={{ display: 'grid', gap: '12px' }}>
              {data.sentiment?.headlines?.map((h, i) => (
                <div key={i} style={{ 
                  padding: '12px 16px', 
                  background: 'rgba(255,255,255,0.03)', 
                  borderRadius: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <div style={{ fontWeight: 500, marginBottom: '4px' }}>{h.title}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{h.source}</div>
                  </div>
                  <div style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '0.8rem', 
                    fontWeight: 600,
                    background: h.sentiment > 0.05 ? 'rgba(16, 185, 129, 0.2)' : h.sentiment < -0.05 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                    color: h.sentiment > 0.05 ? 'var(--signal-buy)' : h.sentiment < -0.05 ? 'var(--signal-sell)' : 'var(--text-main)'
                  }}>
                    {h.sentiment > 0.05 ? 'Bullish' : h.sentiment < -0.05 ? 'Bearish' : 'Neutral'}
                  </div>
                </div>
              ))}
              {!data.sentiment?.headlines?.length && (
                <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No recent headlines found.</div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;

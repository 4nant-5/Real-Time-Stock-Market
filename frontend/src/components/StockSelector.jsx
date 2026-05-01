import React from 'react';

export function StockSelector({ tickers, selectedTicker, onSelect }) {
  return (
    <div className="glass-card col-span-12" style={{ padding: '12px 24px' }}>
      <div style={{ display: 'flex', gap: '16px', overflowX: 'auto' }}>
        {tickers.map(ticker => (
          <button
            key={ticker}
            onClick={() => onSelect(ticker)}
            style={{
              padding: '8px 24px',
              borderRadius: '8px',
              border: `1px solid ${selectedTicker === ticker ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
              background: selectedTicker === ticker ? 'rgba(0, 212, 255, 0.1)' : 'transparent',
              color: selectedTicker === ticker ? 'var(--text-main)' : 'var(--text-muted)',
              cursor: 'pointer',
              fontWeight: 600,
              transition: 'all 0.2s ease',
              outline: 'none'
            }}
          >
            {ticker}
          </button>
        ))}
      </div>
    </div>
  );
}

import React from 'react';
import { Activity, TrendingUp, TrendingDown, Clock } from 'lucide-react';

export function Header({ connected, lastUpdated }) {
  return (
    <header className="glass-card col-span-12" style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      padding: '16px 32px' 
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Activity size={28} color="var(--accent-cyan)" />
        <h1 className="text-gradient" style={{ fontSize: '1.5rem', fontWeight: 700 }}>
          TradeSage
        </h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
          <Clock size={16} />
          <span style={{ fontSize: '0.9rem' }}>
            {lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : 'Waiting for data...'}
          </span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ 
            width: '10px', 
            height: '10px', 
            borderRadius: '50%', 
            backgroundColor: connected ? 'var(--signal-buy)' : 'var(--signal-sell)',
            boxShadow: `0 0 10px ${connected ? 'var(--signal-buy)' : 'var(--signal-sell)'}`
          }} className={connected ? "animate-pulse" : ""} />
          <span style={{ fontSize: '0.9rem', color: connected ? 'var(--text-main)' : 'var(--text-muted)' }}>
            {connected ? 'Live Data' : 'Disconnected'}
          </span>
        </div>
      </div>
    </header>
  );
}

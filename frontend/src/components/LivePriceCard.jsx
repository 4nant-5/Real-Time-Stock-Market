import React from 'react';
import { DollarSign, TrendingUp, TrendingDown } from 'lucide-react';

export function LivePriceCard({ price, change, changePct, volume }) {
  const isPositive = change >= 0;
  const colorVar = isPositive ? 'var(--signal-buy)' : 'var(--signal-sell)';
  const Icon = isPositive ? TrendingUp : TrendingDown;

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <h3 style={{ color: 'var(--text-muted)', fontSize: '1rem', fontWeight: 500 }}>Live Price</h3>
        <DollarSign size={20} color="var(--accent-blue)" />
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '8px' }}>
        <span style={{ fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-1px' }}>
          ${price?.toFixed(2) || '0.00'}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '4px',
          color: colorVar,
          background: `${colorVar}20`,
          padding: '4px 8px',
          borderRadius: '6px',
          fontSize: '0.9rem',
          fontWeight: 600
        }}>
          <Icon size={16} />
          {isPositive ? '+' : ''}{change?.toFixed(2)} ({isPositive ? '+' : ''}{changePct?.toFixed(2)}%)
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Vol: {(volume / 1000000).toFixed(2)}M
        </div>
      </div>
    </div>
  );
}

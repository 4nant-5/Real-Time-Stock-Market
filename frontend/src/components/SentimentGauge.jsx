import React from 'react';
import { MessageSquareText } from 'lucide-react';

export function SentimentGauge({ sentiment }) {
  const score = sentiment?.score || 0; // -1 to +1
  const label = sentiment?.label || 'Neutral';
  const count = sentiment?.headline_count || 0;
  
  // Convert -1 to +1 into 0 to 180 degrees for the gauge
  const rotation = (score + 1) * 90; 
  
  let color = 'var(--text-main)';
  if (score > 0.1) color = 'var(--signal-buy)';
  else if (score < -0.1) color = 'var(--signal-sell)';
  else color = 'var(--signal-hold)';

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <h3 style={{ color: 'var(--text-muted)', fontSize: '1rem', fontWeight: 500 }}>News Sentiment</h3>
        <MessageSquareText size={20} color="var(--accent-cyan)" />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '24px 0' }}>
        {/* Semi-circle Gauge */}
        <div style={{ position: 'relative', width: '160px', height: '80px', overflow: 'hidden' }}>
          {/* Track */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '160px',
            height: '160px',
            borderRadius: '50%',
            border: '12px solid rgba(255,255,255,0.1)',
            borderBottomColor: 'transparent',
            borderLeftColor: 'transparent',
            transform: 'rotate(-45deg)'
          }} />
          
          {/* Fill */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '160px',
            height: '160px',
            borderRadius: '50%',
            border: `12px solid ${color}`,
            borderBottomColor: 'transparent',
            borderLeftColor: 'transparent',
            transform: `rotate(${rotation - 225}deg)`,
            transition: 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }} />
          
          {/* Needle Center */}
          <div style={{
            position: 'absolute',
            bottom: '-6px',
            left: 'calc(50% - 6px)',
            width: '12px',
            height: '12px',
            backgroundColor: 'var(--text-main)',
            borderRadius: '50%'
          }} />
        </div>
        
        <div style={{ marginTop: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '1.25rem', fontWeight: 600, color: color }}>{label}</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Score: {score.toFixed(2)}
          </div>
        </div>
      </div>

      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center' }}>
        Based on {count} recent headlines
      </div>
    </div>
  );
}

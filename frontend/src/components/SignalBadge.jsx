import React from 'react';
import { AlertCircle } from 'lucide-react';

export function SignalBadge({ signal }) {
  const currentSignal = signal || 'HOLD';
  
  let bgColor, textColor, glowColor;
  
  switch(currentSignal) {
    case 'BUY':
      bgColor = 'rgba(16, 185, 129, 0.2)';
      textColor = 'var(--signal-buy)';
      glowColor = 'rgba(16, 185, 129, 0.4)';
      break;
    case 'SELL':
      bgColor = 'rgba(239, 68, 68, 0.2)';
      textColor = 'var(--signal-sell)';
      glowColor = 'rgba(239, 68, 68, 0.4)';
      break;
    default:
      bgColor = 'rgba(245, 158, 11, 0.2)';
      textColor = 'var(--signal-hold)';
      glowColor = 'rgba(245, 158, 11, 0.4)';
  }

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <h3 style={{ color: 'var(--text-muted)', fontSize: '1rem', fontWeight: 500 }}>Trading Signal</h3>
        <AlertCircle size={20} color="var(--accent-cyan)" />
      </div>

      <div style={{ 
        flex: 1, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '20px 0'
      }}>
        <div style={{
          background: bgColor,
          color: textColor,
          padding: '16px 48px',
          borderRadius: '12px',
          fontSize: '2rem',
          fontWeight: 800,
          letterSpacing: '2px',
          boxShadow: `0 0 30px ${glowColor}`,
          border: `1px solid ${glowColor}`,
          textShadow: `0 0 10px ${glowColor}`
        }}>
          {currentSignal}
        </div>
      </div>
    </div>
  );
}

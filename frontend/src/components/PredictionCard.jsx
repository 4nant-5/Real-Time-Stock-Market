import React from 'react';
import { Target, Zap } from 'lucide-react';

export function PredictionCard({ prediction, currentPrice }) {
  const predictedPrice = prediction?.predicted_price || 0;
  const confidence = prediction?.confidence || 0;
  
  const isUp = predictedPrice > currentPrice;
  const colorVar = isUp ? 'var(--signal-buy)' : 'var(--signal-sell)';
  
  return (
    <div className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Background glow based on prediction */}
      <div style={{
        position: 'absolute',
        top: '-50%',
        right: '-10%',
        width: '200px',
        height: '200px',
        background: `radial-gradient(circle, ${colorVar}20 0%, transparent 70%)`,
        borderRadius: '50%',
        pointerEvents: 'none'
      }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <h3 style={{ color: 'var(--text-muted)', fontSize: '1rem', fontWeight: 500 }}>ML Prediction</h3>
        <Target size={20} color="var(--accent-cyan)" />
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '8px' }}>
        <span style={{ fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-1px', color: 'var(--text-main)' }}>
          ${predictedPrice.toFixed(2)}
        </span>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Target (Next Period)
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Zap size={14} color="var(--accent-cyan)" />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>
            {(confidence * 100).toFixed(0)}% Confidence
          </span>
        </div>
      </div>
      
      {/* Confidence Bar */}
      <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '16px', overflow: 'hidden' }}>
        <div style={{ 
          width: `${confidence * 100}%`, 
          height: '100%', 
          background: 'linear-gradient(90deg, var(--accent-blue), var(--accent-cyan))',
          borderRadius: '2px',
          transition: 'width 0.5s ease-out'
        }} />
      </div>
    </div>
  );
}

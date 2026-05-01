import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function SentimentChart({ history }) {
  const data = history?.map(item => ({
    time: new Date(item.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    score: item.value,
  })) || [];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const val = payload[0].value;
      const color = val > 0 ? 'var(--signal-buy)' : val < 0 ? 'var(--signal-sell)' : 'var(--text-main)';
      
      return (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          padding: '12px',
          borderRadius: '8px',
          backdropFilter: 'blur(8px)'
        }}>
          <p style={{ margin: '0 0 4px 0', color: 'var(--text-muted)' }}>{label}</p>
          <p style={{ color, margin: 0, fontWeight: 600 }}>
            Score: {val.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  // Gradient definitions for positive/negative areas
  const gradientOffset = () => {
    const dataMax = Math.max(...data.map(i => i.score));
    const dataMin = Math.min(...data.map(i => i.score));

    if (dataMax <= 0) return 0;
    if (dataMin >= 0) return 1;
    return dataMax / (dataMax - dataMin);
  };

  const off = gradientOffset();

  return (
    <div className="glass-card col-span-4" style={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ color: 'var(--text-muted)', fontSize: '1rem', fontWeight: 500, marginBottom: '16px' }}>
        Sentiment Trend
      </h3>
      
      <div style={{ flex: 1, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <defs>
              <linearGradient id="splitColor" x1="0" y1="0" x2="0" y2="1">
                <stop offset={off} stopColor="var(--signal-buy)" stopOpacity={0.5} />
                <stop offset={off} stopColor="var(--signal-sell)" stopOpacity={0.5} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis 
              dataKey="time" 
              stroke="var(--text-muted)" 
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              domain={[-1, 1]} 
              stroke="var(--text-muted)" 
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area 
              type="monotone" 
              dataKey="score" 
              stroke="var(--text-main)" 
              fill="url(#splitColor)" 
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

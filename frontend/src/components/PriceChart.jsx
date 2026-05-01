import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export function PriceChart({ history, prediction }) {
  // Format data for chart
  const data = history?.map(item => ({
    time: new Date(item.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    price: item.value,
  })) || [];

  // Add prediction point if available
  if (prediction && data.length > 0) {
    const lastItem = data[data.length - 1];
    data.push({
      time: 'Prediction',
      price: lastItem.price,
      predicted: prediction.predicted_price
    });
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          padding: '12px',
          borderRadius: '8px',
          backdropFilter: 'blur(8px)'
        }}>
          <p style={{ margin: '0 0 8px 0', color: 'var(--text-muted)' }}>{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color, margin: 0, fontWeight: 600 }}>
              {entry.name}: ${entry.value.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-card col-span-8" style={{ height: '400px', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ color: 'var(--text-muted)', fontSize: '1rem', fontWeight: 500, marginBottom: '16px' }}>
        Price History & ML Forecast
      </h3>
      
      <div style={{ flex: 1, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis 
              dataKey="time" 
              stroke="var(--text-muted)" 
              tick={{ fill: 'var(--text-muted)' }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              domain={['auto', 'auto']} 
              stroke="var(--text-muted)" 
              tick={{ fill: 'var(--text-muted)' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            
            <Line 
              type="monotone" 
              dataKey="price" 
              name="Actual Price"
              stroke="var(--accent-blue)" 
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 6, fill: 'var(--accent-blue)', stroke: 'var(--bg-dark)' }}
            />
            <Line 
              type="monotone" 
              dataKey="predicted" 
              name="Predicted"
              stroke="var(--accent-cyan)" 
              strokeWidth={3}
              strokeDasharray="5 5"
              dot={{ r: 4, fill: 'var(--accent-cyan)' }}
              activeDot={{ r: 6, fill: 'var(--accent-cyan)' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

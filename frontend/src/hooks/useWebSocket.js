import { useState, useEffect, useRef } from 'react';

export function useWebSocket(url, ticker) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    let isMounted = true;
    
    const connect = () => {
      try {
        const wsUrl = ticker ? `${url}/${ticker}` : url;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          if (isMounted) {
            setConnected(true);
            setError(null);
          }
        };

        ws.onmessage = (event) => {
          if (isMounted) {
            const parsedData = JSON.parse(event.data);
            setData(parsedData);
          }
        };

        ws.onerror = (e) => {
          if (isMounted) {
            console.error('WebSocket error:', e);
            setError('Connection error');
          }
        };

        ws.onclose = () => {
          if (isMounted) {
            setConnected(false);
            // Attempt to reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(connect, 3000);
          }
        };
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url, ticker]);

  return { data, connected, error };
}

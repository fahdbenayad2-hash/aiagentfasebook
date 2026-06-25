import { useEffect, useRef, useState } from 'react';
import { getToken } from './useAuth';

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function useWebSocket(convId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!convId) return;

    const token = getToken();
    const ws = new WebSocket(`${WS_BASE}/ws/conversations/${convId}?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        setMessages(prev => [...prev, msg]);
      } catch { /* ignore */ }
    };

    ws.onclose = () => {
      wsRef.current = null;
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [convId]);

  return { messages, setMessages };
}

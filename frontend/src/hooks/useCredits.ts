import { useState, useEffect, useCallback } from 'react';
import client from '../api/client';
import { getUser, setUser } from './useAuth';

export default function useCredits() {
  const [credits, setCredits] = useState(() => {
    try { return getUser()?.credits ?? 0; } catch { return 0; }
  });

  const refresh = useCallback(async () => {
    try {
      const { data } = await client.get('/api/auth/me');
      setCredits(data.credits);
      setUser(data);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  return { credits, refresh };
}

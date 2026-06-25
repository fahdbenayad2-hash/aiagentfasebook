import { useState, useEffect } from 'react';
import client from '../api/client';
import { getUser, setUser } from './useAuth';

export default function useCredits() {
  const [credits, setCredits] = useState(getUser()?.credits ?? 0);

  const refresh = async () => {
    try {
      const { data } = await client.get('/api/auth/me');
      setCredits(data.credits);
      setUser(data);
    } catch { /* ignore */ }
  };

  useEffect(() => { refresh(); }, []);

  return { credits, refresh };
}

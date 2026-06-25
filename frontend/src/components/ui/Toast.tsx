import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertCircle, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info';

interface ToastData { id: number; type: ToastType; message: string; }

let toastId = 0;
const listeners: Set<(t: ToastData) => void> = new Set();

export function showToast(type: ToastType, message: string) {
  const t: ToastData = { id: ++toastId, type, message };
  listeners.forEach(fn => fn(t));
}

const icons: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle size={18} />,
  error: <XCircle size={18} />,
  info: <AlertCircle size={18} />,
};

const colors: Record<ToastType, { bg: string; border: string; icon: string }> = {
  success: { bg: 'rgba(34,197,94,0.1)', border: 'rgba(34,197,94,0.2)', icon: 'var(--success)' },
  error: { bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)', icon: 'var(--danger)' },
  info: { bg: 'rgba(232,168,48,0.1)', border: 'rgba(232,168,48,0.2)', icon: 'var(--gold)' },
};

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  useEffect(() => {
    const handler = (t: ToastData) => setToasts(prev => [...prev, t]);
    listeners.add(handler);
    return () => { listeners.delete(handler); };
  }, []);

  const remove = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <div style={{ position: 'fixed', bottom: 24, left: 24, zIndex: 2000, display: 'flex', flexDirection: 'column', gap: 8 }}>
      <AnimatePresence>
        {toasts.map(t => (
          <ToastItem key={t.id} toast={t} onRemove={remove} />
        ))}
      </AnimatePresence>
    </div>
  );
}

function ToastItem({ toast, onRemove }: { toast: ToastData; onRemove: (id: number) => void }) {
  useEffect(() => { const t = setTimeout(() => onRemove(toast.id), 4000); return () => clearTimeout(t); }, [toast.id, onRemove]);
  const c = colors[toast.type];

  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }} animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }} transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: c.bg, border: `1px solid ${c.border}`, borderRadius: 12,
        padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 10,
        minWidth: 280, maxWidth: 400, backdropFilter: 'blur(12px)',
        boxShadow: '0 8px 24px rgba(0,0,0,0.3)',
      }}
    >
      <span style={{ color: c.icon, display: 'flex' }}>{icons[toast.type]}</span>
      <span style={{ flex: 1, fontSize: '.85rem', color: 'var(--text)' }}>{toast.message}</span>
      <button onClick={() => onRemove(toast.id)} style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', padding: 2 }}>
        <X size={14} />
      </button>
    </motion.div>
  );
}

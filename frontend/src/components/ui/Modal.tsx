import { ReactNode, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { modalBackdrop, modalContent } from '../../animations/variants';

interface Props {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  maxWidth?: number;
}

export default function Modal({ open, onClose, title, children, maxWidth = 520 }: Props) {
  useEffect(() => {
    if (open) { document.body.style.overflow = 'hidden'; }
    else { document.body.style.overflow = ''; }
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          variants={modalBackdrop} initial="hidden" animate="visible" exit="exit"
          onClick={onClose}
          style={{
            position: 'fixed', inset: 0, zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
            padding: '1rem',
          }}
        >
          <motion.div
            variants={modalContent} initial="hidden" animate="visible" exit="exit"
            onClick={e => e.stopPropagation()}
            style={{
              background: 'var(--bg2)', border: '1px solid var(--border)',
              borderRadius: 16, padding: '1.75rem', width: '100%',
              maxWidth, maxHeight: '85vh', overflowY: 'auto',
              boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
            }}
          >
            {title && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '1.05rem' }}>{title}</h3>
                <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', padding: 4, borderRadius: 6, transition: 'all .2s' }}>
                  <X size={18} />
                </button>
              </div>
            )}
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

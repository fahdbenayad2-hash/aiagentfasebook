import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X } from 'lucide-react';
import Button from '../ui/Button';

const LINKS = [
  { id: 'features', label: 'المميزات' },
  { id: 'how', label: 'كيفاش تخدم' },
  { id: 'pricing', label: 'الأسعار' },
  { id: 'faq', label: 'الأسئلة' },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <motion.nav className="landing-nav"
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        position: 'fixed', top: 0, right: 0, left: 0, zIndex: 100,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '.75rem 4rem',
        background: scrolled ? 'rgba(7,8,13,0.85)' : 'transparent',
        backdropFilter: scrolled ? 'blur(20px)' : 'none',
        borderBottom: scrolled ? '1px solid var(--border)' : '1px solid transparent',
        transition: 'all .3s',
      }}
    >
      <a href="/" style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.4rem', fontWeight: 900, color: 'var(--text)', letterSpacing: '-.01em' }}>
        فهد <span style={{ color: 'var(--gold)' }}>✦</span>
      </a>

      <div className="nav-links" style={{ display: 'flex', alignItems: 'center', gap: '.5rem' }}>
        {LINKS.map(link => (
          <a
            key={link.id}
            href={`#${link.id}`}
            style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '.88rem', fontFamily: "'Cairo',sans-serif", padding: '.45rem .9rem', borderRadius: 6, transition: 'color .2s' }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--text)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--muted)'}
          >
            {link.label}
          </a>
        ))}
      </div>

      <div className="nav-links" style={{ display: 'flex', gap: '.6rem', alignItems: 'center' }}>
        <a href="/auth" style={{ color: 'var(--muted)', fontSize: '.85rem', fontFamily: "'Cairo',sans-serif", fontWeight: 600, transition: 'color .2s' }}
          onMouseEnter={e => e.currentTarget.style.color = 'var(--text)'}
          onMouseLeave={e => e.currentTarget.style.color = 'var(--muted)'}
        >تسجيل الدخول</a>
        <a href="/auth?signup=1">
          <Button size="sm">ابدأ تجربتك</Button>
        </a>
      </div>

      <button className="mobile-menu-btn" onClick={() => setMobileOpen(!mobileOpen)} style={{ display: 'none', background: 'none', border: 'none', color: 'var(--text)', cursor: 'pointer', padding: 4 }}>
        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            style={{ position: 'fixed', top: 60, right: 0, left: 0, background: 'var(--bg2)', borderBottom: '1px solid var(--border)', padding: '1rem', zIndex: 99, display: 'flex', flexDirection: 'column', gap: 8 }}>
            {LINKS.map(link => (
              <a key={link.id} href={`#${link.id}`} onClick={() => setMobileOpen(false)}
                style={{ padding: '.6rem .8rem', borderRadius: 8, color: 'var(--muted)', fontSize: '.88rem', fontFamily: "'Cairo',sans-serif" }}>
                {link.label}
              </a>
            ))}
            <a href="/auth" style={{ padding: '.6rem .8rem', borderRadius: 8, color: 'var(--muted)', fontSize: '.88rem' }}>تسجيل الدخول</a>
            <a href="/auth?signup=1" style={{ padding: '.6rem .8rem', borderRadius: 8, background: 'var(--gold)', color: 'var(--bg)', fontWeight: 700, textAlign: 'center' }}>ابدأ تجربتك</a>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

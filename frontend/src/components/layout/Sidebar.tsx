import { NavLink } from 'react-router-dom';
import useCredits from '../../hooks/useCredits';

const LINKS = [
  { to: '/dashboard', icon: '🏠', label: 'الرئيسية', exact: true },
  { to: '/dashboard/conversations', icon: '💬', label: 'المحادثات' },
  { to: '/dashboard/orders', icon: '📦', label: 'الطلبات' },
  { to: '/dashboard/products', icon: '🛍️', label: 'المنتجات' },
  { to: '/dashboard/customers', icon: '👥', label: 'العملاء' },
  { to: '/dashboard/connected-accounts', icon: '🔗', label: 'الحسابات المتصلة' },
  { to: '/dashboard/settings', icon: '⚙️', label: 'الإعدادات' },
];

export default function Sidebar() {
  const { credits } = useCredits();

  return (
    <aside
      id="sidebar"
      style={{
        width: 240,
        background: 'var(--bg2)',
        borderLeft: '1px solid var(--border)',
        height: '100vh',
        position: 'fixed',
        right: 0,
        top: 0,
        display: 'flex',
        flexDirection: 'column',
        zIndex: 50,
      }}
    >
      <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border)' }}>
        <a href="/" style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.4rem', fontWeight: 900, color: 'var(--text)', letterSpacing: '-.01em' }}>
          MARIA <span style={{ color: 'var(--gold)' }}>✦</span>
        </a>
      </div>

      <nav style={{ padding: '1rem .75rem', flex: 1 }}>
        {LINKS.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.exact}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '.65rem',
              padding: '.7rem 1rem',
              borderRadius: 8,
              fontSize: '.9rem',
              fontWeight: 600,
              color: isActive ? 'var(--gold)' : 'var(--muted)',
              background: isActive ? 'var(--gold-d)' : 'transparent',
              border: isActive ? '1px solid var(--b-gold)' : '1px solid transparent',
              marginBottom: 4,
              transition: 'all .2s',
              fontFamily: "'Cairo',sans-serif",
            })}
          >
            {link.icon} {link.label}
          </NavLink>
        ))}
      </nav>

      <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: '.78rem', color: 'var(--muted)', marginBottom: 6 }}>نقاطي</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ flex: 1, height: 6, background: 'var(--bg3)', borderRadius: 3 }}>
            <div style={{ width: '70%', height: '100%', background: 'var(--gold)', borderRadius: 3 }} />
          </div>
          <span style={{ fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.85rem', color: 'var(--gold)' }}>{credits.toLocaleString()}</span>
        </div>
      </div>
    </aside>
  );
}

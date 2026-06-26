import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, ShoppingCart, Package, BarChart3, Coins, Settings, ChevronRight } from 'lucide-react';
import useCredits from '../../hooks/useCredits';
import { useState } from 'react';

const LINKS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'الرئيسية', exact: true },
  { to: '/dashboard/conversations', icon: MessageSquare, label: 'المحادثات' },
  { to: '/dashboard/orders', icon: ShoppingCart, label: 'الطلبات' },
  { to: '/dashboard/products', icon: Package, label: 'المنتجات' },
  { to: '/dashboard/analytics', icon: BarChart3, label: 'الإحصائيات' },
  { to: '/dashboard/credits', icon: Coins, label: 'الرصيد' },
  { to: '/dashboard/settings', icon: Settings, label: 'الإعدادات' },
];

export default function Sidebar() {
  const { credits } = useCredits();
  const [collapsed, setCollapsed] = useState(false);
  const w = collapsed ? 72 : 260;

  return (
    <aside className="sidebar" style={{
      width: w, background: 'var(--bg2)', borderLeft: '1px solid var(--border)',
      height: '100vh', position: 'fixed', right: 0, top: 0,
      display: 'flex', flexDirection: 'column', zIndex: 50,
      transition: 'width .3s',
    }}>
      <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {!collapsed && (
          <a href="/" style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.3rem', fontWeight: 900, color: 'var(--text)', letterSpacing: '-.01em' }}>
            فهد <span style={{ color: 'var(--gold)' }}>✦</span>
          </a>
        )}
        <button onClick={() => setCollapsed(!collapsed)}
          style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', padding: 4, borderRadius: 6, transition: 'all .2s', transform: collapsed ? 'rotate(180deg)' : '' }}
        >
          <ChevronRight size={16} />
        </button>
      </div>

      <nav style={{ padding: '1rem .75rem', flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {LINKS.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.exact}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: '.75rem',
              padding: collapsed ? '.7rem 0' : '.7rem 1rem',
              justifyContent: collapsed ? 'center' : 'flex-start',
              borderRadius: 8, fontSize: '.86rem', fontWeight: 600,
              color: isActive ? 'var(--gold)' : 'var(--muted)',
              background: isActive ? 'rgba(232,168,48,.1)' : 'transparent',
              borderRight: isActive ? '2px solid var(--gold)' : '2px solid transparent',
              transition: 'all .2s',
              fontFamily: "'Cairo',sans-serif",
            })}
          >
            <link.icon size={18} />
            {!collapsed && link.label}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border)' }}>
          <div style={{ fontSize: '.78rem', color: 'var(--muted)', marginBottom: 6 }}>الرصيد</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ flex: 1, height: 6, background: 'var(--bg3)', borderRadius: 3 }}>
              <div style={{ width: `${Math.min((credits / 100000) * 100, 100)}%`, height: '100%', background: 'var(--gold)', borderRadius: 3 }} />
            </div>
            <span style={{ fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.85rem', color: 'var(--gold)' }}>{credits.toLocaleString()}</span>
          </div>
          <a href="/dashboard/credits" style={{ display: 'block', textAlign: 'center', marginTop: 8, fontSize: '.75rem', color: 'var(--gold)', fontFamily: "'Cairo',sans-serif", fontWeight: 600 }}>شحن ←</a>
        </div>
      )}
    </aside>
  );
}

import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Bell, LogOut } from 'lucide-react';
import { useState } from 'react';

const PATH_NAMES: Record<string, string> = {
  '': 'الرئيسية',
  conversations: 'المحادثات',
  orders: 'الطلبات',
  products: 'المنتجات',
  analytics: 'الإحصائيات',
  credits: 'الرصيد',
  settings: 'الإعدادات',
};

export default function TopBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const segment = location.pathname.split('/').filter(Boolean).pop() || '';
  const pageName = PATH_NAMES[segment] || 'الرئيسية';

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/auth');
  };

  return (
    <header style={{
      background: 'rgba(7,8,13,0.8)', backdropFilter: 'blur(20px)',
      borderBottom: '1px solid var(--border)',
      padding: '.75rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      position: 'sticky', top: 0, zIndex: 40,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', fontFamily: "'Cairo',sans-serif", fontSize: '.88rem', color: 'var(--gold)', fontWeight: 600 }}>
        لوحة التحكم / <span style={{ color: 'var(--text)' }}>{pageName}</span>
      </div>

      <div style={{ flex: 1, maxWidth: 320, margin: '0 2rem', position: 'relative' }}>
        <Search size={15} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }} />
        <input placeholder="بحث..."
          style={{
            width: '100%', padding: '8px 36px 8px 12px', borderRadius: 8,
            border: '1px solid var(--border)', background: 'var(--bg3)', color: 'var(--text)',
            fontSize: '.82rem', outline: 'none', transition: 'all .22s',
          }}
          onFocus={e => e.currentTarget.style.borderColor = 'var(--b-gold)'}
          onBlur={e => e.currentTarget.style.borderColor = 'var(--border)'}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '.75rem' }}>
        <button style={{ position: 'relative', background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', padding: 6, borderRadius: 8, transition: 'all .2s' }}>
          <Bell size={18} />
          <span style={{ position: 'absolute', top: 2, left: 2, width: 8, height: 8, borderRadius: '50%', background: 'var(--danger)' }} />
        </button>
        <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--gold-d)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.78rem', color: 'var(--gold)', cursor: 'pointer' }}>
          ف
        </div>
        <button onClick={handleLogout} style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', padding: 6, borderRadius: 8, transition: 'all .2s', fontSize: '.78rem', fontWeight: 600, fontFamily: "'Cairo',sans-serif", display: 'flex', alignItems: 'center', gap: 4 }}>
          <LogOut size={14} /> خروج
        </button>
      </div>
    </header>
  );
}

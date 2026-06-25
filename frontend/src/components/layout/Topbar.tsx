import { getUser, clearToken } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

export default function Topbar({ pageTitle }: { pageTitle?: string }) {
  const nav = useNavigate();
  const user = getUser();

  const logout = () => {
    clearToken();
    nav('/auth');
  };

  return (
    <header
      style={{
        height: 60,
        background: 'var(--bg2)',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 1.75rem',
      }}
    >
      <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{pageTitle || 'لوحة التحكم'}</h2>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{ fontSize: '.85rem', color: 'var(--muted)' }}>{user?.name || 'مستخدم'}</span>
        <button
          onClick={logout}
          style={{
            background: 'transparent',
            border: '1px solid var(--border)',
            borderRadius: 6,
            padding: '.35rem .85rem',
            color: 'var(--danger)',
            fontSize: '.8rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          تسجيل خروج
        </button>
      </div>
    </header>
  );
}

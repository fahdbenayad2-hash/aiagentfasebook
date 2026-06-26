import { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

export default function DashboardLayout() {
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/auth', { replace: true });
    } else {
      setChecking(false);
    }
  }, [navigate]);

  if (checking) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)' }}>
        <div style={{ width: 32, height: 32, border: '3px solid var(--gold)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin .6s linear infinite' }} />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
        <main className="dashboard-main" style={{ flex: 1, marginRight: 260, display: 'flex', flexDirection: 'column' }}>
        <TopBar />
        <div className="dashboard-content" style={{ flex: 1, padding: '1.5rem', background: 'var(--bg)' }}>
          <Outlet />
        </div>
      </main>
      <Sidebar />
    </div>
  );
}

import { useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { isAuthenticated } from '../../hooks/useAuth';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import GeoBg from '../shared/GeoBg';

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'الرئيسية',
  '/dashboard/conversations': 'المحادثات',
  '/dashboard/orders': 'الطلبات',
  '/dashboard/settings': 'الإعدادات',
};

export default function DashboardLayout() {
  const nav = useNavigate();
  const loc = useLocation();

  useEffect(() => {
    if (!isAuthenticated()) {
      nav('/auth', { replace: true });
    }
  }, [nav]);

  if (!isAuthenticated()) return null;

  const title = PAGE_TITLES[loc.pathname] || 'لوحة التحكم';

  return (
    <GeoBg style={{ minHeight: '100vh', paddingRight: 240 }}>
      <Sidebar />
      <div style={{ marginRight: 0 }}>
        <Topbar pageTitle={title} />
        <main style={{ padding: '1.75rem' }}>
          <Outlet />
        </main>
      </div>
    </GeoBg>
  );
}

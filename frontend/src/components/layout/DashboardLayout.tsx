import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import ToastContainer from '../ui/Toast';

export default function DashboardLayout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <ToastContainer />
      <main style={{ flex: 1, marginRight: 260, display: 'flex', flexDirection: 'column' }}>
        <TopBar />
        <div style={{ flex: 1, padding: '1.5rem', background: 'var(--bg)' }}>
          <Outlet />
        </div>
      </main>
      <Sidebar />
    </div>
  );
}

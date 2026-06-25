import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './pages/Auth';
import DashboardLayout from './components/layout/DashboardLayout';
import DashboardHome from './pages/Dashboard/Home';
import Conversations from './pages/Dashboard/Conversations';
import Orders from './pages/Dashboard/Orders';
import Products from './pages/Dashboard/Products';
import Customers from './pages/Dashboard/Customers';
import ConnectedAccounts from './pages/Dashboard/ConnectedAccounts';
import Settings from './pages/Dashboard/Settings';
import Demo from './pages/Demo';

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/demo" element={<Demo />} />
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<DashboardHome />} />
          <Route path="conversations" element={<Conversations />} />
          <Route path="orders" element={<Orders />} />
          <Route path="products" element={<Products />} />
          <Route path="customers" element={<Customers />} />
          <Route path="connected-accounts" element={<ConnectedAccounts />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/auth" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

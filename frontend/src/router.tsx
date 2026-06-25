import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';

const AuthPage = lazy(() => import('./pages/Auth'));
const LandingPage = lazy(() => import('./pages/Landing/LandingPage'));
const DashboardLayout = lazy(() => import('./components/layout/DashboardLayout'));
const DashboardHome = lazy(() => import('./pages/Dashboard/Home'));
const Conversations = lazy(() => import('./pages/Dashboard/Conversations'));
const Orders = lazy(() => import('./pages/Dashboard/Orders'));
const Products = lazy(() => import('./pages/Dashboard/Products'));
const Customers = lazy(() => import('./pages/Dashboard/Customers'));
const ConnectedAccounts = lazy(() => import('./pages/Dashboard/ConnectedAccounts'));
const Analytics = lazy(() => import('./pages/Dashboard/Analytics'));
const Credits = lazy(() => import('./pages/Dashboard/Credits'));
const Settings = lazy(() => import('./pages/Dashboard/Settings'));
const Demo = lazy(() => import('./pages/Demo'));

function Loader() {
  return (
    <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)' }}>
      <div style={{ width: 32, height: 32, border: '3px solid var(--gold)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin .6s linear infinite' }} />
    </div>
  );
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<Loader />}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<DashboardHome />} />
            <Route path="conversations" element={<Conversations />} />
            <Route path="orders" element={<Orders />} />
            <Route path="products" element={<Products />} />
            <Route path="customers" element={<Customers />} />
            <Route path="connected-accounts" element={<ConnectedAccounts />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="credits" element={<Credits />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

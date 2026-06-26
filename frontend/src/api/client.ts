import axios from 'axios';
import { showToast } from '../components/ui/Toast';

const BASE_URL = import.meta.env.VITE_API_URL || '';

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail;
    const msg = Array.isArray(detail) ? detail.map((d: any) => d.msg || d.message || '').filter(Boolean).join('; ') : (detail || err.message || 'حدث خطأ');
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (!window.location.pathname.startsWith('/auth')) {
        showToast('error', 'انتهت الجلسة. سجل دخول مرة أخرى');
        setTimeout(() => { window.location.href = '/auth'; }, 1000);
      }
    } else if (err.response?.status !== 404) {
      showToast('error', msg);
    }
    return Promise.reject(err);
  },
);

export default client;

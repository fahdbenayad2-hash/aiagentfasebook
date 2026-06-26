import { useState, useEffect } from 'react';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Skeleton from '../../components/ui/Skeleton';

interface Customer {
  id: number;
  name: string;
  phone: string;
  state: string;
  platform: string;
  created_at: string;
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pages: number;
}

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const limit = 20;

  useEffect(() => {
    setPage(1);
  }, [search]);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (search) params.set('search', search);
    client.get(`/api/customers?${params}`, { signal: controller.signal })
      .then(r => {
        const res: PaginatedResponse<Customer> = r.data;
        setCustomers(res.data);
        setTotal(res.total);
        setPages(res.pages);
      })
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Customers]:', err); })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [page, search]);

  const from = (page - 1) * limit + 1;
  const to = Math.min(page * limit, total);

  return (
    <div>
      <h3 style={{ fontSize: '1rem', marginBottom: 16 }}>العملاء ({total})</h3>
      <input
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="بحث باسم العميل..."
        style={{
          width: 300, padding: '10px 14px', borderRadius: 8, border: '1px solid var(--border)',
          background: 'var(--bg3)', color: 'var(--text)', fontSize: '.85rem', outline: 'none',
          marginBottom: 16,
        }}
      />
      <Card style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 24 }}><Skeleton width="100%" height={200} borderRadius={8} /></div>
        ) : (<>
        <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.82rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              {['#', 'الاسم', 'الهاتف', 'الولاية', 'المنصة', 'تاريخ التسجيل'].map(h => (
                <th key={h} style={{ padding: '12px 14px', textAlign: 'right', color: 'var(--muted)', fontWeight: 700, fontSize: '.75rem' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {customers.map(c => (
              <tr key={c.id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '12px 14px', color: 'var(--gold)', fontWeight: 700 }}><span className="num">{c.id}</span></td>
                <td style={{ padding: '12px 14px' }}>{c.name}</td>
                <td style={{ padding: '12px 14px', direction: 'ltr' }}>{c.phone}</td>
                <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{c.state}</td>
                <td style={{ padding: '12px 14px' }}>{c.platform === 'facebook' ? '📘' : '📸'} {c.platform}</td>
                <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{c.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!customers.length && !loading && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted)' }}>ماكاش عملاء</div>}
        </div>
        </>)}
      </Card>

      {pages > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 16, fontSize: '.85rem', color: 'var(--muted)' }}>
          <span>عرض <span className="num">{from}</span>-<span className="num">{to}</span> من <span className="num">{total}</span> عميل</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← السابق</Button>
            <Button size="sm" variant="outline" disabled={page >= pages} onClick={() => setPage(p => p + 1)}>التالي →</Button>
          </div>
        </div>
      )}
    </div>
  );
}
import { useState, useEffect } from 'react';
import client from '../../api/client';
import Card from '../../components/ui/Card';

export default function Customers() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    client.get(`/api/customers${params}`).then(r => setCustomers(r.data)).catch(() => {});
  }, [search]);

  return (
    <div>
      <h3 style={{ fontSize: '1rem', marginBottom: 16 }}>العملاء ({customers.length})</h3>
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
                <td style={{ padding: '12px 14px', color: 'var(--gold)', fontWeight: 700 }}>{c.id}</td>
                <td style={{ padding: '12px 14px' }}>{c.name}</td>
                <td style={{ padding: '12px 14px', direction: 'ltr' }}>{c.phone}</td>
                <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{c.state}</td>
                <td style={{ padding: '12px 14px' }}>{c.platform === 'facebook' ? '📘' : '📸'} {c.platform}</td>
                <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{c.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!customers.length && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted)' }}>ماكاش عملاء</div>}
      </Card>
    </div>
  );
}

import { useState, useEffect, FormEvent } from 'react';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function Products() {
  const [products, setProducts] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    client.get('/api/products').then(r => setProducts(r.data)).catch(() => {});
  }, []);

  const toggleProduct = async (id: number, active: boolean) => {
    try {
      await client.patch(`/api/products/${id}`, { available: active });
      setProducts(prev => prev.map(p => p.id === id ? { ...p, active } : p));
    } catch {}
  };

  const handleUpload = async (e: FormEvent<HTMLInputElement>) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append('file', file);
    try {
      const { data } = await client.post('/api/products/upload', form);
      setProducts(prev => [...prev, ...data]);
    } catch {}
    setUploading(false);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3 style={{ fontSize: '1rem' }}>المنتجات ({products.length})</h3>
        <label style={{ cursor: 'pointer' }}>
          <input type="file" accept=".csv,.json" onChange={handleUpload} style={{ display: 'none' }} />
          <Button variant="outline" size="sm" loading={uploading}>رفع كتالوغ</Button>
        </label>
      </div>
      <Card style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.82rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              {['المنتج', 'السعر', 'المخزون', 'الألوان', 'المقاسات', 'متوفر'].map(h => (
                <th key={h} style={{ padding: '12px 14px', textAlign: 'right', color: 'var(--muted)', fontWeight: 700, fontSize: '.75rem' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {products.map(p => (
              <tr key={p.id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '12px 14px' }}>{p.name}</td>
                <td style={{ padding: '12px 14px', fontFamily: "'Cairo',sans-serif", fontWeight: 700 }}>{p.price.toLocaleString()} دج</td>
                <td style={{ padding: '12px 14px' }}>{p.stock}</td>
                <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{(p.colors || []).join(', ')}</td>
                <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{(p.sizes || []).join(', ')}</td>
                <td style={{ padding: '12px 14px' }}>
                  <button
                    onClick={() => toggleProduct(p.id, !p.active)}
                    style={{
                      width: 44, height: 22, borderRadius: 11, border: 'none', cursor: 'pointer',
                      background: p.active ? 'var(--success)' : 'var(--faint)',
                      position: 'relative', transition: 'background .2s',
                    }}
                  >
                    <div style={{
                      width: 16, height: 16, borderRadius: '50%', background: '#fff',
                      position: 'absolute', top: 3, right: p.active ? 3 : 25,
                      transition: 'right .2s',
                    }} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!products.length && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted)' }}>ماكاش منتجات. ارفع كتالوغ باش تبدا.</div>}
      </Card>
    </div>
  );
}

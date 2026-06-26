import { useState, useEffect, FormEvent } from 'react';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Skeleton from '../../components/ui/Skeleton';

interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  active: boolean;
  colors?: string[];
  sizes?: string[];
}

const emptyForm = () => ({ name: '', price: '', stock: '', category: '', description: '', colors: '', sizes: '' });

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [uploading, setUploading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm());
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    client.get('/api/products', { signal: controller.signal })
      .then(r => setProducts(r.data))
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Products]:', err); })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, []);

  const toggleProduct = async (id: number, active: boolean) => {
    try {
      await client.patch(`/api/products/${id}`, { available: active });
      setProducts(prev => prev.map(p => p.id === id ? { ...p, active } : p));
    } catch (err: any) { console.error('[Products toggle]:', err); }
  };

  const handleUpload = async (e: FormEvent<HTMLInputElement>) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const { data } = await client.post('/api/products/upload', fd);
      setProducts(prev => [...prev, ...data]);
    } catch (err: any) { console.error('[Products upload]:', err); }
    setUploading(false);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.price) return;
    setSaving(true);
    try {
      const { data } = await client.post('/api/products', {
        ...form,
        price: Number(form.price),
        stock: Number(form.stock) || 0,
      });
      setProducts(prev => [...prev, { id: data.id, name: data.name, price: Number(form.price), stock: Number(form.stock) || 0, colors: form.colors ? form.colors.split(',').map(c => c.trim()) : [], sizes: form.sizes ? form.sizes.split(',').map(s => s.trim()) : [], active: true }]);
      setShowForm(false);
      setForm(emptyForm());
    } catch (err: any) { console.error('[Products save]:', err); }
    setSaving(false);
  };

  const col = (label: string, val: string, key: string) => (
    <div style={{ marginBottom: 12 }}>
      <label style={{ display: 'block', fontSize: '.78rem', color: 'var(--muted)', marginBottom: 4 }}>{label}</label>
      <input value={val} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))} style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg3)', color: 'var(--text)', fontSize: '.85rem', outline: 'none' }} />
    </div>
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3 style={{ fontSize: '1rem' }}>المنتجات ({products.length})</h3>
        <div style={{ display: 'flex', gap: 8 }}>
          <label style={{ cursor: 'pointer' }}>
            <input type="file" accept=".csv,.json" onChange={handleUpload} style={{ display: 'none' }} />
            <Button variant="outline" size="sm" loading={uploading}>رفع كتالوغ</Button>
          </label>
          <Button size="sm" onClick={() => setShowForm(true)}>+ إضافة منتج</Button>
        </div>
      </div>

      {showForm && (
        <Card style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <h4 style={{ fontSize: '.9rem' }}>إضافة منتج جديد</h4>
            <button onClick={() => setShowForm(false)} style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', fontSize: '1.2rem' }}>✕</button>
          </div>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {col('الاسم *', form.name, 'name')}
              {col('السعر (دج) *', form.price, 'price')}
              {col('المخزون', form.stock, 'stock')}
              {col('التصنيف', form.category, 'category')}
              {col('الألوان (مفصولة بفاصلة)', form.colors, 'colors')}
              {col('المقاسات (مفصولة بفاصلة)', form.sizes, 'sizes')}
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', fontSize: '.78rem', color: 'var(--muted)', marginBottom: 4 }}>الوصف</label>
              <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={3} style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg3)', color: 'var(--text)', fontSize: '.85rem', outline: 'none', resize: 'vertical' }} />
            </div>
            <Button type="submit" loading={saving}>حفظ المنتج</Button>
          </form>
        </Card>
      )}

      <Card style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 24 }}><Skeleton width="100%" height={200} borderRadius={8} /></div>
        ) : (<>
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
                <td style={{ padding: '12px 14px', fontFamily: "'Cairo',sans-serif", fontWeight: 700 }}><span className="num">{p.price.toLocaleString()}</span> دج</td>
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
        {!products.length && !loading && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted)' }}>ماكاش منتجات. ارفع كتالوغ أو ضغط "إضافة منتج" باش تبدا.</div>}
        </>)}
      </Card>
    </div>
  );
}

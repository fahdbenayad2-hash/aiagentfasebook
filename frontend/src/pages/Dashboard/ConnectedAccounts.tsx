import { useState, useEffect } from 'react';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

interface ConnectedPage {
  name: string;
  id: string;
  token_preview: string;
  is_active: boolean;
}

export default function ConnectedAccounts() {
  const [pages, setPages] = useState<ConnectedPage[]>([]);

  useEffect(() => {
    const controller = new AbortController();
    client.get('/api/facebook/connections', { signal: controller.signal })
      .then(r => setPages(r.data?.connections || []))
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[ConnectedAccounts]:', err); });
    return () => controller.abort();
  }, []);

  return (
    <div>
      <h3 style={{ fontSize: '1rem', marginBottom: 16 }}>الحسابات المتصلة</h3>

      <Card style={{ marginBottom: 20 }}>
        <p style={{ color: 'var(--muted)', marginBottom: 16, fontSize: '.85rem' }}>
          اربط صفحة فيسبوك باش ماريا تستقبل الرسائل وترد عليهم تلقائياً.
        </p>
        <a href="/admin/facebook/connect" target="_blank" rel="noopener noreferrer">
          <Button>➕ ربط صفحة جديدة</Button>
        </a>
      </Card>

      {pages.map(p => (
        <Card key={p.id} style={{ marginBottom: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 44, height: 44, borderRadius: '50%',
              background: 'var(--gold-d)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: "'Cairo',sans-serif", fontWeight: 700,
              fontSize: '1rem', color: 'var(--gold)',
            }}>
              {(p.name || '?')[0]}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700 }}>{p.name}</div>
              <div style={{ fontSize: '.78rem', color: 'var(--muted)', direction: 'ltr' }}>ID: {p.id}</div>
              <div style={{ fontSize: '.75rem', color: 'var(--faint)' }}>التوكن: {p.token_preview}</div>
            </div>
            <div style={{
              padding: '4px 12px', borderRadius: 100,
              background: p.is_active ? 'var(--success)' : 'var(--faint)',
              color: p.is_active ? '#fff' : 'var(--muted)',
              fontSize: '.75rem', fontWeight: 600,
            }}>
              {p.is_active ? 'نشط' : 'غير نشط'}
            </div>
          </div>
        </Card>
      ))}

      {!pages.length && (
        <Card>
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--muted)' }}>
            ماكاش صفحات متصلة. ضغط "ربط صفحة جديدة" باش تبدأ.
          </div>
        </Card>
      )}
    </div>
  );
}

import { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import { clearToken } from '../../hooks/useAuth';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Modal from '../../components/ui/Modal';

interface SettingsProduct {
  id: number;
  name: string;
  price: number;
  sizes?: string[];
  active?: boolean;
}

export default function Settings() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<'page' | 'products' | 'notifications' | 'account'>('page');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [connectedPage, setConnectedPage] = useState<{ name: string; id: string } | null>(null);
  const [products, setProducts] = useState<SettingsProduct[]>([]);
  const [notifPhone, setNotifPhone] = useState('');
  const [notifNewOrder, setNotifNewOrder] = useState(true);
  const [notifHandoff, setNotifHandoff] = useState(true);
  const [telegramChatId, setTelegramChatId] = useState('');
  const [testingTelegram, setTestingTelegram] = useState(false);
  const [testResult, setTestResult] = useState<'ok' | 'fail' | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    client.get('/api/facebook/connections', { signal: controller.signal })
      .then(r => {
        const pages = r.data?.connections || r.data || [];
        if (pages.length) setConnectedPage(pages[0]);
      })
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Settings fb]:', err); });

    client.get('/api/products', { signal: controller.signal })
      .then(r => setProducts(r.data))
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Settings prods]:', err); });

    client.get('/api/settings/notifications', { signal: controller.signal })
      .then(r => {
        setNotifPhone(r.data.phone || '');
        setNotifNewOrder(r.data.new_order ?? true);
        setNotifHandoff(r.data.handoff ?? true);
        setTelegramChatId(r.data.telegram_chat_id || '');
      })
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Settings notif]:', err); });
    return () => controller.abort();
  }, []);

  const handleProductToggle = async (id: number, available: boolean) => {
    try {
      await client.patch(`/api/products/${id}`, { available });
      setProducts(prev => prev.map(p => p.id === id ? { ...p, active: available } : p));
    } catch (err: any) { console.error('[Settings toggle]:', err); }
  };

  const handleCSVUpload = async (e: FormEvent<HTMLInputElement>) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append('file', file);
    try {
      const { data } = await client.post('/api/products/upload', form);
      setProducts(prev => [...prev, ...data]);
    } catch (err: any) { console.error('[Settings upload]:', err); }
  };

  const saveNotifications = async () => {
    try {
      await client.put('/api/settings/notifications', {
        phone: notifPhone,
        new_order: notifNewOrder,
        handoff: notifHandoff,
        telegram_chat_id: telegramChatId,
      });
    } catch (err: any) { console.error('[Settings save]:', err); }
  };

  const testTelegram = async () => {
    setTestingTelegram(true);
    setTestResult(null);
    try {
      await client.put('/api/settings/notifications', {
        phone: notifPhone,
        new_order: notifNewOrder,
        handoff: notifHandoff,
        telegram_chat_id: telegramChatId,
      });
      const { data } = await client.post('/api/settings/notifications/test');
      setTestResult(data.success ? 'ok' : 'fail');
    } catch (err: any) {
      console.error('[Settings telegram]:', err);
      setTestResult('fail');
    }
    setTestingTelegram(false);
  };

  const deleteAccount = async () => {
    setDeleting(true);
    try {
      await client.delete('/api/auth/account', { data: { password: deletePassword } });
      clearToken();
      navigate('/auth');
    } catch (err: any) {
      console.error('[Settings delete]:', err);
      alert('كلمة المرور غير صحيحة');
    }
    setDeleting(false);
    setShowDeleteModal(false);
    setDeletePassword('');
  };

  const tabs = [
    { key: 'page', label: 'الصفحة' },
    { key: 'products', label: 'المنتجات' },
    { key: 'notifications', label: 'الإشعارات' },
    { key: 'account', label: 'الحساب' },
  ];

  return (
    <div>
      <div className="settings-tabs" style={{ display: 'flex', gap: 4, marginBottom: 24, borderBottom: '1px solid var(--border)', paddingBottom: 12 }}>
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key as typeof tab)}
            style={{
              padding: '.55rem 1.25rem',
              borderRadius: 6,
              border: 'none',
              background: tab === t.key ? 'var(--gold-d)' : 'transparent',
              color: tab === t.key ? 'var(--gold)' : 'var(--muted)',
              fontWeight: 700,
              fontSize: '.85rem',
              fontFamily: "'Cairo',sans-serif",
              cursor: 'pointer',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'page' && (
        <Card>
          <h3 style={{ marginBottom: 16 }}>ربط صفحة فيسبوك</h3>
          {connectedPage ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'var(--gold-d)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '1rem', color: 'var(--gold)' }}>
                  {(connectedPage.name || '?')[0]}
                </div>
                <div>
                  <div style={{ fontWeight: 700 }}>{connectedPage.name}</div>
                  <div style={{ fontSize: '.78rem', color: 'var(--muted)' }}>ID: {connectedPage.id}</div>
                </div>
              </div>
              <a href="/admin/facebook/connect" target="_blank">
                <Button variant="danger" size="sm">فصل الصفحة</Button>
              </a>
            </div>
          ) : (
            <div>
              <p style={{ color: 'var(--muted)', marginBottom: 16, fontSize: '.85rem' }}>ماكاش صفحة متصلة حالياً. اربط صفحتك باش ماريا تبدأ تستقبل الرسائل.</p>
              <a href="/admin/facebook/connect" target="_blank">
                <Button>ربط صفحة فيسبوك</Button>
              </a>
            </div>
          )}
        </Card>
      )}

      {tab === 'products' && (
        <div>
          <div style={{ marginBottom: 20 }}>
            <input
              type="file"
              accept=".csv,.json"
              onChange={handleCSVUpload}
              style={{ display: 'none' }}
              id="csv-upload"
            />
            <label htmlFor="csv-upload">
              <Button variant="outline">رفع كتالوغ (CSV/JSON)</Button>
            </label>
          </div>
          <Card style={{ padding: 0, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.82rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  {['اسم المنتج', 'السعر', 'المقاسات', 'متوفر'].map(h => (
                    <th key={h} style={{ padding: '12px 14px', textAlign: 'right', color: 'var(--muted)', fontWeight: 700, fontFamily: "'Cairo',sans-serif", fontSize: '.75rem' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {products.map(p => (
                  <tr key={p.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '12px 14px' }}>{p.name}</td>
                    <td style={{ padding: '12px 14px', fontFamily: "'Cairo',sans-serif", fontWeight: 700 }}>{p.price.toLocaleString()} دج</td>
                    <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{(p.sizes || []).join(', ')}</td>
                    <td style={{ padding: '12px 14px' }}>
                      <button
                        onClick={() => handleProductToggle(p.id, !p.active)}
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
      )}

      {tab === 'account' && (
        <Card style={{ border: '1px solid var(--danger)', background: 'rgba(220,78,78,0.04)' }}>
          <h3 style={{ marginBottom: 12, color: 'var(--danger)' }}>منطقة الخطر</h3>
          <p style={{ fontSize: '.85rem', color: 'var(--muted)', marginBottom: 16, lineHeight: 1.7 }}>
            حذف الحساب راح يمسح جميع بياناتك نهائياً. ما تقدرش ترجعهم بعد الحذف.
          </p>
          <Button variant="danger" onClick={() => setShowDeleteModal(true)}>حذف الحساب</Button>
        </Card>
      )}

      <Modal open={showDeleteModal} onClose={() => { setShowDeleteModal(false); setDeletePassword(''); }} title="تأكيد حذف الحساب">
        <p style={{ marginBottom: 16, color: 'var(--muted)', fontSize: '.9rem', lineHeight: 1.7 }}>
          هل أنت متأكد؟ هذا الإجراء نهائي ولا يمكن التراجع عنه. اكتب كلمة المرور لتأكيد الحذف.
        </p>
        <Input
          label="كلمة المرور"
          type="password"
          value={deletePassword}
          onChange={e => setDeletePassword(e.target.value)}
          placeholder="اكتب كلمة المرور"
        />
        <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
          <Button variant="danger" onClick={deleteAccount} loading={deleting}>تأكيد الحذف</Button>
          <Button variant="ghost" onClick={() => { setShowDeleteModal(false); setDeletePassword(''); }}>رجوع</Button>
        </div>
      </Modal>

      {tab === 'notifications' && (
        <Card>
          <h3 style={{ marginBottom: 16 }}>إعدادات الإشعارات</h3>
          <Input
            label="رقم واتساب للتنبيهات"
            value={notifPhone}
            onChange={e => setNotifPhone(e.target.value)}
            placeholder="05XX XXXXXX"
          />
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', marginBottom: 8 }}>
              <input type="checkbox" checked={notifNewOrder} onChange={e => setNotifNewOrder(e.target.checked)} style={{ accentColor: 'var(--gold)', width: 18, height: 18 }} />
              <span style={{ fontSize: '.85rem' }}>إشعار طلب جديد</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input type="checkbox" checked={notifHandoff} onChange={e => setNotifHandoff(e.target.checked)} style={{ accentColor: 'var(--gold)', width: 18, height: 18 }} />
              <span style={{ fontSize: '.85rem' }}>إشعار تحويل يدوي</span>
            </label>
          </div>
          <Button onClick={saveNotifications}>حفظ الإعدادات</Button>
          <div style={{ marginTop: 24, paddingTop: 20, borderTop: '1px solid var(--border)' }}>
            <h4 style={{ fontSize: '.9rem', marginBottom: 12 }}>إشعارات تلجرام</h4>
            <p style={{ fontSize: '.8rem', color: 'var(--muted)', marginBottom: 12, lineHeight: 1.6 }}>
              1. افتح البوت <a href="https://t.me/language_buddy_doudi_bot" target="_blank" style={{ color: 'var(--gold)' }}>@language_buddy_doudi_bot</a> و ابعتلـه <code>/start</code><br />
              2. افتح <a href="https://t.me/userinfobot" target="_blank" style={{ color: 'var(--gold)' }}>@userinfobot</a> و ابعتلـه <code>/start</code> — راح يردلك رقم شاتك<br />
              3. انسخ الرقم (مثلاً 123456789) و حطه تحت
            </p>
            <Input
              label="معرف شات تلجرام (Chat ID)"
              value={telegramChatId}
              onChange={e => setTelegramChatId(e.target.value)}
              placeholder="مثال: 123456789"
            />
            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <Button size="sm" onClick={testTelegram} loading={testingTelegram}>إرسال اختبار</Button>
              {testResult === 'ok' && <span style={{ color: 'var(--success)', fontSize: '.82rem', alignSelf: 'center' }}>✅ تم — تحقق من تلجرام</span>}
              {testResult === 'fail' && <span style={{ color: 'var(--danger)', fontSize: '.82rem', alignSelf: 'center' }}>❌ فشل — تحقق من الرقم و انك بدأت البوت</span>}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

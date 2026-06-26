import { useState, useEffect } from 'react';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/ui/Modal';
import Skeleton from '../../components/ui/Skeleton';

interface Order {
  id: number;
  customer: string;
  wilaya: string;
  product: string;
  size: string;
  total: number;
  status: string;
  date: string;
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pages: number;
}

const statusColors: Record<string, 'muted' | 'gold' | 'terra' | 'green'> = {
  'معلق': 'muted',
  'مؤكد': 'gold',
  'في التوصيل': 'terra',
  'مسلّم': 'green',
};

const WILAYAS = [
  '', 'أدرار', 'الشلف', 'الأغواط', 'أم البواقي', 'باتنة', 'بجاية', 'بسكرة', 'بشار',
  'البليدة', 'البويرة', 'تمنراست', 'تبسة', 'تلمسان', 'تيارت', 'تيزي وزو', 'الجزائر',
  'الجلفة', 'جيجل', 'سطيف', 'سعيدة', 'سكيكدة', 'سيدي بلعباس', 'عنابة', 'قالمة',
  'قسنطينة', 'المدية', 'مستغانم', 'المسيلة', 'معسكر', 'ورقلة', 'وهران', 'البيض',
  'إليزي', 'برج بوعريريج', 'بومرداس', 'الطارف', 'تندوف', 'تيسمسيلت', 'الوادي',
  'خنشلة', 'سوق أهراس', 'تيبازة', 'ميلة', 'عين الدفلى', 'النعامة', 'عين تموشنتة',
  'غرداية', 'غليزان',
];

export default function Orders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [wilayaFilter, setWilayaFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [cancelId, setCancelId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const limit = 20;

  useEffect(() => {
    setLoading(true);
    setPage(1);
  }, [wilayaFilter, statusFilter, dateFrom, dateTo]);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (wilayaFilter) params.set('wilaya', wilayaFilter);
    if (statusFilter) params.set('status', statusFilter);
    if (dateFrom) params.set('from', dateFrom);
    if (dateTo) params.set('to', dateTo);
    client.get(`/api/orders?${params}`, { signal: controller.signal })
      .then(r => {
        const res: PaginatedResponse<Order> = r.data;
        setOrders(res.data);
        setTotal(res.total);
        setPages(res.pages);
      })
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Orders]:', err); })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [page, wilayaFilter, statusFilter, dateFrom, dateTo]);

  const confirmOrder = async (id: number) => {
    try {
      await client.patch(`/api/orders/${id}`, { status: 'confirmed' });
      const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
      if (wilayaFilter) params.set('wilaya', wilayaFilter);
      if (statusFilter) params.set('status', statusFilter);
      const res = await client.get(`/api/orders?${params}`);
      const data: PaginatedResponse<Order> = res.data;
      setOrders(data.data);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err: any) { console.error('[Orders confirm]:', err); }
  };

  const cancelOrder = async () => {
    if (!cancelId) return;
    try {
      await client.patch(`/api/orders/${cancelId}`, { status: 'cancelled' });
      setCancelId(null);
      const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
      if (wilayaFilter) params.set('wilaya', wilayaFilter);
      if (statusFilter) params.set('status', statusFilter);
      const res = await client.get(`/api/orders?${params}`);
      const data: PaginatedResponse<Order> = res.data;
      setOrders(data.data);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err: any) { console.error('[Orders cancel]:', err); }
  };

  const exportCSV = () => {
    const rows = [['#', 'الزبون', 'الولاية', 'المنتج', 'المقاس', 'المجموع', 'الحالة', 'التاريخ'].join(',')];
    orders.forEach(o => rows.push([o.id, o.customer, o.wilaya, o.product, o.size, o.total, o.status, o.date].join(',')));
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'orders.csv';
    a.click();
  };

  const from = (page - 1) * limit + 1;
  const to = Math.min(page * limit, total);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3 style={{ fontSize: '1rem' }}>الطلبات ({total})</h3>
        <Button variant="outline" size="sm" onClick={exportCSV}>تصدير CSV</Button>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap', alignItems: 'end' }}>
        <div>
          <label style={{ display: 'block', fontSize: '.72rem', color: 'var(--muted)', marginBottom: 4 }}>الولاية</label>
          <select
            value={wilayaFilter}
            onChange={e => setWilayaFilter(e.target.value)}
            style={{ padding: '8px 12px', background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', fontSize: '.82rem' }}
          >
            <option value="">الكل</option>
            {WILAYAS.filter(Boolean).map(w => <option key={w} value={w}>{w}</option>)}
          </select>
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '.72rem', color: 'var(--muted)', marginBottom: 4 }}>الحالة</label>
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            style={{ padding: '8px 12px', background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', fontSize: '.82rem' }}
          >
            <option value="">الكل</option>
            <option value="معلق">معلق</option>
            <option value="مؤكد">مؤكد</option>
            <option value="في التوصيل">في التوصيل</option>
            <option value="مسلّم">مسلّم</option>
          </select>
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '.72rem', color: 'var(--muted)', marginBottom: 4 }}>من</label>
          <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} style={{ padding: '8px 12px', background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', fontSize: '.82rem' }} />
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '.72rem', color: 'var(--muted)', marginBottom: 4 }}>إلى</label>
          <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} style={{ padding: '8px 12px', background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text)', fontSize: '.82rem' }} />
        </div>
      </div>

      <Card style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: 24 }}><Skeleton width="100%" height={260} borderRadius={8} /></div>
        ) : (<>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.82rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                {['#', 'الزبون', 'الولاية', 'المنتج', 'المقاس', 'المجموع', 'الحالة', 'التاريخ', 'إجراءات'].map(h => (
                  <th key={h} style={{ padding: '12px 14px', textAlign: 'right', color: 'var(--muted)', fontWeight: 700, fontFamily: "'Cairo',sans-serif", fontSize: '.75rem', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {orders.map(o => (
                <tr key={o.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px 14px', fontFamily: "'Cairo',sans-serif", color: 'var(--gold)', fontWeight: 700 }}>#<span className="num">{o.id}</span></td>
                  <td style={{ padding: '12px 14px' }}>{o.customer}</td>
                  <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{o.wilaya}</td>
                  <td style={{ padding: '12px 14px' }}>{o.product}</td>
                  <td style={{ padding: '12px 14px' }}>{o.size}</td>
                  <td style={{ padding: '12px 14px', fontFamily: "'Cairo',sans-serif", fontWeight: 700 }}><span className="num">{o.total.toLocaleString()}</span> دج</td>
                  <td style={{ padding: '12px 14px' }}><Badge variant={o.status === 'مؤكد' ? 'green' : o.status === 'ملغي' ? 'red' : 'yellow'}>{o.status}</Badge></td>
                  <td style={{ padding: '12px 14px', color: 'var(--muted)', fontSize: '.78rem' }}>{o.date}</td>
                  <td style={{ padding: '12px 14px', display: 'flex', gap: 4 }}>
                    <Button size="sm" variant="gold" onClick={() => confirmOrder(o.id)}>تأكيد</Button>
                    <Button size="sm" variant="danger" onClick={() => setCancelId(o.id)}>إلغاء</Button>
                    <Button size="sm" variant="ghost" onClick={() => {}}>Noest</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!orders.length && !loading && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted)' }}>ماكاش طلبات</div>}
          </div>
        </>)}
      </Card>

      {pages > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 16, fontSize: '.85rem', color: 'var(--muted)' }}>
          <span>عرض <span className="num">{from}</span>-<span className="num">{to}</span> من <span className="num">{total}</span> طلب</span>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← السابق</Button>
            <Button size="sm" variant="outline" disabled={page >= pages} onClick={() => setPage(p => p + 1)}>التالي →</Button>
          </div>
        </div>
      )}

      <Modal open={!!cancelId} onClose={() => setCancelId(null)} title="تأكيد الإلغاء">
        <p style={{ marginBottom: 16, color: 'var(--muted)' }}>هل أنت متأكد من إلغاء الطلب #{cancelId}؟</p>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button variant="danger" onClick={cancelOrder}>تأكيد الإلغاء</Button>
          <Button variant="ghost" onClick={() => setCancelId(null)}>رجوع</Button>
        </div>
      </Modal>
    </div>
  );
}

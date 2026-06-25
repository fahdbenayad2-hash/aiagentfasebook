import { useState, useEffect } from 'react';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/ui/Modal';

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
  const [wilayaFilter, setWilayaFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [cancelId, setCancelId] = useState<number | null>(null);

  const fetchOrders = () => {
    const params = new URLSearchParams();
    if (wilayaFilter) params.set('wilaya', wilayaFilter);
    if (statusFilter) params.set('status', statusFilter);
    if (dateFrom) params.set('from', dateFrom);
    if (dateTo) params.set('to', dateTo);
    client.get(`/api/orders?${params}`).then(r => setOrders(r.data)).catch(() => {});
  };

  useEffect(() => { fetchOrders(); }, [wilayaFilter, statusFilter, dateFrom, dateTo]);

  const confirmOrder = async (id: number) => {
    try {
      await client.patch(`/api/orders/${id}`, { status: 'confirmed' });
      fetchOrders();
    } catch {}
  };

  const cancelOrder = async () => {
    if (!cancelId) return;
    try {
      await client.patch(`/api/orders/${cancelId}`, { status: 'cancelled' });
      setCancelId(null);
      fetchOrders();
    } catch {}
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3 style={{ fontSize: '1rem' }}>الطلبات ({orders.length})</h3>
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
                  <td style={{ padding: '12px 14px', fontFamily: "'Cairo',sans-serif", color: 'var(--gold)', fontWeight: 700 }}>#{o.id}</td>
                  <td style={{ padding: '12px 14px' }}>{o.customer}</td>
                  <td style={{ padding: '12px 14px', color: 'var(--muted)' }}>{o.wilaya}</td>
                  <td style={{ padding: '12px 14px' }}>{o.product}</td>
                  <td style={{ padding: '12px 14px' }}>{o.size}</td>
                  <td style={{ padding: '12px 14px', fontFamily: "'Cairo',sans-serif", fontWeight: 700 }}>{o.total.toLocaleString()} دج</td>
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
          {!orders.length && <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted)' }}>ماكاش طلبات</div>}
        </div>
      </Card>

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

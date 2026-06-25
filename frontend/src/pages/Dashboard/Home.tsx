import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { getUser } from '../../hooks/useAuth';

interface Stats {
  conversations_today: number;
  orders_new: number;
  close_rate: number;
  credits_remaining: number;
  conv_delta?: string;
  order_delta?: string;
  rate_delta?: string;
}

interface Conversation {
  id: number;
  customer_name: string;
  last_message: string;
  time_ago: string;
  status: string;
}

interface Order {
  id: number;
  customer: string;
  product: string;
  wilaya: string;
  status: string;
}

export default function DashboardHome() {
  const nav = useNavigate();
  const user = getUser();
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentConvs, setRecentConvs] = useState<Conversation[]>([]);
  const [recentOrders, setRecentOrders] = useState<Order[]>([]);

  useEffect(() => {
    Promise.all([
      client.get('/api/dashboard/stats'),
      client.get('/api/conversations?limit=5'),
      client.get('/api/orders?limit=5'),
    ]).then(([s, c, o]) => {
      setStats(s.data);
      setRecentConvs(c.data);
      setRecentOrders(o.data);
    }).catch(() => {});
  }, []);

  const statCards = stats ? [
    { label: 'محادثات اليوم', value: stats.conversations_today.toString(), delta: stats.conv_delta || '+0' },
    { label: 'طلبات جديدة', value: stats.orders_new.toString(), delta: stats.order_delta || '+0' },
    { label: 'معدل الإغلاق', value: `${stats.close_rate}%`, delta: stats.rate_delta || '0%' },
    { label: 'نقاط متبقية', value: stats.credits_remaining.toLocaleString(), delta: '' },
  ] : [];

  const statusColors: Record<string, 'green' | 'gold' | 'terra' | 'muted'> = {
    'نشط': 'green',
    'مريا': 'gold',
    'يدوي': 'terra',
    'طلب مسجّل': 'muted',
  };

  const orderStatusColors: Record<string, 'muted' | 'gold' | 'green' | 'terra'> = {
    'معلق': 'muted',
    'مؤكد': 'gold',
    'في التوصيل': 'terra',
    'مسلّم': 'green',
  };

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
        {statCards.map((s, i) => (
          <Card key={i} style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '.78rem', color: 'var(--muted)', marginBottom: 8 }}>{s.label}</div>
            <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '2rem', fontWeight: 900, color: 'var(--gold)', lineHeight: 1 }}>{s.value}</div>
            {s.delta && <div style={{ fontSize: '.75rem', color: 'var(--success)', marginTop: 4 }}>{s.delta}</div>}
          </Card>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <Card>
          <h3 style={{ marginBottom: 16, fontSize: '.95rem' }}>آخر المحادثات</h3>
          {recentConvs.map(c => (
            <div key={c.id} onClick={() => nav(`/dashboard/conversations?id=${c.id}`)} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0', borderBottom: '1px solid var(--border)', cursor: 'pointer' }}>
              <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--gold-d)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.8rem', color: 'var(--gold)', flexShrink: 0 }}>
                {(c.customer_name || '?')[0]}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 600, fontSize: '.85rem' }}>{c.customer_name}</div>
                <div style={{ fontSize: '.75rem', color: 'var(--muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.last_message}</div>
              </div>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontSize: '.7rem', color: 'var(--faint)', marginBottom: 4 }}>{c.time_ago}</div>
                <Badge color={statusColors[c.status] || 'muted'}>{c.status}</Badge>
              </div>
            </div>
          ))}
          {!recentConvs.length && <div style={{ color: 'var(--muted)', fontSize: '.85rem', textAlign: 'center', padding: 20 }}>ماكاش محادثات حالياً</div>}
        </Card>

        <Card>
          <h3 style={{ marginBottom: 16, fontSize: '.95rem' }}>آخر الطلبات</h3>
          {recentOrders.map(o => (
            <div key={o.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0', borderBottom: '1px solid var(--border)' }}>
              <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.82rem', fontWeight: 700, color: 'var(--gold)', width: 50, flexShrink: 0 }}>#{o.id}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '.85rem', fontWeight: 600 }}>{o.customer}</div>
                <div style={{ fontSize: '.75rem', color: 'var(--muted)' }}>{o.product} • {o.wilaya}</div>
              </div>
              <Badge color={orderStatusColors[o.status] || 'muted'}>{o.status}</Badge>
            </div>
          ))}
          {!recentOrders.length && <div style={{ color: 'var(--muted)', fontSize: '.85rem', textAlign: 'center', padding: 20 }}>ماكاش طلبات حالياً</div>}
        </Card>
      </div>
    </div>
  );
}

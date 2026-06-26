import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, ShoppingCart, Coins, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Skeleton from '../../components/ui/Skeleton';
import { staggerContainer, fadeUp } from '../../animations/variants';

interface OrderRow {
  id: number;
  customer: string;
  total: number;
  total_price?: number;
  status: string;
}

const STATS: { key: keyof DashboardStats; icon: any; label: string; color: string; bg: string }[] = [
  { key: 'conversations_today', icon: MessageSquare, label: 'إجمالي المحادثات', color: '#4A7FB5', bg: 'rgba(74,127,181,0.1)' },
  { key: 'orders_new', icon: ShoppingCart, label: 'الطلبات اليوم', color: '#5A9E6F', bg: 'rgba(90,158,111,0.1)' },
  { key: 'credits_remaining', icon: Coins, label: 'الرصيد المتبقي', color: '#E8A830', bg: 'rgba(232,168,48,0.1)' },
  { key: 'close_rate', icon: TrendingUp, label: 'معدل التحويل', color: '#8B6FBF', bg: 'rgba(139,111,191,0.1)' },
];

function CountUp({ end }: { end: number }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (end === 0) return;
    const start = performance.now();
    const duration = 1500;
    const raf = requestAnimationFrame(function animate(now) {
      const p = Math.min((now - start) / duration, 1);
      const e = 1 - Math.pow(1 - p, 3);
      setCount(Math.floor(e * end));
      if (p < 1) requestAnimationFrame(animate);
    });
    return () => cancelAnimationFrame(raf);
  }, [end]);
  return <>{count}</>;
}

interface DashboardStats {
  conversations_today: number;
  orders_new: number;
  credits_remaining: number;
  close_rate: number;
}

export default function DashboardHome() {
  const [stats, setStats] = useState<DashboardStats>({ conversations_today: 0, orders_new: 0, credits_remaining: 0, close_rate: 0 });
  const [recentOrders, setRecentOrders] = useState<OrderRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      client.get('/api/dashboard/stats', { signal: controller.signal }).then(r => setStats(r.data)).catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Home stats]:', err); }),
      client.get('/api/orders?limit=5', { signal: controller.signal }).then(r => setRecentOrders(r.data?.data || r.data || [])).catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Home orders]:', err); }),
    ]).finally(() => setLoading(false));
    return () => controller.abort();
  }, []);

  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="visible">
      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
          {[1,2,3,4].map(i => (
            <Card key={i}><Skeleton width={48} height={48} borderRadius={12} style={{marginBottom:12}} /><Skeleton width="40%" height={28} style={{marginBottom:8}} /><Skeleton width="60%" height={14} /></Card>
          ))}
        </div>
      ) : (<>
      <div className="grid-4 stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
        {STATS.map((s, i) => (
          <motion.div key={s.key} variants={fadeUp} transition={{ delay: i * 0.08 }}>
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.75rem', fontWeight: 900, lineHeight: 1 }}>
                    {s.key !== 'close_rate' ? (
                      <span className="num"><CountUp end={stats[s.key] || 0} /></span>
                    ) : (
                      <span className="num">{(stats[s.key] || 0)}%</span>
                    )}
                  </div>
                  <div style={{ fontSize: '.82rem', color: 'var(--muted)', marginTop: 4 }}>{s.label}</div>
                </div>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: s.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <s.icon size={20} style={{ color: s.color }} />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="charts-row" style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 16, marginBottom: 24 }}>
        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>نشاط المحادثات (7 أيام)</h3>
          {stats.conversations_today > 0 ? (
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={[{ day: 'اليوم', inbound: stats.conversations_today, orders: stats.orders_new }]}>
              <defs>
                <linearGradient id="goldGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#E8A830" stopOpacity={0.2}/><stop offset="100%" stopColor="#E8A830" stopOpacity={0}/></linearGradient>
                <linearGradient id="greenGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#5A9E6F" stopOpacity={0.2}/><stop offset="100%" stopColor="#5A9E6F" stopOpacity={0}/></linearGradient>
              </defs>
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#3A3F4A', fontSize: 11 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: '#3A3F4A', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0D1018', border: '1px solid rgba(232,168,48,0.25)', borderRadius: 8, color: '#EDE9E0', fontSize: 12 }} />
              <Area type="monotone" dataKey="inbound" stroke="#E8A830" fill="url(#goldGrad)" strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="orders" stroke="#5A9E6F" fill="url(#greenGrad)" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
          ) : (
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:240, color:'var(--muted)', fontSize:'.85rem' }}>لا توجد بيانات كافية بعد</div>
          )}
        </Card>

        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>آخر الطلبات</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recentOrders.map((o: any, i: number) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: i < recentOrders.length - 1 ? '1px solid var(--border)' : 'none' }}>
                <div>
                  <div style={{ fontSize: '.82rem', fontWeight: 600 }}>{o.customer || `عميل #${o.id}`}</div>
                  <div style={{ fontSize: '.72rem', color: 'var(--muted)' }}>#{o.id}</div>
                </div>
                <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
                  <span className="num" style={{ fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.82rem' }}>{(o.total || o.total_price)?.toLocaleString()} دج</span>
                  <Badge variant={o.status === 'مؤكد' || o.status === 'confirmed' ? 'green' : o.status === 'ملغي' || o.status === 'cancelled' ? 'red' : o.status === 'pending' ? 'yellow' : 'default'}>
                    {o.status || 'قيد الانتظار'}
                  </Badge>
                </div>
              </div>
            ))}
            {!recentOrders.length && <div style={{ color: 'var(--muted)', fontSize: '.82rem', textAlign: 'center', padding: '1rem' }}>ماكاش طلبات</div>}
          </div>
        </Card>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>أداء المنصات</h3>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:160, color:'var(--muted)', fontSize:'.85rem' }}>تظهر الإحصائيات هنا بعد توفر البيانات</div>
        </Card>

        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>العملاء الأكثر تفاعلاً</h3>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:160, color:'var(--muted)', fontSize:'.85rem' }}>لا يوجد عملاء بعد</div>
        </Card>
      </div>
      </>)}
    </motion.div>
  );
}

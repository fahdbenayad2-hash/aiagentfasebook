import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, ShoppingCart, Coins, TrendingUp, Phone, Globe } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart, PieChart, Pie, Cell } from 'recharts';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { staggerContainer, fadeUp } from '../../animations/variants';
import ScrollReveal from '../../components/landing/ScrollReveal';

const STATS = [
  { key: 'conversations', icon: MessageSquare, label: 'إجمالي المحادثات', color: '#4A7FB5', bg: 'rgba(74,127,181,0.1)' },
  { key: 'today_orders', icon: ShoppingCart, label: 'الطلبات اليوم', color: '#5A9E6F', bg: 'rgba(90,158,111,0.1)' },
  { key: 'credits', icon: Coins, label: 'الرصيد المتبقي', color: '#E8A830', bg: 'rgba(232,168,48,0.1)' },
  { key: 'conversion_rate', icon: TrendingUp, label: 'معدل التحويل', color: '#8B6FBF', bg: 'rgba(139,111,191,0.1)' },
];

const CHART_DATA = [
  { day: 'السبت', inbound: 28, orders: 12 },
  { day: 'الأحد', inbound: 35, orders: 18 },
  { day: 'الإثنين', inbound: 42, orders: 22 },
  { day: 'الثلاثاء', inbound: 38, orders: 20 },
  { day: 'الأربعاء', inbound: 45, orders: 25 },
  { day: 'الخميس', inbound: 52, orders: 30 },
  { day: 'الجمعة', inbound: 48, orders: 28 },
];

const PIE_DATA = [
  { name: 'فيسبوك', value: 65, color: '#E8A830' },
  { name: 'إنستغرام', value: 25, color: '#8B6FBF' },
  { name: 'واتساب', value: 10, color: '#4A7FB5' },
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

export default function DashboardHome() {
  const [stats, setStats] = useState<any>({ conversations: 0, today_orders: 0, credits: 0, conversion_rate: 0 });
  const [recentOrders, setRecentOrders] = useState<any[]>([]);

  useEffect(() => {
    client.get('/api/dashboard/stats').then(r => setStats(r.data)).catch(() => {});
    client.get('/api/orders?limit=5').then(r => setRecentOrders(r.data || [])).catch(() => {});
  }, []);

  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="visible">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
        {STATS.map((s, i) => (
          <motion.div key={s.key} variants={fadeUp} transition={{ delay: i * 0.08 }}>
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.75rem', fontWeight: 900, lineHeight: 1 }}>
                    {s.key === 'credits' || s.key === 'conversations' || s.key === 'today_orders' ? (
                      <CountUp end={stats[s.key] || 0} />
                    ) : (
                      <span>{(stats[s.key] || 0)}%</span>
                    )}
                  </div>
                  <div style={{ fontSize: '.8rem', color: 'var(--muted)', marginTop: 4 }}>{s.label}</div>
                </div>
                <div style={{ width: 40, height: 40, borderRadius: 12, background: s.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', color: s.color }}>
                  <s.icon size={18} />
                </div>
              </div>
              <div style={{ fontSize: '.72rem', color: 'var(--faint)', marginTop: 8, display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ color: 'var(--success)' }}>↑ 12%</span> مقارنة بالأمس
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 16, marginBottom: 24 }}>
        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>نشاط المحادثات (7 أيام)</h3>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={CHART_DATA}>
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
        </Card>

        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>آخر الطلبات</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {recentOrders.map((o: any, i: number) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: i < recentOrders.length - 1 ? '1px solid var(--border)' : 'none' }}>
                <div>
                  <div style={{ fontSize: '.82rem', fontWeight: 600 }}>{o.customer_name || `عميل #${o.id}`}</div>
                  <div style={{ fontSize: '.72rem', color: 'var(--muted)' }}>#{o.id}</div>
                </div>
                <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
                  <span style={{ fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.82rem' }}>{o.total_price?.toLocaleString()} دج</span>
                  <Badge variant={o.status === 'مؤكد' ? 'green' : o.status === 'ملغي' ? 'red' : o.status === 'pending' ? 'yellow' : 'default'}>
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
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <ResponsiveContainer width={160} height={160}>
              <PieChart>
                <Pie data={PIE_DATA} cx="50%" cy="50%" innerRadius={50} outerRadius={70} dataKey="value" stroke="none">
                  {PIE_DATA.map(e => <Cell key={e.name} fill={e.color} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {PIE_DATA.map(e => (
                <div key={e.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '.82rem' }}>
                  <div style={{ width: 10, height: 10, borderRadius: 3, background: e.color }} />
                  <span style={{ color: 'var(--muted)' }}>{e.name}</span>
                  <span style={{ fontWeight: 700 }}>{e.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </Card>

        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>العملاء الأكثر تفاعلاً</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { name: 'سارة', msgs: 24, spent: 12400 },
              { name: 'نهاد', msgs: 18, spent: 8900 },
              { name: 'مريم', msgs: 15, spent: 7500 },
              { name: 'أحمد', msgs: 12, spent: 6200 },
              { name: 'خديجة', msgs: 10, spent: 5100 },
            ].map((c, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0', borderBottom: i < 4 ? '1px solid var(--border)' : 'none' }}>
                <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--gold-d)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.75rem', color: 'var(--gold)' }}>{c.name[0]}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '.82rem', fontWeight: 600 }}>{c.name}</div>
                  <div style={{ fontSize: '.72rem', color: 'var(--muted)' }}>{c.msgs} محادثة</div>
                </div>
                <span style={{ fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.82rem', color: 'var(--gold)' }}>{c.spent.toLocaleString()} دج</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </motion.div>
  );
}

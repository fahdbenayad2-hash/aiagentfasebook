import { motion } from 'framer-motion';
import Card from '../../components/ui/Card';
import { staggerContainer, fadeUp } from '../../animations/variants';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, Area, AreaChart } from 'recharts';

const MONTHLY = [
  { month: 'يناير', conversations: 180, orders: 72, revenue: 216000 },
  { month: 'فبراير', conversations: 210, orders: 85, revenue: 255000 },
  { month: 'مارس', conversations: 245, orders: 98, revenue: 294000 },
  { month: 'أبريل', conversations: 280, orders: 112, revenue: 336000 },
  { month: 'ماي', conversations: 310, orders: 125, revenue: 375000 },
  { month: 'يونيو', conversations: 340, orders: 138, revenue: 414000 },
];

const TOP_PRODUCTS = [
  { name: 'قيلا رزيزة', sales: 145, revenue: 406000 },
  { name: 'بلوزة صيفية', sales: 98, revenue: 156800 },
  { name: 'فساتين سهرة', sales: 76, revenue: 342000 },
  { name: 'بناطيل جينز', sales: 62, revenue: 124000 },
  { name: 'إكسسوارات', sales: 48, revenue: 48000 },
];

export default function Analytics() {
  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="visible">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <motion.div variants={fadeUp}>
          <Card>
            <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>أداء المبيعات الشهري</h3>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={MONTHLY}>
                <defs>
                  <linearGradient id="revGrad"><stop offset="0%" stopColor="#E8A830" stopOpacity={0.2}/><stop offset="100%" stopColor="#E8A830" stopOpacity={0}/></linearGradient>
                </defs>
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#3A3F4A', fontSize: 11 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#3A3F4A', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0D1018', border: '1px solid rgba(232,168,48,0.25)', borderRadius: 8, color: '#EDE9E0', fontSize: 12 }} />
                <Area type="monotone" dataKey="revenue" stroke="#E8A830" fill="url(#revGrad)" strokeWidth={2} dot={{ fill: '#E8A830', r: 3 }} />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>

        <motion.div variants={fadeUp} transition={{ delay: 0.08 }}>
          <Card>
            <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>المحادثات والطلبات</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={MONTHLY}>
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#3A3F4A', fontSize: 11 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#3A3F4A', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0D1018', border: '1px solid rgba(232,168,48,0.25)', borderRadius: 8, color: '#EDE9E0', fontSize: 12 }} />
                <Bar dataKey="conversations" fill="#4A7FB5" radius={[4, 4, 0, 0]} />
                <Bar dataKey="orders" fill="#E8A830" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>
      </div>

      <motion.div variants={fadeUp}>
        <Card>
          <h3 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: 16 }}>أفضل المنتجات مبيعاً</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {TOP_PRODUCTS.map((p, i) => (
              <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 24, height: 24, borderRadius: '50%', background: 'var(--gold-d)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.72rem', color: 'var(--gold)' }}>{i + 1}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: '.85rem', fontWeight: 600 }}>{p.name}</span>
                    <span style={{ fontSize: '.82rem', color: 'var(--gold)', fontWeight: 700, fontFamily: "'Cairo',sans-serif" }}>{p.sales} مبيعات</span>
                  </div>
                  <div style={{ height: 6, background: 'var(--bg3)', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{ width: `${(p.sales / TOP_PRODUCTS[0].sales) * 100}%`, height: '100%', background: 'var(--gold)', borderRadius: 3 }} />
                  </div>
                  <div style={{ fontSize: '.72rem', color: 'var(--muted)', marginTop: 2 }}>{p.revenue.toLocaleString()} دج</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}

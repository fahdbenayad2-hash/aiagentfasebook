import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, MessageSquare, ShoppingCart } from 'lucide-react';
import ScrollReveal from './ScrollReveal';

const TABS = [
  { id: 'dashboard', icon: <LayoutDashboard size={20} />, label: 'لوحة المعلومات' },
  { id: 'chat', icon: <MessageSquare size={20} />, label: 'المحادثات الذكية' },
  { id: 'orders', icon: <ShoppingCart size={20} />, label: 'إدارة الطلبات' },
];

const TAB_CONTENT: Record<string, { title: string; desc: string; features: string[] }> = {
  dashboard: {
    title: 'لوحة تحكم كاملة',
    desc: 'كل شيء في مكان واحد — المحادثات، الطلبات، المنتجات، والإحصائيات.',
    features: ['إحصائيات حية', 'إدارة المنتجات', 'تقارير المبيعات', 'تحكم كامل'],
  },
  chat: {
    title: 'محادثات ذكية بالفهم السياقي',
    desc: 'فهد يفهم السياق الكامل للمحادثة، مش غير ردود مبرمجة. يتابع الطلب من البداية للنهاية.',
    features: ['فهم الدارجة', 'ردود ذكية', 'تحويل بشري', 'وسائط متعددة'],
  },
  orders: {
    title: 'إدارة الطلبات بشكل احترافي',
    desc: 'تسجيل تلقائي للطلبات مع معلومات العميل، الولاية، والمبلغ — كل طلب في مكانه.',
    features: ['تسجيل تلقائي', 'حالات الطلب', 'تصدير CSV', 'إشعارات تلجرام'],
  },
};

export default function HowItWorksSection() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <section id="how" style={{ padding: '5rem 4rem', background: 'var(--bg3)' }}>
      <ScrollReveal>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.75rem', fontWeight: 700, color: 'var(--gold)', letterSpacing: '.18em', marginBottom: '.9rem' }}>✦ كيفاش تخدم</div>
          <h2 style={{ fontSize: 'clamp(1.75rem,2.8vw,2.4rem)', fontWeight: 800, lineHeight: 1.25, marginBottom: '.85rem' }}>نظام متكامل يمنحك السيطرة الكاملة</h2>
        </div>
      </ScrollReveal>

      <div style={{ display: 'flex', justifyContent: 'center', gap: 4, marginBottom: '2.5rem' }}>
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '.6rem 1.4rem', borderRadius: 8, border: 'none',
              background: activeTab === tab.id ? 'var(--gold-d)' : 'transparent',
              color: activeTab === tab.id ? 'var(--gold)' : 'var(--muted)',
              fontWeight: 700, fontSize: '.88rem', fontFamily: "'Cairo',sans-serif",
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '.5rem',
              transition: 'all .25s',
            }}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          style={{ maxWidth: 640, margin: '0 auto', textAlign: 'center' }}
        >
          <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '.75rem' }}>{TAB_CONTENT[activeTab].title}</h3>
          <p style={{ color: 'var(--muted)', fontSize: '.95rem', marginBottom: '1.5rem' }}>{TAB_CONTENT[activeTab].desc}</p>
          <div style={{ display: 'flex', gap: '.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            {TAB_CONTENT[activeTab].features.map(f => (
              <span key={f} style={{ background: 'var(--bg2)', border: '1px solid var(--border)', padding: '.4rem 1rem', borderRadius: 8, fontSize: '.85rem', fontFamily: "'Cairo',sans-serif", fontWeight: 600 }}>
                ✦ {f}
              </span>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>
    </section>
  );
}

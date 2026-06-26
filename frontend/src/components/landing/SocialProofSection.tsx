import { motion } from 'framer-motion';
import { Store, MessageSquare, Heart } from 'lucide-react';

const STATS = [
  { icon: <Store size={22} />, value: '+50 تاجر', label: 'يستخدمون فهد' },
  { icon: <MessageSquare size={22} />, value: '+5,000 رد/يوم', label: 'رد تلقائي' },
  { icon: <Heart size={22} />, value: '94%', label: 'نسبة رضا' },
];

export default function SocialProofSection() {
  return (
    <section style={{ padding: '4rem 2rem', textAlign: 'center' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        style={{ display: 'flex', justifyContent: 'center', gap: '3rem', flexWrap: 'wrap', maxWidth: 800, margin: '0 auto' }}
      >
        {STATS.map(s => (
          <div key={s.value} style={{ textAlign: 'center' }}>
            <div style={{ color: 'var(--gold)', marginBottom: 8 }}>{s.icon}</div>
            <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.6rem', fontWeight: 900, color: 'var(--text)' }}>{s.value}</div>
            <div style={{ fontSize: '.82rem', color: 'var(--muted)' }}>{s.label}</div>
          </div>
        ))}
      </motion.div>
    </section>
  );
}

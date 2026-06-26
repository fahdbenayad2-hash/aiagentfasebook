import { motion } from 'framer-motion';
import { Brain, MessageCircle, Clock, Truck, Users, Bell } from 'lucide-react';
import ScrollReveal from './ScrollReveal';
import { staggerContainer } from '../../animations/variants';

const FEATURES = [
  { icon: <Brain size={24} />, title: 'رد آلي بالذكاء الاصطناعي', desc: 'Groq AI (llama-3.3-70b) — أسرع وأذكى وكيل مبيعات' },
  { icon: <MessageCircle size={24} />, title: 'فهم الدارجة الجزائرية', desc: 'مدرب خصيصاً على الدارجة بكل تنوعاتها — "واش عندكم؟"، "بكاش؟"، "يصلح هذا؟"' },
  { icon: <Clock size={24} />, title: '24/7 بدون توقف', desc: 'لا إجازات، لا دوام، لا تأخير — يرد على زبائنك في أي وقت' },
  { icon: <Truck size={24} />, title: 'تتبع طلبات COD', desc: 'الدفع عند الاستلام مع 58 ولاية — تكلفة التوصيل مباشرة في المحادثة' },
  { icon: <Users size={24} />, title: 'تحويل ذكي لموظف بشري', desc: 'عندما لا يعرف الإجابة، يحول المحادثة فوراً — بدون نقاط محسوبة' },
  { icon: <Bell size={24} />, title: 'إشعارات فورية', desc: 'إشعارات Telegram لكل طلب جديد — ابقى على اطلاع دائم' },
];

export default function FeaturesSection() {
  return (
    <section id="features" className="landing-features" style={{ padding: '5rem 4rem', background: 'var(--bg)' }}>
      <ScrollReveal>
        <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.75rem', fontWeight: 700, color: 'var(--gold)', letterSpacing: '.18em', marginBottom: '.9rem' }}>✦ المميزات</div>
          <h2 style={{ fontSize: 'clamp(1.75rem,2.8vw,2.4rem)', fontWeight: 800, lineHeight: 1.25, marginBottom: '.85rem' }}>لماذا فهد هو خيارك الأفضل؟</h2>
        </div>
      </ScrollReveal>

      <motion.div variants={staggerContainer} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-50px' }} className="features-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '1.25rem', maxWidth: 900, margin: '0 auto' }}>
        {FEATURES.map((f, i) => (
          <ScrollReveal key={f.title} delay={i * 0.08}>
            <div style={{ background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 16, padding: '1.75rem', position: 'relative', overflow: 'hidden', transition: 'all .28s' }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--b-gold)'; e.currentTarget.style.transform = 'translateY(-3px)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.transform = ''; }}
            >
              <div style={{ width: 44, height: 44, borderRadius: 12, background: 'var(--gold-d)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--gold)', marginBottom: '.85rem' }}>{f.icon}</div>
              <h3 style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.05rem', fontWeight: 700, marginBottom: '.6rem' }}>{f.title}</h3>
              <p style={{ color: 'var(--muted)', fontSize: '.88rem', lineHeight: 1.75 }}>{f.desc}</p>
            </div>
          </ScrollReveal>
        ))}
      </motion.div>
    </section>
  );
}

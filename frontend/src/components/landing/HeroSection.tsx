import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Play, MessageCircle, Clock, Globe, Smartphone } from 'lucide-react';

const CHAT_MSGS = [
  { t: 'in', txt: 'السلام، واش عندكم القيلا بالرزيزة في L؟', ms: 800 },
  { t: 'out', txt: 'وعليكم السلام! آه عندنا 🎉 القيلا رزيزة متوفرة في L — السعر 2,800 دج. التوصيل 48-72 ساعة لكل الولايات. تحبي نسجّل ليك واحدة؟', ms: 2600 },
  { t: 'in', txt: 'آه واه، الاسم نهاد، وهران', ms: 5000 },
  { t: 'out', txt: 'تمام نهاد! سجّلنا طلبك ✅ رقم الطلب: #1047. التوصيل لوهران: 500 دج. المجموع: 3,300 دج. راح يتواصل معك الفريق قريب 🚚', ms: 6600 },
];

export default function HeroSection() {
  const [chatState, setChatState] = useState<{ bubbles: { t: string; txt: string }[]; typing: boolean }>({ bubbles: [], typing: false });

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    let idx = 0;
    const runChat = () => {
      CHAT_MSGS.forEach((m, i) => {
        const t = setTimeout(() => {
          if (m.t === 'out') {
            setChatState(prev => ({ ...prev, typing: true }));
            setTimeout(() => {
              setChatState(prev => ({ bubbles: [...prev.bubbles, m], typing: false }));
            }, 1200);
          } else {
              setChatState(prev => ({ bubbles: [...prev.bubbles, m], typing: false }));
          }
        }, m.ms);
        timers.push(t);
      });
    };
    runChat();
    const reset = setInterval(() => {
      idx = 0;
      setChatState({ bubbles: [], typing: false });
      setTimeout(runChat, 500);
    }, 12000);
    timers.push(reset);
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <section id="hero" className="landing-hero geo-pattern" style={{ minHeight: '100vh', display: 'grid', gridTemplateColumns: '1fr 1fr', alignItems: 'center', gap: '4rem', padding: '8rem 4rem 4rem', position: 'relative', overflow: 'hidden' }}>
      <motion.div initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}>
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.5 }}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '.5rem', background: 'var(--gold-d)', border: '1px solid var(--b-gold)', padding: '.3rem 1rem', borderRadius: 100, fontSize: '.78rem', color: 'var(--gold)', fontFamily: "'Cairo',sans-serif", marginBottom: '1.5rem' }}
        >
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--gold)', animation: 'blink 2s infinite' }} />
          وكيل مبيعات يفهم الدارجة الجزائرية
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          style={{ fontSize: 'clamp(2.8rem,5.5vw,4.5rem)', fontWeight: 900, lineHeight: 1.12, marginBottom: '1rem', letterSpacing: '-.02em' }}
        >
          يفهم. يرد. <span style={{ color: 'var(--gold)' }}>يبيع.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5, duration: 0.5 }}
          style={{ fontSize: '1.05rem', color: 'var(--muted)', marginBottom: '2.5rem', maxWidth: 460, lineHeight: 1.85 }}
        >
          فهد وكيل مبيعات ذكي يرد على زبائنك 24/7 بالدارجة، يسجّل الطلبات، ويحوّل الزائر لزبون بدون ما تكون موجود.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65, duration: 0.5 }}
          style={{ display: 'flex', gap: '.9rem', flexWrap: 'wrap' }}
        >
          <a href="/auth?signup=1">
            <button style={{ background: 'var(--gold)', color: 'var(--bg)', padding: '.85rem 2rem', borderRadius: 8, fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.95rem', border: 'none', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '.4rem', transition: 'all .22s' }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(232,168,48,.3)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}
            >
              جرب الآن مجاناً ←
            </button>
          </a>
          <a href="#how">
            <button style={{ background: 'transparent', color: 'var(--text)', padding: '.85rem 2rem', borderRadius: 8, fontFamily: "'Cairo',sans-serif", fontWeight: 600, fontSize: '.95rem', border: '1px solid var(--border)', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '.4rem', transition: 'all .22s' }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--gold-m)'; e.currentTarget.style.color = 'var(--gold)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text)'; }}

            >
              <Play size={16} /> شوف كيفاش يعمل
            </button>
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8, duration: 0.5 }}
          style={{ display: 'flex', gap: '2rem', marginTop: '3rem', padding: '1.25rem 0', borderTop: '1px solid var(--border)' }}
        >
          {[
            { icon: <Clock size={18} />, label: '24/7 متاح' },
            { icon: <MessageCircle size={18} />, label: 'دارجة جزائرية' },
            { icon: <Smartphone size={18} />, label: '3 منصات' },
          ].map(s => (
            <div key={s.label} style={{ display: 'flex', alignItems: 'center', gap: '.5rem', color: 'var(--muted)', fontSize: '.85rem', fontFamily: "'Cairo',sans-serif", fontWeight: 600 }}>
              <span style={{ color: 'var(--gold)' }}>{s.icon}</span> {s.label}
            </div>
          ))}
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        style={{ display: 'flex', justifyContent: 'center' }}
      >
        <div style={{ width: 290, background: 'var(--bg2)', borderRadius: 38, border: '1.5px solid var(--border)', boxShadow: '0 40px 90px rgba(0,0,0,.65), 0 0 0 1px rgba(255,255,255,.04)', overflow: 'hidden' }}>
          <div style={{ background: 'var(--gold)', padding: '.9rem 1.1rem', display: 'flex', alignItems: 'center', gap: '.65rem' }}>
            <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg,var(--gold),var(--terra))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Cairo',sans-serif", fontWeight: 800, fontSize: '1rem', color: '#fff' }}>ف</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '.85rem', color: '#fff', fontFamily: "'Cairo',sans-serif" }}>فهد — وكيل المبيعات</div>
              <div style={{ fontSize: '.68rem', color: 'rgba(255,255,255,.65)' }}>متاح دائماً ✦</div>
            </div>
          </div>
          <div style={{ padding: '.9rem', minHeight: 360, background: '#f0f2f5', display: 'flex', flexDirection: 'column', gap: '.65rem' }}>
            {chatState.bubbles.map((b, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.9, y: 6 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                style={{ maxWidth: '88%', padding: '.55rem .85rem', borderRadius: 16, fontSize: '.78rem', lineHeight: 1.5, fontFamily: "'Tajawal',sans-serif", whiteSpace: 'pre-line', background: b.t === 'in' ? '#fff' : 'var(--gold)', color: b.t === 'in' ? '#111' : '#fff', alignSelf: b.t === 'in' ? 'flex-start' : 'flex-end', borderBottomRightRadius: b.t === 'in' ? undefined : 3, borderBottomLeftRadius: b.t === 'in' ? 3 : undefined, textAlign: b.t === 'in' ? 'right' : 'right' }}
              >
                {b.txt}
              </motion.div>
            ))}
            {chatState.typing && (
              <div style={{ display: 'flex', gap: 4, alignItems: 'center', padding: '.55rem .85rem', background: '#fff', borderRadius: 16, width: 'fit-content', alignSelf: 'flex-start' }}>
                {[0, 1, 2].map(i => <div key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: '#bbb', animation: `td 1.2s infinite ${i * 0.2}s` }} />)}
              </div>
            )}
          </div>
          <div style={{ padding: '.65rem .9rem', background: '#fff', display: 'flex', alignItems: 'center', gap: '.5rem', borderTop: '1px solid #e5e7eb' }}>
            <div style={{ flex: 1, background: '#f0f2f5', borderRadius: 18, padding: '.35rem .9rem', fontSize: '.72rem', color: '#9ca3af', fontFamily: "'Tajawal',sans-serif" }}>اكتب رسالة...</div>
            <span style={{ fontSize: '.9rem' }}>📤</span>
          </div>
        </div>
      </motion.div>
    </section>
  );
}

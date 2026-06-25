import { useState, useEffect, useRef } from 'react';
import ScrollReveal from './ScrollReveal';

const PLANS = [
  { name: 'البداية', price: '2,500', credits: '5,000', ht: '2,125', tva: '375', popular: false },
  { name: 'النمو', price: '6,000', credits: '15,000', ht: '5,085', tva: '915', popular: true },
  { name: 'المتجر الكبير', price: '18,000', credits: '50,000', ht: '15,254', tva: '2,746', popular: false },
];

function CountUp({ end, duration = 1.5 }: { end: number; duration?: number }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        const start = performance.now();
        const animate = (now: number) => {
          const elapsed = (now - start) / 1000;
          const progress = Math.min(elapsed / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          setCount(Math.floor(eased * end));
          if (progress < 1) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
        observer.unobserve(el);
      }
    }, { threshold: 0.5 });
    observer.observe(el);
    return () => observer.disconnect();
  }, [end, duration]);

  return <span ref={ref}>{count.toLocaleString()}</span>;
}

export default function PricingSection() {
  const [msgs, setMsgs] = useState(5000);
  const pricePerThousand = 500;

  return (
    <section id="pricing" style={{ padding: '5rem 4rem', background: 'var(--bg)' }}>
      <ScrollReveal>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.75rem', fontWeight: 700, color: 'var(--gold)', letterSpacing: '.18em', marginBottom: '.9rem' }}>✦ الأسعار</div>
          <h2 style={{ fontSize: 'clamp(1.75rem,2.8vw,2.4rem)', fontWeight: 800, lineHeight: 1.25, marginBottom: '.85rem' }}>اختر الباقة المناسبة لك</h2>
          <p style={{ color: 'var(--muted)', maxWidth: 520, margin: '0 auto', fontSize: '.95rem' }}>
            نقاط غير منتهية الصلاحية — ادفع على الردود اللي تصنع مبيعات
          </p>
        </div>
      </ScrollReveal>

      <ScrollReveal delay={0.15}>
        <div style={{ maxWidth: 500, margin: '0 auto 3rem', background: 'var(--bg2)', borderRadius: 16, border: '1px solid var(--border)', padding: '1.5rem', textAlign: 'center' }}>
          <h4 style={{ fontSize: '.9rem', fontWeight: 700, marginBottom: '.5rem' }}>حاسبة الرصيد</h4>
          <p style={{ fontSize: '.82rem', color: 'var(--muted)', marginBottom: '.75rem' }}>اختار عدد الردود اللي تحتاجها</p>
          <input
            type="range"
            min={1000}
            max={50000}
            step={1000}
            value={msgs}
            onChange={e => setMsgs(Number(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--gold)', marginBottom: '.5rem' }}
          />
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.1rem', fontWeight: 700, color: 'var(--gold)' }}>
            {msgs.toLocaleString()} رد = {((msgs / 1000) * pricePerThousand).toLocaleString()} دج
          </div>
        </div>
      </ScrollReveal>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '1.25rem', maxWidth: 940, margin: '0 auto' }}>
        {PLANS.map((plan, i) => (
          <ScrollReveal key={plan.name} delay={i * 0.1}>
            <div style={{
              background: plan.popular ? 'linear-gradient(150deg, var(--bg3) 0%, #120F00 100%)' : 'var(--bg2)',
              border: `1px solid ${plan.popular ? 'var(--gold)' : 'var(--border)'}`,
              borderRadius: 20, padding: '1.75rem', position: 'relative', transition: 'all .28s',
            }}
              onMouseEnter={e => { if (!plan.popular) e.currentTarget.style.borderColor = 'var(--b-gold)'; }}
              onMouseLeave={e => { if (!plan.popular) e.currentTarget.style.borderColor = 'var(--border)'; }}
            >
              {plan.popular && (
                <div style={{ position: 'absolute', top: -11, left: '50%', transform: 'translateX(-50%)', background: 'var(--gold)', color: 'var(--bg)', fontFamily: "'Cairo',sans-serif", fontSize: '.7rem', fontWeight: 700, padding: '.2rem .9rem', borderRadius: 100 }}>
                  الأكثر طلباً
                </div>
              )}
              <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.85rem', fontWeight: 700, color: 'var(--muted)', marginBottom: '.75rem' }}>{plan.name}</div>
              <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '2.4rem', fontWeight: 900, lineHeight: 1 }}>
                {plan.price} <sub style={{ fontSize: '1rem', fontWeight: 400, color: 'var(--muted)' }}>دج</sub>
              </div>
              <div style={{ fontSize: '.82rem', color: 'var(--muted)', margin: '.4rem 0 1.25rem' }}>{plan.credits} رد ذكي</div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '.6rem', marginBottom: '1.5rem' }}>
                {['ردود الدارجة والعربي والفرنسي', 'تسجيل الطلبات تلقائي', 'لوحة تحكم كاملة', ...(plan.popular ? ['تكامل Noest Express', 'تقارير المبيعات'] : [])].map(f => (
                  <li key={f} style={{ fontSize: '.85rem', display: 'flex', alignItems: 'flex-start', gap: '.5rem' }}>
                    <span style={{ color: 'var(--gold)', fontSize: '.55rem', marginTop: '.35rem', flexShrink: 0 }}>◆</span> {f}
                  </li>
                ))}
              </ul>
              <a href="/auth?signup=1">
                <button style={{
                  width: '100%', padding: '.7rem', borderRadius: 8, fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.9rem',
                  border: plan.popular ? 'none' : '1px solid var(--border)', cursor: 'pointer',
                  background: plan.popular ? 'var(--gold)' : 'transparent',
                  color: plan.popular ? 'var(--bg)' : 'var(--text)',
                  transition: 'all .2s',
                }}
                  onMouseEnter={e => { if (!plan.popular) e.currentTarget.style.borderColor = 'var(--gold-m)'; }}
                  onMouseLeave={e => { if (!plan.popular) e.currentTarget.style.borderColor = 'var(--border)'; }}
                >
                  ابدأ هنا
                </button>
              </a>
              <div style={{ fontSize: '.7rem', color: 'var(--faint)', marginTop: '.5rem' }}>ش ق م: {plan.ht} دج | الرسم على القيمة المضافة: {plan.tva} دج</div>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </section>
  );
}

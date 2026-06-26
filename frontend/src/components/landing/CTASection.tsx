import ScrollReveal from './ScrollReveal';

export default function CTASection() {
  return (
    <section className="landing-cta" style={{ padding: '5rem 4rem', background: 'var(--bg)' }}>
      <ScrollReveal>
        <div style={{ maxWidth: 660, margin: '0 auto', textAlign: 'center', background: 'linear-gradient(140deg, var(--bg2) 0%, #110E00 100%)', border: '1px solid var(--b-gold)', borderRadius: 24, padding: '3.5rem', position: 'relative', overflow: 'hidden' }}>
          <div className="geo-pattern" style={{ position: 'absolute', inset: 0, opacity: 0.06, pointerEvents: 'none' }} />
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.75rem', fontWeight: 700, color: 'var(--gold)', letterSpacing: '.18em', marginBottom: '.9rem', position: 'relative' }}>✦ ابدأ اليوم</div>
          <h2 style={{ fontSize: 'clamp(1.6rem,2.5vw,2.1rem)', fontWeight: 800, marginBottom: '.9rem', position: 'relative' }}>زبائنك ينتظرون — فهد مستعد</h2>
          <p style={{ color: 'var(--muted)', marginBottom: '2rem', fontSize: '.95rem', position: 'relative' }}>ابدأ تجربتك المجانية اليوم. إعداد في أقل من 10 دقائق، بدون بطاقة بنكية.</p>
          <a href="/auth?signup=1" style={{ position: 'relative', display: 'inline-block' }}>
            <button style={{ background: 'var(--gold)', color: 'var(--bg)', padding: '.9rem 2.25rem', borderRadius: 8, fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '1rem', border: 'none', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '.4rem', transition: 'all .22s' }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(232,168,48,.3)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}
            >
              ابدأ تجربتك المجانية ←
            </button>
          </a>
          <div style={{ fontSize: '.75rem', color: 'var(--faint)', marginTop: '.9rem', position: 'relative' }}>بدون بطاقة بنكية • إلغاء في أي وقت • دعم على واتساب</div>
        </div>
      </ScrollReveal>
    </section>
  );
}

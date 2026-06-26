export default function FooterSection() {
  return (
    <footer className="landing-footer" style={{ borderTop: '1px solid var(--border)' }}>
      <div style={{ height: 2, background: 'linear-gradient(90deg, transparent, var(--gold-m), transparent)' }} />
      <div style={{ padding: '2rem 4rem', display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', gap: '2rem', maxWidth: 1100, margin: '0 auto' }}>
        <div>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.2rem', fontWeight: 900, color: 'var(--text)', marginBottom: '.75rem' }}>فهد <span style={{ color: 'var(--gold)' }}>✦</span></div>
          <p style={{ fontSize: '.82rem', color: 'var(--muted)', lineHeight: 1.7 }}>منصة الذكاء الاصطناعي الأولى في الجزائر للتجارة الإلكترونية. وكيل مبيعات ذكي يفهم الدارجة ويرد على زبائنك 24/7.</p>
        </div>
        <div>
          <h4 style={{ fontSize: '.85rem', fontWeight: 700, marginBottom: '.75rem', fontFamily: "'Cairo',sans-serif" }}>روابط سريعة</h4>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '.4rem' }}>
            <li><a href="/" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '.82rem', transition: 'color .2s' }}>الرئيسية</a></li>
            <li><a href="/pricing" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '.82rem', transition: 'color .2s' }}>الأسعار</a></li>
            <li><a href="/privacy" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '.82rem', transition: 'color .2s' }}>سياسة الخصوصية</a></li>
            <li><a href="/terms" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '.82rem', transition: 'color .2s' }}>شروط الاستخدام</a></li>
          </ul>
        </div>
        <div>
          <h4 style={{ fontSize: '.85rem', fontWeight: 700, marginBottom: '.75rem', fontFamily: "'Cairo',sans-serif" }}>تواصل معنا</h4>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '.4rem' }}>
            <li><a href="mailto:admin@store.dz" style={{ color: 'var(--muted)', textDecoration: 'none', fontSize: '.82rem' }}>admin@store.dz</a></li>
            <li><a href="/delete-account" style={{ color: 'var(--danger)', textDecoration: 'none', fontSize: '.78rem', opacity: 0.6 }}>حذف الحساب</a></li>
          </ul>
        </div>
        <div>
          <h4 style={{ fontSize: '.85rem', fontWeight: 700, marginBottom: '.75rem', fontFamily: "'Cairo',sans-serif" }}>اللغة</h4>
          <button style={{ background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6, padding: '.35rem 1rem', color: 'var(--text)', fontFamily: "'Cairo',sans-serif", fontSize: '.85rem', cursor: 'pointer' }}>
            العربية
          </button>
        </div>
      </div>
      <div style={{ padding: '1rem 4rem', borderTop: '1px solid var(--border)', textAlign: 'center' }}>
        <div style={{ fontSize: '.75rem', color: 'var(--faint)' }}>© 2026 فهد. جميع الحقوق محفوظة.</div>
      </div>
    </footer>
  );
}

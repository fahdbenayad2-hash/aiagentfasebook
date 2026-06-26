import { Component, ErrorInfo, ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)', color: 'var(--text)', padding: 24, textAlign: 'center' }}>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '3rem', fontWeight: 900, color: 'var(--gold)', marginBottom: 8 }}>فهد</div>
          <div style={{ fontSize: '1.2rem', marginBottom: 8 }}>⚠️</div>
          <p style={{ color: 'var(--muted)', fontSize: '.9rem', marginBottom: 16 }}>حدث خطأ غير متوقع. حاول تحديث الصفحة.</p>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={() => window.location.href = '/'} style={{ padding: '10px 24px', borderRadius: 8, border: 'none', background: 'var(--gold)', color: 'var(--bg)', fontWeight: 700, cursor: 'pointer', fontFamily: "'Cairo',sans-serif", fontSize: '.85rem', transition:'all .2s' }}
              onMouseEnter={e => e.currentTarget.style.opacity = '0.85'}
              onMouseLeave={e => e.currentTarget.style.opacity = '1'}
            >
              الصفحة الرئيسية
            </button>
            <button onClick={() => window.location.reload()} style={{ padding: '10px 24px', borderRadius: 8, border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)', fontWeight: 600, cursor: 'pointer', fontFamily: "'Cairo',sans-serif", fontSize: '.85rem', transition:'all .2s' }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--gold-m)'; e.currentTarget.style.color = 'var(--gold)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text)'; }}
            >
              تحديث الصفحة
            </button>
          </div>
          <details style={{ marginTop: 24, maxWidth: 500, textAlign: 'left', fontSize: '.72rem', color: 'var(--faint)' }}>
            <summary style={{ cursor: 'pointer', color: 'var(--muted)' }}>التفاصيل التقنية</summary>
            <pre style={{ marginTop: 8, padding: 12, background: 'var(--bg3)', borderRadius: 8, overflow: 'auto', maxHeight: 200, color: 'var(--muted)' }}>{this.state.error?.message}</pre>
          </details>
        </div>
      );
    }
    return this.props.children;
  }
}

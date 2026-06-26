import { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  headerTitle?: string;
  headerStatus?: string;
}

export default function PhoneMockup({ children, headerTitle = 'فهد — وكيلة المبيعات', headerStatus = 'متاحة دائماً ✦' }: Props) {
  return (
    <div
      style={{
        width: 290,
        background: 'var(--bg2)',
        borderRadius: 38,
        border: '1.5px solid var(--border)',
        boxShadow: '0 40px 90px rgba(0,0,0,.65), 0 0 0 1px rgba(255,255,255,.04)',
        overflow: 'hidden',
      }}
    >
      <div style={{ background: '#1877F2', padding: '.9rem 1.1rem', display: 'flex', alignItems: 'center', gap: '.65rem' }}>
        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: '50%',
            flexShrink: 0,
            background: 'linear-gradient(135deg,var(--gold),var(--terra))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: "'Cairo',sans-serif",
            fontWeight: 800,
            fontSize: '1rem',
            color: '#fff',
          }}
        >
          ف
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '.85rem', color: '#fff', fontFamily: "'Cairo',sans-serif" }}>{headerTitle}</div>
          <div style={{ fontSize: '.68rem', color: 'rgba(255,255,255,.65)' }}>{headerStatus}</div>
        </div>
      </div>
      <div
        style={{
          padding: '.9rem',
          minHeight: 360,
          background: '#f0f2f5',
          display: 'flex',
          flexDirection: 'column',
          gap: '.65rem',
        }}
      >
        {children}
      </div>
    </div>
  );
}

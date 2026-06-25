import { ReactNode } from 'react';

type BadgeVariant = 'gold' | 'green' | 'red' | 'yellow' | 'purple' | 'blue' | 'default';

interface Props {
  children: ReactNode;
  variant?: BadgeVariant;
  style?: React.CSSProperties;
}

const colors: Record<BadgeVariant, { bg: string; text: string; border: string }> = {
  gold: { bg: 'rgba(232,168,48,0.12)', text: 'var(--gold)', border: 'var(--b-gold)' },
  green: { bg: 'rgba(34,197,94,0.1)', text: 'var(--success)', border: 'rgba(34,197,94,0.2)' },
  red: { bg: 'rgba(239,68,68,0.1)', text: 'var(--danger)', border: 'rgba(239,68,68,0.2)' },
  yellow: { bg: 'rgba(234,179,8,0.1)', text: '#EAB308', border: 'rgba(234,179,8,0.2)' },
  purple: { bg: 'rgba(139,111,191,0.1)', text: 'var(--purple)', border: 'rgba(139,111,191,0.2)' },
  blue: { bg: 'rgba(74,127,181,0.1)', text: 'var(--blue)', border: 'rgba(74,127,181,0.2)' },
  default: { bg: 'var(--bg3)', text: 'var(--muted)', border: 'var(--border)' },
};

export default function Badge({ children, variant = 'default', style }: Props) {
  const c = colors[variant];
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      background: c.bg, color: c.text, border: `1px solid ${c.border}`,
      padding: '2px 10px', borderRadius: 100,
      fontFamily: "'Cairo',sans-serif", fontSize: '.75rem', fontWeight: 600,
      ...style,
    }}>
      {children}
    </span>
  );
}

import { ReactNode, CSSProperties } from 'react';

type Color = 'gold' | 'green' | 'red' | 'terra' | 'muted';

interface Props {
  children: ReactNode;
  color?: Color;
}

const colors: Record<Color, CSSProperties> = {
  gold: { background: 'var(--gold-d)', border: '1px solid var(--b-gold)', color: 'var(--gold)' },
  green: { background: 'rgba(34,197,94,.12)', border: '1px solid rgba(34,197,94,.3)', color: 'var(--success)' },
  red: { background: 'rgba(239,68,68,.12)', border: '1px solid rgba(239,68,68,.3)', color: 'var(--danger)' },
  terra: { background: 'rgba(184,74,43,.15)', border: '1px solid rgba(184,74,43,.3)', color: '#E86A48' },
  muted: { background: 'var(--border)', border: '1px solid var(--border)', color: 'var(--muted)' },
};

export default function Badge({ children, color = 'muted' }: Props) {
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '.15rem .6rem',
        borderRadius: 100,
        fontSize: .7,
        fontWeight: 700,
        fontFamily: "'Cairo',sans-serif",
        ...colors[color],
      }}
    >
      {children}
    </span>
  );
}

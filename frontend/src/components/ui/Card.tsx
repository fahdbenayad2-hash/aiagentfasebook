import { ReactNode, CSSProperties } from 'react';

interface Props {
  children: ReactNode;
  style?: CSSProperties;
  gold?: boolean;
  onClick?: () => void;
}

export default function Card({ children, style, gold, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      style={{
        background: 'var(--bg2)',
        border: `1px solid ${gold ? 'var(--b-gold)' : 'var(--border)'}`,
        borderRadius: 16,
        padding: '1.5rem',
        transition: 'all .28s',
        cursor: onClick ? 'pointer' : undefined,
        ...style,
      }}
    >
      {children}
    </div>
  );
}

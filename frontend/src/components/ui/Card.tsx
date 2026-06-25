import { ReactNode, CSSProperties, useState } from 'react';

interface Props {
  children: ReactNode;
  style?: CSSProperties;
  gold?: boolean;
  hover?: boolean;
  onClick?: () => void;
}

export default function Card({ children, style, gold, hover, onClick }: Props) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => hover && setIsHovered(true)}
      onMouseLeave={() => hover && setIsHovered(false)}
      style={{
        background: 'var(--bg2)',
        border: `1px solid ${gold ? 'var(--b-gold)' : isHovered ? 'var(--b-gold)' : 'var(--border)'}`,
        borderRadius: 16,
        padding: '1.5rem',
        transition: 'all .28s',
        cursor: onClick ? 'pointer' : undefined,
        transform: isHovered ? 'translateY(-4px)' : undefined,
        boxShadow: isHovered ? '0 8px 30px rgba(0,0,0,0.3)' : undefined,
        ...style,
      }}
    >
      {children}
    </div>
  );
}

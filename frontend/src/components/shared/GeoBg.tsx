import { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  style?: React.CSSProperties;
}

const GEO_SVG = `url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%23E8A830' stroke-width='.6' opacity='.1'%3E%3Cpath d='M40 8 L72 40 L40 72 L8 40 Z'/%3E%3Cpath d='M40 22 L58 40 L40 58 L22 40 Z'/%3E%3Cline x1='40' y1='8' x2='40' y2='72'/%3E%3Cline x1='8' y1='40' x2='72' y2='40'/%3E%3C/g%3E%3C/svg%3E")`;

export default function GeoBg({ children, style }: Props) {
  return (
    <div
      style={{
        minHeight: '100vh',
        background: `
          radial-gradient(ellipse 80% 60% at 50% 0%, rgba(232,168,48,.055) 0%, transparent 70%),
          ${GEO_SVG}
        `,
        backgroundColor: 'var(--bg)',
        ...style,
      }}
    >
      {children}
    </div>
  );
}

import { CSSProperties } from 'react';

interface Props {
  width?: string | number;
  height?: string | number;
  borderRadius?: number;
  style?: CSSProperties;
}

export default function Skeleton({ width = '100%', height = 16, borderRadius = 8, style }: Props) {
  return (
    <div
      style={{
        width, height, borderRadius,
        background: 'linear-gradient(90deg, var(--bg3) 25%, var(--bg2) 50%, var(--bg3) 75%)',
        backgroundSize: '200% 100%',
        animation: 'shimmer 1.5s infinite linear',
        ...style,
      }}
    />
  );
}

export function CardSkeleton() {
  return (
    <div style={{ background: 'var(--bg2)', borderRadius: 16, padding: '1.5rem', border: '1px solid var(--border)' }}>
      <Skeleton width={48} height={48} borderRadius={12} style={{ marginBottom: 12 }} />
      <Skeleton width="60%" height={18} style={{ marginBottom: 8 }} />
      <Skeleton width="80%" height={14} />
    </div>
  );
}

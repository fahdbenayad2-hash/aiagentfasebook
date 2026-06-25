import { ButtonHTMLAttributes, ReactNode, CSSProperties } from 'react';

type Variant = 'gold' | 'ghost' | 'outline' | 'danger' | 'glass';
type Size = 'sm' | 'md' | 'lg';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  children: ReactNode;
}

const styles: Record<Variant, CSSProperties> = {
  gold: { background: 'var(--gold)', color: 'var(--bg)', fontWeight: 700, border: 'none' },
  ghost: { background: 'transparent', color: 'var(--text)', fontWeight: 600, border: '1px solid var(--border)' },
  outline: { background: 'transparent', color: 'var(--text)', fontWeight: 700, border: '1px solid var(--border)' },
  danger: { background: 'var(--danger)', color: '#fff', fontWeight: 700, border: 'none' },
  glass: { background: 'rgba(232,168,48,0.08)', color: 'var(--gold)', fontWeight: 700, border: '1px solid var(--b-gold)', backdropFilter: 'blur(12px)' },
};

const sizes: Record<Size, CSSProperties> = {
  sm: { padding: '.45rem 1rem', fontSize: '.8rem', borderRadius: 6 },
  md: { padding: '.7rem 1.5rem', fontSize: '.9rem', borderRadius: 8 },
  lg: { padding: '.85rem 2rem', fontSize: '.95rem', borderRadius: 8 },
};

export default function Button({ variant = 'gold', size = 'md', loading, children, style, disabled, ...rest }: Props) {
  return (
    <button
      style={{
        ...styles[variant],
        ...sizes[size],
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '.4rem',
        cursor: (disabled || loading) ? 'not-allowed' : 'pointer',
        opacity: (disabled || loading) ? .6 : 1,
        transition: 'all .22s',
        ...style,
      }}
      onMouseEnter={e => { if (!disabled && !loading) { e.currentTarget.style.transform = 'translateY(-1px)'; if (variant === 'gold') e.currentTarget.style.boxShadow = '0 6px 20px rgba(232,168,48,.3)'; } }}
      onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}
      onMouseDown={e => { if (!disabled && !loading) e.currentTarget.style.transform = 'scale(0.97)'; }}
      onMouseUp={e => { if (!disabled && !loading) e.currentTarget.style.transform = ''; }}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && <span style={{ width: 14, height: 14, border: '2px solid currentColor', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin .6s linear infinite', display: 'inline-block' }} />}
      {children}
    </button>
  );
}

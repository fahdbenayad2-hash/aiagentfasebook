import { InputHTMLAttributes, forwardRef } from 'react';

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, Props>(({ label, error, style, ...rest }, ref) => (
  <div style={{ marginBottom: 16 }}>
    {label && <label style={{ display: 'block', marginBottom: 6, fontWeight: 600, fontSize: 14, color: 'var(--muted)' }}>{label}</label>}
    <input
      ref={ref}
      style={{
        width: '100%',
        padding: '12px 14px',
        background: 'var(--bg3)',
        border: `1.5px solid ${error ? 'var(--danger)' : 'var(--border)'}`,
        borderRadius: 8,
        color: 'var(--text)',
        fontSize: 15,
        outline: 'none',
        transition: 'border-color .2s',
        ...style,
      }}
      {...rest}
    />
    {error && <p style={{ color: 'var(--danger)', fontSize: 13, marginTop: 4 }}>{error}</p>}
  </div>
));

export default Input;

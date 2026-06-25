import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import GeoBg from '../components/shared/GeoBg';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import client from '../api/client';
import { setToken, setUser } from '../hooks/useAuth';

const PLANS = [
  { id: 'starter', name: 'البداية', price: '2,500', replies: '5,000 رد' },
  { id: 'growth', name: 'النمو', price: '6,000', replies: '15,000 رد', hot: true },
  { id: 'enterprise', name: 'المتجر الكبير', price: '18,000', replies: '50,000 رد' },
];

export default function Auth() {
  const nav = useNavigate();
  const [tab, setTab] = useState<'login' | 'register'>('login');

  return (
    <GeoBg style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ position: 'absolute', top: 20, left: 24, display: 'flex', gap: 8, fontSize: '.8rem', color: 'var(--muted)', fontFamily: "'Cairo',sans-serif" }}>
        <span style={{ color: 'var(--gold)' }}>AR</span> <span>|</span> <span>FR</span>
      </div>

      <Card style={{ maxWidth: 420, width: '100%', padding: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.6rem', fontWeight: 900 }}>
            MARIA <span style={{ color: 'var(--gold)' }}>✦</span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 0, marginBottom: '1.75rem', background: 'var(--bg3)', borderRadius: 8, overflow: 'hidden' }}>
          {(['login', 'register'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                flex: 1,
                padding: '.65rem',
                background: tab === t ? 'var(--gold)' : 'transparent',
                color: tab === t ? 'var(--bg)' : 'var(--muted)',
                border: 'none',
                fontWeight: 700,
                fontSize: '.9rem',
                fontFamily: "'Cairo',sans-serif",
                transition: 'all .2s',
              }}
            >
              {t === 'login' ? 'تسجيل الدخول' : 'إنشاء حساب'}
            </button>
          ))}
        </div>

        {tab === 'login' ? <LoginForm onSuccess={() => nav('/dashboard')} /> : <RegisterForm onSuccess={() => nav('/dashboard')} />}

        <div style={{ textAlign: 'center', fontSize: '.72rem', color: 'var(--faint)', marginTop: 16 }}>
          بالنقر على متابعة، أنت توافق على <a href="#" style={{ color: 'var(--gold)', textDecoration: 'underline' }}>شروط الاستخدام</a>
        </div>
      </Card>
    </GeoBg>
  );
}

function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await client.post('/api/auth/login', { email, password });
      setToken(data.token);
      setUser(data.user);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'البريد الإلكتروني أو كلمة المرور غير صحيحة');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Input label="البريد الإلكتروني" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
      <div style={{ position: 'relative' }}>
        <Input label="كلمة المرور" type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} required error={error} />
        <button type="button" onClick={() => setShowPw(!showPw)} style={{ position: 'absolute', left: 12, top: 40, background: 'none', border: 'none', color: 'var(--muted)', fontSize: '.8rem', cursor: 'pointer' }}>
          {showPw ? 'إخفاء' : 'إظهار'}
        </button>
      </div>
      {error && <p style={{ color: 'var(--danger)', fontSize: 13, marginBottom: 8 }}>{error}</p>}
      <Button type="submit" loading={loading} style={{ width: '100%', marginTop: 4 }}>تسجيل الدخول</Button>
      <div style={{ textAlign: 'center', marginTop: 12 }}>
        <button type="button" style={{ background: 'none', border: 'none', color: 'var(--gold)', fontSize: '.82rem', cursor: 'pointer' }}>نسيت كلمة المرور؟</button>
      </div>
    </form>
  );
}

function RegisterForm({ onSuccess }: { onSuccess: () => void }) {
  const [step, setStep] = useState<'form' | 'payment'>('form');
  const [form, setForm] = useState({ name: '', phone: '', email: '', password: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'satim' | 'baridimob'>('satim');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.name) errs.name = 'الاسم مطلوب';
    if (!/^(05|06|07|09)\d{8}$/.test(form.phone.replace(/\s/g, ''))) errs.phone = 'رقم هاتف غير صحيح (05/06/07/09 XXXXXXXX)';
    if (!form.email.includes('@')) errs.email = 'بريد إلكتروني غير صحيح';
    if (form.password.length < 6) errs.password = 'كلمة المرور 6 أحرف على الأقل';
    if (!selectedPlan) errs.plan = 'اختر باقة';
    return errs;
  };

  const passStrength = (pw: string) => {
    if (pw.length < 6) return 'weak';
    if (pw.length >= 8 && /[A-Z]/.test(pw) && /\d/.test(pw) && /[^A-Za-z0-9]/.test(pw)) return 'strong';
    if (pw.length >= 6) return 'medium';
    return 'weak';
  };

  const strength = passStrength(form.password);
  const strengthColors = { weak: 'var(--danger)', medium: 'var(--gold)', strong: 'var(--success)' };

  const handleRegister = async () => {
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length) return;

    setStep('payment');
  };

  const handlePayment = async () => {
    if (paymentMethod !== 'satim') return;
    setLoading(true);
    try {
      const { data } = await client.post('/api/auth/register', { ...form, plan: selectedPlan });
      const { data: payData } = await client.post('/api/payments/initiate-satim', {
        amount: selectedPlan === 'starter' ? 2500 : selectedPlan === 'growth' ? 6000 : 18000,
        pack_id: selectedPlan,
        user_id: data.user.id,
      });
      window.location.href = payData.payment_url;
    } catch (err: any) {
      setErrors({ form: err.response?.data?.detail || 'فشل إنشاء الحساب' });
      setLoading(false);
    }
  };

  if (step === 'payment') {
    return (
      <div>
        <h3 style={{ textAlign: 'center', marginBottom: 16 }}>اختيار طريقة الدفع</h3>
        <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          <button onClick={() => setPaymentMethod('satim')} style={{ flex: 1, padding: '.7rem', borderRadius: 8, border: paymentMethod === 'satim' ? '1.5px solid var(--gold)' : '1px solid var(--border)', background: paymentMethod === 'satim' ? 'var(--gold-d)' : 'var(--bg3)', fontWeight: 700, color: 'var(--text)' }}>
            CIB / Edahabia
          </button>
          <button onClick={() => setPaymentMethod('baridimob')} style={{ flex: 1, padding: '.7rem', borderRadius: 8, border: paymentMethod === 'baridimob' ? '1.5px solid var(--gold)' : '1px solid var(--border)', background: paymentMethod === 'baridimob' ? 'var(--gold-d)' : 'var(--bg3)', fontWeight: 700, color: 'var(--text)' }}>
            Baridimob
          </button>
        </div>
        {errors.form && <p style={{ color: 'var(--danger)', fontSize: 13, marginBottom: 8, textAlign: 'center' }}>{errors.form}</p>}
        <Button onClick={handlePayment} loading={loading} style={{ width: '100%' }}>
          {loading ? 'جاري تحضير الدفع...' : 'تأكيد الدفع'}
        </Button>
        <button onClick={() => setStep('form')} style={{ display: 'block', margin: '12px auto 0', background: 'none', border: 'none', color: 'var(--muted)', fontSize: '.82rem', cursor: 'pointer' }}>
          رجع
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={e => { e.preventDefault(); handleRegister(); }}>
      <Input label="الاسم الكامل" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} error={errors.name} required />
      <Input label="رقم الهاتف" value={form.phone} onChange={e => setForm(p => ({ ...p, phone: e.target.value }))} placeholder="05XX XXXXXX" error={errors.phone} required />
      <Input label="البريد الإلكتروني" type="email" value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} error={errors.email} required />
      <div style={{ position: 'relative' }}>
        <Input label="كلمة المرور" type="password" value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} error={errors.password} required />
        {form.password && (
          <div style={{ marginTop: -8, marginBottom: 12 }}>
            <div style={{ display: 'flex', gap: 4, marginBottom: 2 }}>
              {['ضعيفة', 'متوسطة', 'قوية'].map((lbl, i) => {
                const levels = ['weak', 'medium', 'strong'];
                const idx = levels.indexOf(strength);
                return <div key={lbl} style={{ flex: 1, height: 3, borderRadius: 2, background: i <= idx ? strengthColors[strength as keyof typeof strengthColors] : 'var(--border)' }} />;
              })}
            </div>
            <span style={{ fontSize: '.72rem', color: strengthColors[strength as keyof typeof strengthColors] }}>
              {strength === 'weak' ? 'ضعيفة' : strength === 'medium' ? 'متوسطة' : 'قوية'}
            </span>
          </div>
        )}
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8, fontWeight: 600, fontSize: 14, color: 'var(--muted)' }}>اختر باقة</label>
        <div style={{ display: 'flex', gap: 8 }}>
          {PLANS.map(p => (
            <button
              key={p.id}
              type="button"
              onClick={() => setSelectedPlan(p.id)}
              style={{
                flex: 1,
                padding: '.65rem .4rem',
                borderRadius: 10,
                border: `1.5px solid ${selectedPlan === p.id ? 'var(--gold)' : 'var(--border)'}`,
                background: selectedPlan === p.id ? 'var(--gold-d)' : 'var(--bg3)',
                textAlign: 'center',
                cursor: 'pointer',
                position: 'relative',
              }}
            >
              {p.hot && <span style={{ position: 'absolute', top: -8, left: '50%', transform: 'translateX(-50%)', background: 'var(--gold)', color: 'var(--bg)', fontSize: '.6rem', fontWeight: 700, padding: '.1rem .5rem', borderRadius: 100 }}>★</span>}
              <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '.75rem', fontWeight: 700, marginBottom: 4 }}>{p.name}</div>
              <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.1rem', fontWeight: 900, color: 'var(--gold)' }}>{p.price}<sub style={{ fontSize: '.65rem', fontWeight: 400, color: 'var(--muted)' }}>دج</sub></div>
              <div style={{ fontSize: '.68rem', color: 'var(--muted)' }}>{p.replies}</div>
              {selectedPlan === p.id && <div style={{ color: 'var(--gold)', fontSize: '.8rem', marginTop: 4 }}>✓</div>}
            </button>
          ))}
        </div>
        {errors.plan && <p style={{ color: 'var(--danger)', fontSize: 13, marginTop: 4 }}>{errors.plan}</p>}
      </div>

      <Button type="submit" style={{ width: '100%' }}>إنشاء حساب</Button>
    </form>
  );
}

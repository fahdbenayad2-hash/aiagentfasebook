import { useState, FormEvent, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, Store, Eye, EyeOff, Check, X, LogIn, UserPlus, Sparkles } from 'lucide-react';
import client from '../api/client';
import ParticlesCanvas from '../animations/ParticlesCanvas';

export default function AuthPage() {
  const [searchParams] = useSearchParams();
  const [isSignUp, setIsSignUp] = useState(searchParams.get('signup') === '1');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [storeName, setStoreName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showConfetti, setShowConfetti] = useState(false);
  const navigate = useNavigate();

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const passwordValid = password.length >= 6;
  const passwordsMatch = password === confirmPassword;
  const canSubmit = isSignUp
    ? emailValid && passwordValid && passwordsMatch && storeName.trim()
    : emailValid && password.length > 0;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (!canSubmit) return;
    setLoading(true);
    try {
      if (isSignUp) {
        await client.post('/api/auth/register', { email, password, name: storeName.trim() });
        setShowConfetti(true);
        setTimeout(() => { setShowConfetti(false); setIsSignUp(false); }, 1500);
      } else {
        const { data } = await client.post('/api/auth/login', { email, password });
        localStorage.setItem('token', data.token);
        if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'حدث خطأ. حاول مرة أخرى.');
    }
    setLoading(false);
  };

  const handleSendTest = async () => {
    if (!emailValid || !passwordValid) return;
    setLoading(true);
    try {
      await client.post('/api/auth/register', { email, password, name: storeName.trim() || 'متجري' });
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 1500);
    } catch {}
    setLoading(false);
  };
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)', position: 'relative', overflow: 'hidden' }}>
      <ParticlesCanvas count={35} />

      {showConfetti && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 100, pointerEvents: 'none', overflow: 'hidden' }}>
          {Array.from({ length: 40 }).map((_, i) => (
            <motion.div
              key={i}
              initial={{ x: Math.random() * window.innerWidth, y: -10, rotate: 0, opacity: 1 }}
              animate={{ y: window.innerHeight + 10, rotate: Math.random() * 720, opacity: 0 }}
              transition={{ duration: 2 + Math.random() * 2, delay: Math.random() * 0.5 }}
              style={{
                position: 'absolute', width: 8, height: 8,
                background: ['var(--gold)', 'var(--gold-m)', '#fff'][i % 3],
                borderRadius: i % 2 === 0 ? '50%' : '2px',
              }}
            />
          ))}
        </div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        style={{
          width: '100%', maxWidth: 440, padding: '2rem', position: 'relative', zIndex: 1,
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.8rem', fontWeight: 900, color: 'var(--text)', marginBottom: '.3rem' }}
          >
            فهد <span style={{ color: 'var(--gold)' }}>✦</span>
          </motion.div>
          <p style={{ color: 'var(--muted)', fontSize: '.85rem' }}>
            {isSignUp ? 'أنشئ حسابك الجديد' : 'تسجيل الدخول إلى لوحة التحكم'}
          </p>
        </div>

        <div style={{
          background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 20, padding: '2rem',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)', backdropFilter: 'blur(20px)',
        }}>
          <div style={{ display: 'flex', gap: 4, marginBottom: '1.5rem', background: 'var(--bg3)', borderRadius: 10, padding: 3 }}>
            {[
              { key: false, label: 'تسجيل الدخول', icon: <LogIn size={15} /> },
              { key: true, label: 'إنشاء حساب', icon: <UserPlus size={15} /> },
            ].map(tab => (
              <button
                key={String(tab.key)}
                onClick={() => { setIsSignUp(tab.key); setError(''); }}
                style={{
                  flex: 1, padding: '.6rem', borderRadius: 8, border: 'none', cursor: 'pointer',
                  background: isSignUp === tab.key ? 'var(--gold-d)' : 'transparent',
                  color: isSignUp === tab.key ? 'var(--gold)' : 'var(--muted)',
                  fontWeight: 700, fontSize: '.85rem', fontFamily: "'Cairo',sans-serif",
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '.5rem',
                  transition: 'all .25s',
                }}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            <motion.form
              key={isSignUp ? 'signup' : 'signin'}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.25 }}
              onSubmit={handleSubmit}
            >
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: '.8rem', color: 'var(--muted)', marginBottom: 4 }}>البريد الإلكتروني</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={16} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }} />
                  <input value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@store.dz" type="email"
                    style={{
                      width: '100%', padding: '12px 12px 12px 40px', borderRadius: 10, border: `1px solid ${email && !emailValid ? 'var(--danger)' : emailValid ? 'var(--b-gold)' : 'var(--border)'}`,
                      background: 'var(--bg3)', color: 'var(--text)', fontSize: '.88rem', outline: 'none', transition: 'all .22s',
                    }}
                  />
                  {email && (
                    <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: emailValid ? 'var(--success)' : 'var(--danger)' }}>
                      {emailValid ? <Check size={16} /> : <X size={16} />}
                    </span>
                  )}
                </div>
              </div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: '.8rem', color: 'var(--muted)', marginBottom: 4 }}>كلمة المرور</label>
                <div style={{ position: 'relative' }}>
                  <Lock size={16} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }} />
                  <input value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" type={showPassword ? 'text' : 'password'}
                    style={{
                      width: '100%', padding: '12px 40px 12px 36px', borderRadius: 10, border: `1px solid ${password && !passwordValid ? 'var(--danger)' : passwordValid ? 'var(--b-gold)' : 'var(--border)'}`,
                      background: 'var(--bg3)', color: 'var(--text)', fontSize: '.88rem', outline: 'none', transition: 'all .22s',
                    }}
                  />
                  <span onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--muted)', cursor: 'pointer', display: 'flex' }}>
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </span>
                  {password && (
                    <span style={{ position: 'absolute', left: 36, top: '50%', transform: 'translateY(-50%)', color: passwordValid ? 'var(--success)' : 'var(--danger)' }}>
                      {passwordValid ? <Check size={16} /> : <X size={16} />}
                    </span>
                  )}
                </div>
              </div>

              {isSignUp && (
                <>
                  <div style={{ marginBottom: 14 }}>
                    <label style={{ display: 'block', fontSize: '.8rem', color: 'var(--muted)', marginBottom: 4 }}>تأكيد كلمة المرور</label>
                    <div style={{ position: 'relative' }}>
                      <Lock size={16} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }} />
                      <input value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="••••••••" type="password"
                        style={{
                          width: '100%', padding: '12px 40px 12px 36px', borderRadius: 10, border: `1px solid ${confirmPassword && !passwordsMatch ? 'var(--danger)' : confirmPassword && passwordsMatch ? 'var(--b-gold)' : 'var(--border)'}`,
                          background: 'var(--bg3)', color: 'var(--text)', fontSize: '.88rem', outline: 'none', transition: 'all .22s',
                        }}
                      />
                      {confirmPassword && (
                        <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: passwordsMatch ? 'var(--success)' : 'var(--danger)' }}>
                          {passwordsMatch ? <Check size={16} /> : <X size={16} />}
                        </span>
                      )}
                    </div>
                  </div>

                  <div style={{ marginBottom: 14 }}>
                    <label style={{ display: 'block', fontSize: '.8rem', color: 'var(--muted)', marginBottom: 4 }}>اسم المتجر</label>
                    <div style={{ position: 'relative' }}>
                      <Store size={16} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }} />
                      <input value={storeName} onChange={e => setStoreName(e.target.value)} placeholder="اسم متجرك" type="text"
                        style={{
                          width: '100%', padding: '12px 40px 12px 12px', borderRadius: 10, border: `1px solid ${storeName ? 'var(--b-gold)' : 'var(--border)'}`,
                          background: 'var(--bg3)', color: 'var(--text)', fontSize: '.88rem', outline: 'none', transition: 'all .22s',
                        }}
                      />
                    </div>
                  </div>
                </>
              )}

              {error && <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 10, padding: '.6rem .9rem', fontSize: '.82rem', color: 'var(--danger)', marginBottom: 14 }}>{error}</div>}

              <button type="submit" disabled={!canSubmit || loading}
                style={{
                  width: '100%', padding: '.75rem', borderRadius: 10, border: 'none',
                  background: canSubmit ? 'var(--gold)' : 'var(--faint)', color: canSubmit ? 'var(--bg)' : 'var(--muted)',
                  fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.95rem',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '.5rem',
                  cursor: canSubmit ? 'pointer' : 'not-allowed', transition: 'all .22s',
                  boxShadow: canSubmit ? '0 4px 16px rgba(232,168,48,.2)' : 'none',
                }}
                onMouseEnter={e => { if (canSubmit) { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 6px 20px rgba(232,168,48,.3)'; } }}
                onMouseLeave={e => { if (canSubmit) { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = '0 4px 16px rgba(232,168,48,.2)'; } }}
              >
                {loading ? (
                  <span style={{ width: 16, height: 16, border: '2px solid var(--bg)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin .6s linear infinite', display: 'inline-block' }} />
                ) : (
                  <>{isSignUp ? 'إنشاء الحساب' : 'تسجيل الدخول'} <Sparkles size={16} /></>
                )}
              </button>
            </motion.form>
          </AnimatePresence>

          {!isSignUp && (
            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
              <a href="#" style={{ color: 'var(--muted)', fontSize: '.8rem', textDecoration: 'none' }}>نسيت كلمة المرور؟</a>
            </div>
          )}

          <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '.72rem', color: 'var(--faint)', lineHeight: 1.6 }}>
            بالنقر على متابعة، أنت توافق على <a href="#" style={{ color: 'var(--gold)', textDecoration: 'none' }}>شروط الاستخدام</a>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

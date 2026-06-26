import { useState, FormEvent } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, AlertTriangle, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import ParticlesCanvas from '../animations/ParticlesCanvas';

export default function DeleteAccount() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/delete-account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw { response: { data: errBody, status: res.status } };
      }
      setDone(true);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'حدث خطأ. حاول مرة أخرى.');
    }
    setLoading(false);
  };

  if (done) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)', position: 'relative', overflow: 'hidden' }}>
        <ParticlesCanvas count={25} />
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}
          style={{ background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 20, padding: '3rem 2rem', maxWidth: 420, width: '100%', textAlign: 'center', position: 'relative', zIndex: 1 }}>
          <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'rgba(220,78,78,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
            <AlertTriangle size={28} color="var(--danger)" />
          </div>
          <h2 style={{ fontFamily: "'Cairo',sans-serif", marginBottom: 8 }}>تم حذف الحساب</h2>
          <p style={{ color: 'var(--muted)', fontSize: '.85rem', marginBottom: 20, lineHeight: 1.7 }}>تم حذف جميع بياناتك بنجاح. نحن آسفون لرؤيتك ترحل.</p>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <button style={{ padding: '.7rem 1.5rem', borderRadius: 10, border: 'none', background: 'var(--gold)', color: 'var(--bg)', fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.9rem', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
              <ArrowLeft size={16} /> العودة للصفحة الرئيسية
            </button>
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)', position: 'relative', overflow: 'hidden' }}>
      <ParticlesCanvas count={30} />
      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        style={{ width: '100%', maxWidth: 420, padding: '2rem', position: 'relative', zIndex: 1 }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'rgba(220,78,78,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
            <AlertTriangle size={24} color="var(--danger)" />
          </div>
          <h2 style={{ fontFamily: "'Cairo',sans-serif", fontSize: '1.3rem', marginBottom: 4 }}>حذف الحساب</h2>
          <p style={{ color: 'var(--muted)', fontSize: '.82rem', lineHeight: 1.7 }}>هذا الإجراء نهائي ولا يمكن التراجع عنه. سيتم حذف جميع بياناتك.</p>
        </div>

        <div style={{ background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 20, padding: '1.75rem', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: 14 }}>
              <label style={{ display: 'block', fontSize: '.8rem', color: 'var(--muted)', marginBottom: 4 }}>البريد الإلكتروني</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }} />
                <input value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@store.dz" type="email" required
                  style={{ width: '100%', padding: '12px 40px 12px 12px', borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg3)', color: 'var(--text)', fontSize: '.88rem', outline: 'none' }} />
              </div>
            </div>

            <div style={{ marginBottom: 18 }}>
              <label style={{ display: 'block', fontSize: '.8rem', color: 'var(--muted)', marginBottom: 4 }}>كلمة المرور</label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }} />
                <input value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" type="password" required
                  style={{ width: '100%', padding: '12px 40px 12px 12px', borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg3)', color: 'var(--text)', fontSize: '.88rem', outline: 'none' }} />
              </div>
            </div>

            {error && <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 10, padding: '.6rem .9rem', fontSize: '.82rem', color: 'var(--danger)', marginBottom: 14 }}>{error}</div>}

            <button type="submit" disabled={loading || !email || !password}
              style={{ width: '100%', padding: '.75rem', borderRadius: 10, border: 'none',
                background: email && password ? 'var(--danger)' : 'var(--faint)',
                color: email && password ? '#fff' : 'var(--muted)',
                fontFamily: "'Cairo',sans-serif", fontWeight: 700, fontSize: '.9rem', cursor: email && password ? 'pointer' : 'not-allowed', transition: 'all .22s' }}>
              {loading ? <span style={{ width: 16, height: 16, border: '2px solid #fff', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin .6s linear infinite', display: 'inline-block' }} /> : 'حذف الحساب نهائياً'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <Link to="/auth" style={{ color: 'var(--muted)', fontSize: '.8rem', textDecoration: 'none' }}>تراجعت؟ العودة لتسجيل الدخول</Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

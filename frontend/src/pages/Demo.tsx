import { useState, useEffect, useRef, FormEvent, useCallback } from 'react';
import GeoBg from '../components/shared/GeoBg';
import PhoneMockup from '../components/shared/PhoneMockup';
import ChatBubble from '../components/shared/ChatBubble';
import client from '../api/client';

const EXAMPLES = ['واش عندكم في L؟', 'بكاش التوصيل لعنابة؟', 'نبغي نطلب'];

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function getSessionId(): string {
  let sid = sessionStorage.getItem('demo_sid');
  if (!sid) {
    sid = crypto.randomUUID();
    sessionStorage.setItem('demo_sid', sid);
  }
  return sid;
}

export default function Demo() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, _setSessionId] = useState(getSessionId);
  const bottomRef = useRef<HTMLDivElement>(null);
  const msgCount = messages.filter(m => m.role === 'user').length;

  useEffect(() => {
    if (!messages.length) {
      const t = setTimeout(() => {
        setMessages([{
          role: 'assistant',
          content: 'السلام! أنا ماريا 👋 وكيلة مبيعاتي\n\nكيفاش نقدر نساعدك اليوم؟',
        }]);
      }, 800);
      return () => clearTimeout(t);
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || loading) return;

    if (msgCount >= 15) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'للمزيد، سجّل حسابك مجاناً ←' }]);
      window.location.href = '/auth';
      return;
    }

    const userMsg: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await client.post('/api/demo/chat', {
        message: text,
        session_id: sessionId,
        history: messages.concat(userMsg),
      });

      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'عذراً، حدث خطأ. حاول مرة أخرى' }]);
    } finally {
      setLoading(false);
    }
  }, [messages, loading, msgCount, sessionId]);

  return (
    <GeoBg style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3rem', alignItems: 'center', maxWidth: 900 }}>
        <div>
          <div style={{ fontFamily: "'Cairo',sans-serif", fontSize: '2.8rem', fontWeight: 900, lineHeight: 1.12, marginBottom: '1rem' }}>
            جرّب <span style={{ color: 'var(--gold)' }}>ماريا</span> الآن
          </div>
          <p style={{ fontSize: '1rem', color: 'var(--muted)', marginBottom: '2rem', lineHeight: 1.85 }}>
            محادثة حقيقية بالدارجة الجزائرية — اسألها عن أي منتج
          </p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {[
              { emoji: '🗣️', label: 'دارجة جزائرية' },
              { emoji: '📦', label: 'تسجيل طلبات' },
              { emoji: '🚚', label: 'Noest' },
              { emoji: '⏰', label: '24/7' },
            ].map(f => (
              <div key={f.label} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '.45rem .85rem', borderRadius: 100, background: 'var(--gold-d)', border: '1px solid var(--b-gold)', fontSize: '.78rem', color: 'var(--gold)', fontFamily: "'Cairo',sans-serif", fontWeight: 600 }}>
                {f.emoji} {f.label}
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <PhoneMockup>
              {messages.map((m, i) => (
                <ChatBubble key={i} role={m.role} content={m.content} />
              ))}
              {loading && (
                <div style={{ display: 'flex', gap: 4, alignItems: 'center', padding: '.55rem .85rem', background: '#fff', borderRadius: '16px 16px 16px 3px', width: 'fit-content', opacity: 1 }}>
                  {[0, 1, 2].map(i => (
                    <div
                      key={i}
                      style={{
                        width: 6, height: 6, borderRadius: '50%', background: '#bbb',
                        animation: 'td 1.2s infinite',
                        animationDelay: `${i * .2}s`,
                      }}
                    />
                  ))}
                </div>
              )}
              <div ref={bottomRef} />
            </PhoneMockup>

            <div style={{ width: 290, marginTop: 12 }}>
              <form onSubmit={e => { e.preventDefault(); sendMessage(input); }} style={{ display: 'flex', gap: 6 }}>
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="اكتب رسالة..."
                  disabled={loading}
                  style={{
                    flex: 1, padding: '10px 14px', borderRadius: 8, border: '1px solid var(--border)',
                    background: 'var(--bg3)', color: 'var(--text)', fontSize: '.85rem', outline: 'none',
                    fontFamily: "'Tajawal',sans-serif",
                  }}
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  style={{
                    padding: '10px 16px', borderRadius: 8, border: 'none',
                    background: loading ? 'var(--faint)' : 'var(--gold)',
                    color: loading ? 'var(--muted)' : 'var(--bg)',
                    fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
                    fontFamily: "'Cairo',sans-serif",
                  }}
                >
                  إرسال
                </button>
              </form>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8, marginTop: 16, flexWrap: 'wrap', justifyContent: 'center' }}>
            {EXAMPLES.map(ex => (
              <button
                key={ex}
                onClick={() => sendMessage(ex)}
                disabled={loading}
                style={{
                  padding: '.4rem .85rem', borderRadius: 100, border: '1px solid var(--border)',
                  background: 'transparent', color: 'var(--muted)', fontSize: '.78rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontFamily: "'Tajawal',sans-serif",
                  transition: 'all .2s',
                }}
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>
    </GeoBg>
  );
}

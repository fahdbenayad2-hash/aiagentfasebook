import { useState, useEffect, useRef, FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import client from '../../api/client';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Skeleton from '../../components/ui/Skeleton';
import ChatBubble from '../../components/shared/ChatBubble';
import useWebSocket from '../../hooks/useWebSocket';
import ScrollReveal from '../../components/landing/ScrollReveal';

interface Conv {
  id: number;
  customer_name: string;
  last_message: string;
  time_ago: string;
  status: string;
  unread: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const statusColors: Record<string, 'green' | 'gold' | 'terra' | 'muted'> = {
  'نشط': 'green', 'مريا': 'gold', 'يدوي': 'terra', 'مغلق': 'muted',
};

export default function Conversations() {
  const [params, setParams] = useSearchParams();
  const convId = params.get('id');
  const [convs, setConvs] = useState<Conv[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [manualMode, setManualMode] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'manual' | 'closed'>('all');
  const bottomRef = useRef<HTMLDivElement>(null);
  const wsMessages = useWebSocket(convId);

  const filtered = convs.filter(c => {
    if (filter === 'active' && c.status !== 'نشط' && c.status !== 'مريا') return false;
    if (filter === 'manual' && c.status !== 'يدوي') return false;
    if (filter === 'closed' && c.status !== 'مغلق') return false;
    if (search && !c.customer_name.includes(search)) return false;
    return true;
  });

  useEffect(() => {
    const controller = new AbortController();
    client.get('/api/conversations', { signal: controller.signal })
      .then(r => setConvs(r.data))
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Conversations list]:', err); })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!convId) return;
    const controller = new AbortController();
    client.get(`/api/conversations/${convId}/messages`, { signal: controller.signal })
      .then(r => setMessages(r.data))
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Conversations msgs]:', err); });
    client.get(`/api/conversations/${convId}`, { signal: controller.signal })
      .then(r => setManualMode(r.data.manual || false))
      .catch((err: any) => { if (err.name !== 'CanceledError') console.error('[Conversations mode]:', err); });
    return () => controller.abort();
  }, [convId]);

  useEffect(() => {
    if (wsMessages.messages.length) {
      setMessages(prev => [...prev, ...wsMessages.messages.slice(prev.length ? 0 : 0)]);
    }
  }, [wsMessages.messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleManual = async () => {
    if (!convId) return;
    const newMode = !manualMode;
    try {
      await client.patch(`/api/conversations/${convId}/mode`, { manual: newMode });
      setManualMode(newMode);
    } catch {}
  };

  const sendManualReply = async (e: FormEvent) => {
    e.preventDefault();
    if (!convId || !replyText.trim()) return;
    try {
      await client.post(`/api/conversations/${convId}/manual-reply`, { message: replyText });
      setMessages(prev => [...prev, { role: 'user', content: replyText, timestamp: new Date().toISOString() }]);
      setReplyText('');
    } catch {}
  };

  const selectConv = (id: number) => {
    setParams({ id: id.toString() });
  };

  if (!convId) {
    return (
      <div className="conv-layout" style={{ display: 'flex', height: 'calc(100vh - 120px)' }}>
        <LeftPanel loading={loading} convs={filtered} selected={null} onSelect={selectConv} search={search} onSearch={setSearch} filter={filter} onFilter={setFilter} />
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>
          اختر محادثة لعرضها
        </div>
      </div>
    );
  }

  return (
    <div className="conv-layout" style={{ display: 'flex', height: 'calc(100vh - 120px)' }}>
      <LeftPanel loading={loading} convs={filtered} selected={parseInt(convId)} onSelect={selectConv} search={search} onSearch={setSearch} filter={filter} onFilter={setFilter} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--bg3)', borderRadius: 16, overflow: 'hidden' }}>
        <div style={{ padding: '1rem', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontWeight: 700, fontSize: '.9rem' }}>{convs.find(c => c.id === parseInt(convId))?.customer_name || 'محادثة'}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: '.78rem', color: manualMode ? 'var(--danger)' : 'var(--muted)' }}>
              {manualMode ? 'أنت تتحكم الآن' : 'ماريا تردّ تلقائياً 🤖'}
            </span>
            <button
              onClick={toggleManual}
              style={{
                width: 44, height: 24, borderRadius: 12, border: 'none', cursor: 'pointer',
                background: manualMode ? 'var(--danger)' : 'var(--faint)',
                position: 'relative', transition: 'background .2s',
              }}
            >
              <div style={{
                width: 18, height: 18, borderRadius: '50%', background: '#fff',
                position: 'absolute', top: 3, right: manualMode ? 3 : 23,
                transition: 'right .2s',
              }} />
            </button>
          </div>
        </div>

        <div style={{ flex: 1, padding: '1rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '.65rem' }}>
          {messages.map((m, i) => (
            <ChatBubble key={i} role={m.role} content={m.content} timestamp={m.timestamp} />
          ))}
          <div ref={bottomRef} />
        </div>

        {manualMode && (
          <form onSubmit={sendManualReply} style={{ padding: '1rem', borderTop: '1px solid var(--border)', display: 'flex', gap: 8 }}>
            <input
              value={replyText}
              onChange={e => setReplyText(e.target.value)}
              placeholder="اكتب رداً..."
              style={{
                flex: 1, padding: '10px 14px', borderRadius: 8, border: '1px solid var(--border)',
                background: 'var(--bg)', color: 'var(--text)', fontSize: '.85rem', outline: 'none',
              }}
            />
            <button
              type="submit"
              style={{
                padding: '10px 20px', borderRadius: 8, border: 'none',
                background: 'var(--gold)', color: 'var(--bg)', fontWeight: 700, cursor: 'pointer',
              }}
            >
              إرسال
            </button>
          </form>
        )}
        {!manualMode && (
          <div style={{ padding: '1rem', borderTop: '1px solid var(--border)', textAlign: 'center', fontSize: '.82rem', color: 'var(--muted)' }}>
            ماريا تردّ تلقائياً 🤖 — فعّل الوضع اليدوي للتحكم
          </div>
        )}
      </div>
    </div>
  );
}

function LeftPanel({
  loading, convs, selected, onSelect, search, onSearch, filter, onFilter,
}: {
  loading: boolean; convs: Conv[]; selected: number | null; onSelect: (id: number) => void;
  search: string; onSearch: (s: string) => void;
  filter: string; onFilter: (f: any) => void;
}) {
  return (
    <div className="conv-list" style={{ width: 360, marginLeft: 16, display: 'flex', flexDirection: 'column' }}>
      <input
        value={search}
        onChange={e => onSearch(e.target.value)}
        placeholder="بحث بالاسم..."
        style={{
          width: '100%', padding: '10px 14px', borderRadius: 8, border: '1px solid var(--border)',
          background: 'var(--bg3)', color: 'var(--text)', fontSize: '.85rem', outline: 'none',
          marginBottom: 12,
        }}
      />
      <div style={{ display: 'flex', gap: 4, marginBottom: 12, flexWrap: 'wrap' }}>
        {[
          { key: 'all', label: 'الكل' },
          { key: 'active', label: 'نشط' },
          { key: 'manual', label: 'يدوي' },
          { key: 'closed', label: 'مغلق' },
        ].map(f => (
          <button
            key={f.key}
            onClick={() => onFilter(f.key)}
            style={{
              padding: '.35rem .7rem', borderRadius: 6, border: '1px solid var(--border)',
              background: filter === f.key ? 'var(--gold-d)' : 'transparent',
              color: filter === f.key ? 'var(--gold)' : 'var(--muted)',
              fontWeight: 600, fontSize: '.78rem', cursor: 'pointer',
              fontFamily: "'Cairo',sans-serif",
            }}
          >
            {f.label}
          </button>
        ))}
      </div>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {loading && [1,2,3,4,5].map(i => <Skeleton key={i} width="100%" height={60} borderRadius={8} style={{marginBottom:8}} />)}
        {convs.map(c => (
          <div
            key={c.id}
            onClick={() => onSelect(c.id)}
            style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
              borderRadius: 10, cursor: 'pointer',
              background: selected === c.id ? 'var(--gold-d)' : 'transparent',
              border: selected === c.id ? '1px solid var(--b-gold)' : '1px solid transparent',
              marginBottom: 4, transition: 'all .15s',
            }}
          >
            <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--gold-d)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Cairo',sans-serif", fontWeight: 700, color: 'var(--gold)', fontSize: '.85rem', flexShrink: 0 }}>
              {(c.customer_name || '?')[0]}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: '.85rem' }}>{c.customer_name}</span>
                <span style={{ fontSize: '.7rem', color: 'var(--faint)' }}>{c.time_ago}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '.75rem', color: 'var(--muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 180 }}>{c.last_message}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Badge variant="default">{c.status}</Badge>
                  {c.unread > 0 && (
                    <span className="num" style={{ width: 18, height: 18, borderRadius: '50%', background: 'var(--gold)', color: 'var(--bg)', fontSize: '.65rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {c.unread}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

interface Props {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export default function ChatBubble({ role, content, timestamp }: Props) {
  const isUser = role === 'user';

  return (
    <div
      style={{
        maxWidth: '88%',
        padding: '.55rem .85rem',
        borderRadius: 16,
        fontSize: '.82rem',
        lineHeight: 1.6,
        alignSelf: isUser ? 'flex-end' : 'flex-start',
        background: isUser ? '#1877F2' : '#fff',
        color: isUser ? '#fff' : '#111',
        borderBottomRightRadius: isUser ? 3 : 16,
        borderBottomLeftRadius: isUser ? 16 : 3,
        wordBreak: 'break-word',
        whiteSpace: 'pre-line',
      }}
    >
      {content}
      {timestamp && (
        <div
          style={{
            fontSize: '.65rem',
            marginTop: 4,
            opacity: .6,
            textAlign: isUser ? 'left' : 'right',
          }}
        >
          {new Date(timestamp).toLocaleTimeString('ar-DZ', { hour: '2-digit', minute: '2-digit' })}
        </div>
      )}
    </div>
  );
}

import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Send, Bot, Trash2, Loader2 } from 'lucide-react'
import useChatStore from '../../store/useChatStore'
import VigilXFormattedResponse from '../../components/chat/VigilXFormattedResponse'

const STARTERS = [
  'Who are the top suspects in the narcotics case?',
  'Show criminal network activity in Harbor district',
  'What are the trends in violent crime this month?',
]

export default function ChatV1() {
  const { v1Messages, v1Loading, sendV1Message, clearV1 } = useChatStore()
  const [input, setInput] = useState('')
  const endRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [v1Messages, v1Loading])

  const send = () => {
    const q = input.trim()
    if (!q || v1Loading) return
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = '40px'
    sendV1Message(q)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  const handleInput = (e) => {
    setInput(e.target.value)
    const ta = textareaRef.current
    if (ta) {
      ta.style.height = '40px'
      ta.style.height = Math.min(ta.scrollHeight, 120) + 'px'
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 52px - 48px - 80px)',
        minHeight: 440,
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 10,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 16px',
          height: 48,
          borderBottom: '1px solid var(--border-subtle)',
          flexShrink: 0,
          background: 'var(--bg-tertiary)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 7,
              background: 'rgba(0,212,255,0.08)',
              border: '1px solid rgba(0,212,255,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Bot size={13} style={{ color: 'var(--accent-cyan)' }} />
          </div>
          <div>
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>VigilX V1</span>
            <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 1 }}>Standard LLM · Conversational</p>
          </div>
        </div>

        <button
          onClick={clearV1}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            padding: '5px 10px',
            borderRadius: 6,
            fontSize: 12,
            color: 'var(--text-secondary)',
            background: 'transparent',
            border: '1px solid var(--border-active)',
            cursor: 'pointer',
            transition: 'all 0.15s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#F03E3E'
            e.currentTarget.style.borderColor = 'rgba(240,62,62,0.3)'
            e.currentTarget.style.background = 'rgba(240,62,62,0.05)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--text-secondary)'
            e.currentTarget.style.borderColor = 'var(--border-active)'
            e.currentTarget.style.background = 'transparent'
          }}
        >
          <Trash2 size={12} />
          Clear
        </button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px 20px 8px',
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
        }}
      >
        {/* Empty state */}
        {v1Messages.length === 0 && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              flex: 1,
              textAlign: 'center',
              padding: '32px 16px',
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: 10,
                background: 'rgba(0,212,255,0.07)',
                border: '1px solid rgba(0,212,255,0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: 14,
              }}
            >
              <Bot size={22} style={{ color: 'var(--accent-cyan)' }} />
            </div>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 5 }}>
              VigilX V1 Ready
            </h3>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 20, lineHeight: 1.6 }}>
              Standard LLM interface. Ask anything about your cases.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, justifyContent: 'center', maxWidth: 420 }}>
              {STARTERS.map((s) => (
                <button
                  key={s}
                  onClick={() => setInput(s)}
                  style={{
                    padding: '7px 12px',
                    borderRadius: 6,
                    fontSize: 12,
                    color: 'var(--text-secondary)',
                    background: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-subtle)',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                    lineHeight: 1.4,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = 'var(--text-primary)'
                    e.currentTarget.style.borderColor = 'var(--border-active)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = 'var(--text-secondary)'
                    e.currentTarget.style.borderColor = 'var(--border-subtle)'
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message thread */}
        {v1Messages.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.18 }}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: m.role === 'user' ? 'flex-end' : 'flex-start',
              gap: 4,
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                flexDirection: m.role === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <div
                style={{
                  width: 22,
                  height: 22,
                  borderRadius: 5,
                  background: m.role === 'user'
                    ? 'linear-gradient(135deg, #A855F7, #7C3AED)'
                    : 'rgba(0,212,255,0.1)',
                  border: m.role === 'user' ? 'none' : '1px solid rgba(0,212,255,0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {m.role === 'user'
                  ? <span style={{ fontSize: 9, fontWeight: 700, color: '#fff' }}>OF</span>
                  : <Bot size={11} style={{ color: 'var(--accent-cyan)' }} />
                }
              </div>
              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>
                {m.role === 'user' ? 'You' : 'VigilX V1'}
              </span>
            </div>
            {m.role === 'user'
              ? <div className="chat-bubble-user">{m.text}</div>
              : <VigilXFormattedResponse text={m.text} timestamp={m.ts} onRegenerate={() => sendV1Message(v1Messages[i - 1]?.text || m.text)} />
            }
          </motion.div>
        ))}

        {/* Loading */}
        {v1Loading && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '8px 12px',
              borderRadius: 7,
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              width: 'fit-content',
            }}
          >
            <Loader2 size={12} style={{ color: 'var(--accent-cyan)', animation: 'spin 1s linear infinite' }} />
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Thinking…</span>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* Input bar */}
      <div
        style={{
          padding: '12px 16px',
          borderTop: '1px solid var(--border-subtle)',
          flexShrink: 0,
          background: 'var(--bg-tertiary)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-end',
            gap: 8,
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-active)',
            borderRadius: 9,
            padding: '6px 6px 6px 14px',
            transition: 'border-color 0.15s, box-shadow 0.15s',
          }}
          onFocusCapture={(e) => {
            e.currentTarget.style.borderColor = 'rgba(0,212,255,0.4)'
            e.currentTarget.style.boxShadow = '0 0 0 3px rgba(0,212,255,0.06)'
          }}
          onBlurCapture={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-active)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          <textarea
            ref={textareaRef}
            id="v1-chat-input"
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask the AI anything…"
            rows={1}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              resize: 'none',
              fontSize: 13,
              color: 'var(--text-primary)',
              lineHeight: 1.5,
              height: 40,
              minHeight: 40,
              maxHeight: 120,
              paddingTop: 10,
              fontFamily: 'inherit',
              overflowY: 'auto',
            }}
          />
          <button
            id="v1-send-btn"
            onClick={send}
            disabled={!input.trim() || v1Loading}
            style={{
              width: 34,
              height: 34,
              borderRadius: 7,
              background: input.trim() && !v1Loading ? 'var(--accent-cyan)' : 'var(--bg-elevated)',
              border: 'none',
              cursor: input.trim() && !v1Loading ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              transition: 'all 0.15s',
              opacity: input.trim() && !v1Loading ? 1 : 0.4,
            }}
          >
            {v1Loading
              ? <Loader2 size={14} style={{ color: '#000', animation: 'spin 1s linear infinite' }} />
              : <Send size={14} style={{ color: input.trim() ? '#000' : 'var(--text-secondary)' }} />
            }
          </button>
        </div>
      </div>
    </div>
  )
}

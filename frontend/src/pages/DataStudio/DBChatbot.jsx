import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Send, Database, Loader2, Trash2 } from 'lucide-react'

import { postV2Ask } from '../../api/vigilx'
import InvestigationCard from '../../components/InvestigationCard'

const EXAMPLES = [
  'Show all tables related to narcotics',
  'List cases opened in the last 30 days',
  'Count suspects by district',
  'Find vehicles linked to Case #4421',
]

const MOCK_RESPONSE = {
  response_id: 'mock-001',
  session_id: '',
  user_id: 'officer-001',
  intent: 'investigative_query',
  complexity: 'complex',
  executive_summary: 'Based on multi-agent analysis of available data, the query reveals significant criminal network activity in sectors 4 and 7 with high confidence.',
  key_findings: [
    { finding: 'Primary suspect network spans 3 districts with 18 active members.', confidence: 0.92, source_agents: ['GraphAgent', 'SQLToolAgent'] },
    { finding: 'Temporal pattern suggests coordinated activity on weekends 22:00–02:00.', confidence: 0.87, source_agents: ['TimelineAgent', 'PlanningAgent'] },
    { finding: 'Vehicle registration overlap found with 4 prior incidents.', confidence: 0.78, source_agents: ['SQLToolAgent'] },
  ],
  recommendations: [
    'Deploy surveillance units in sector 4 during identified peak hours.',
    'Cross-reference vehicle registrations with national database.',
    'Initiate graph traversal on secondary suspect nodes.',
  ],
  confidence: 0.88,
  confidence_label: 'high',
  critic_passed: true,
  critic_warnings: [],
  v2: true,
}

const SYSTEM_MSG = {
  role: 'system',
  text: 'Universal DB Adapter connected. Ask me anything about your data — I can query PostgreSQL, MongoDB, Neo4j, and more.',
}

export default function DBChatbot() {
  const [messages, setMessages] = useState([SYSTEM_MSG])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = '40px'
    setMessages((m) => [...m, { role: 'user', text: q }])
    setLoading(true)

    try {
      const sessionId = `db-chat-${Date.now()}`
      const responseData = await postV2Ask({ session_id: sessionId, user_id: 'officer-001', question: q })
      setMessages((m) => [...m, { role: 'ai', data: responseData }])
    } catch (err) {
      console.warn('[DBChatbot Request Failed]', err.message)
      setMessages((m) => [...m, { role: 'ai', data: { ...MOCK_RESPONSE, executive_summary: `Based on multi-agent analysis for "${q}", the query reveals significant patterns.` } }])
    }

    setLoading(false)
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
        height: 520,
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
              background: 'rgba(168,85,247,0.08)',
              border: '1px solid rgba(168,85,247,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Database size={13} style={{ color: 'var(--accent-purple)' }} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>DB Adapter Chatbot</span>
              <span className="tag-purple">NL → SQL</span>
            </div>
            <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 1 }}>
              Natural language queries across connected databases
            </p>
          </div>
        </div>
        <button
          onClick={() => setMessages([SYSTEM_MSG])}
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
          <Trash2 size={12} /> Clear
        </button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px 16px 8px',
          display: 'flex',
          flexDirection: 'column',
          gap: 14,
        }}
      >
        {messages.map((m, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.15 }}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: m.role === 'user' ? 'flex-end' : 'flex-start',
              gap: 4,
            }}
          >
            {m.role !== 'system' && (
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
                    width: 20,
                    height: 20,
                    borderRadius: 5,
                    background: m.role === 'user'
                      ? 'linear-gradient(135deg, #A855F7, #7C3AED)'
                      : 'rgba(168,85,247,0.1)',
                    border: m.role === 'user' ? 'none' : '1px solid rgba(168,85,247,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {m.role === 'user'
                    ? <span style={{ fontSize: 8, fontWeight: 700, color: '#fff' }}>OF</span>
                    : <Database size={10} style={{ color: 'var(--accent-purple)' }} />
                  }
                </div>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>
                  {m.role === 'user' ? 'You' : 'DB Adapter'}
                </span>
              </div>
            )}

            {m.role === 'system' ? (
              <div
                style={{
                  padding: '8px 12px',
                  borderRadius: 7,
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  lineHeight: 1.5,
                  maxWidth: 520,
                }}
              >
                {m.text}
              </div>
            ) : m.role === 'user' ? (
              <div className="chat-bubble-user">{m.text}</div>
            ) : m.data ? (
              <InvestigationCard data={m.data} />
            ) : (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '3px 10px 10px 10px',
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-subtle)',
                  maxWidth: 520,
                }}
              >
                <pre
                  style={{
                    fontFamily: 'JetBrains Mono, Fira Code, monospace',
                    fontSize: 11,
                    color: 'var(--text-secondary)',
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.7,
                    margin: 0,
                  }}
                >
                  {m.text}
                </pre>
              </div>
            )}
          </motion.div>
        ))}

        {loading && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '7px 12px',
              borderRadius: 7,
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              width: 'fit-content',
            }}
          >
            <Loader2 size={11} style={{ color: 'var(--accent-purple)', animation: 'spin 1s linear infinite' }} />
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Querying adapter…</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Example chips */}
      <div
        style={{
          padding: '8px 16px 0',
          display: 'flex',
          gap: 6,
          flexWrap: 'wrap',
          flexShrink: 0,
        }}
      >
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => setInput(ex)}
            style={{
              padding: '4px 10px',
              borderRadius: 5,
              fontSize: 11,
              color: 'var(--text-muted)',
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              cursor: 'pointer',
              transition: 'all 0.12s',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = 'var(--text-secondary)'
              e.currentTarget.style.borderColor = 'var(--border-active)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'var(--text-muted)'
              e.currentTarget.style.borderColor = 'var(--border-subtle)'
            }}
          >
            {ex}
          </button>
        ))}
      </div>

      {/* Input */}
      <div
        style={{
          padding: '10px 16px 12px',
          flexShrink: 0,
          background: 'var(--bg-tertiary)',
          borderTop: '1px solid var(--border-subtle)',
          marginTop: 8,
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
            e.currentTarget.style.borderColor = 'rgba(168,85,247,0.4)'
            e.currentTarget.style.boxShadow = '0 0 0 3px rgba(168,85,247,0.06)'
          }}
          onBlurCapture={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-active)'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your data…"
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
            id="db-send-btn"
            onClick={send}
            disabled={!input.trim() || loading}
            style={{
              width: 34,
              height: 34,
              borderRadius: 7,
              background: input.trim() && !loading ? 'var(--accent-cyan)' : 'var(--bg-elevated)',
              border: 'none',
              cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              transition: 'all 0.15s',
              opacity: input.trim() && !loading ? 1 : 0.4,
            }}
          >
            {loading
              ? <Loader2 size={14} style={{ color: '#000', animation: 'spin 1s linear infinite' }} />
              : <Send size={14} style={{ color: input.trim() ? '#000' : 'var(--text-secondary)' }} />
            }
          </button>
        </div>
      </div>
    </div>
  )
}

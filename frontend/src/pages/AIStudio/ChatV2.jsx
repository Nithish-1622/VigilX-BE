import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Trash2, CheckCircle2, Loader2, TrendingUp, Shield, Zap, ChevronDown, ChevronUp, Brain } from 'lucide-react'
import useChatStore from '../../store/useChatStore'

const SUGGESTIONS = [
  { cat: 'Narcotics', q: 'Identify suspect networks and narcotics distribution hotspots in Harbor District linked to vehicle ZX-7742-B.', tag: 'Graph+Geo' },
  { cat: 'Financial Intel', q: 'Trace financial laundering transactions exceeding $50k across accounts linked to Carlos R.', tag: 'SQL+RAG' },
  { cat: 'Timeline', q: 'Map the chronological timeline of incidents and phone calls for Case #4421 over Q3 2026.', tag: 'Timeline' },
]

// Agent node layout for SVG DAG (x,y as fraction of SVG width/height)
const AGENTS = [
  { id: 'PlanningAgent',     label: 'Planning',    x: 0.5,  y: 0.10, color: '#8B5CF6' },
  { id: 'DataRouterAgent',   label: 'Router',      x: 0.5,  y: 0.28, color: '#00C8F0' },
  { id: 'SQLToolAgent',      label: 'SQL',         x: 0.2,  y: 0.50, color: '#00C8F0' },
  { id: 'GraphAgent',        label: 'Graph',       x: 0.5,  y: 0.50, color: '#8B5CF6' },
  { id: 'TimelineAgent',     label: 'Timeline',    x: 0.8,  y: 0.50, color: '#D97706' },
  { id: 'CriticAgent',       label: 'Critic',      x: 0.5,  y: 0.72, color: '#E53E3E' },
  { id: 'SynthesisAgent',    label: 'Synthesis',   x: 0.5,  y: 0.90, color: '#16A34A' },
]

const EDGES = [
  ['PlanningAgent',   'DataRouterAgent'],
  ['DataRouterAgent', 'SQLToolAgent'],
  ['DataRouterAgent', 'GraphAgent'],
  ['DataRouterAgent', 'TimelineAgent'],
  ['SQLToolAgent',    'CriticAgent'],
  ['GraphAgent',      'CriticAgent'],
  ['TimelineAgent',   'CriticAgent'],
  ['CriticAgent',     'SynthesisAgent'],
]

function PipelineDAG({ pipeline }) {
  const W = 320, H = 320
  const nodeMap = Object.fromEntries(pipeline.map(p => [p.name, p.status]))

  const nodePos = (agent) => ({
    x: agent.x * W,
    y: agent.y * H,
  })

  const edgePaths = EDGES.map(([a, b]) => {
    const from = AGENTS.find(n => n.id === a)
    const to   = AGENTS.find(n => n.id === b)
    if (!from || !to) return null
    const p1 = nodePos(from), p2 = nodePos(to)
    const mx = (p1.x + p2.x) / 2
    const d = `M ${p1.x} ${p1.y} C ${mx} ${p1.y}, ${mx} ${p2.y}, ${p2.x} ${p2.y}`
    const toStatus = nodeMap[b] || 'pending'
    const fromStatus = nodeMap[a] || 'pending'
    const isActive = fromStatus === 'active' || (fromStatus === 'done' && toStatus === 'active')
    return { d, a, b, isActive, fromStatus }
  }).filter(Boolean)

  return (
    <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-dim)', background: 'var(--bg-panel)', flexShrink: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.1em', color: 'var(--cyan)' }}>
          ▶ PIPELINE EXECUTING
        </span>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--text-tertiary)' }}>#VX-{Date.now().toString().slice(-4)}</span>
      </div>
      <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
        {/* SVG DAG */}
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ flexShrink: 0 }}>
          <defs>
            <marker id="arr" markerWidth="4" markerHeight="4" refX="2" refY="2" orient="auto">
              <path d="M 0 0 L 4 2 L 0 4 z" fill="#2D3A50" />
            </marker>
          </defs>

          {/* Static edge tracks */}
          {edgePaths.map(({ d, a, b }) => (
            <path key={`${a}-${b}`} d={d} fill="none" stroke="var(--border-base)" strokeWidth="1" markerEnd="url(#arr)" />
          ))}

          {/* Traveling pulse on active edges */}
          {edgePaths.filter(e => e.isActive).map(({ d, a, b }) => (
            <path
              key={`pulse-${a}-${b}`} d={d} fill="none"
              stroke="var(--cyan)" strokeWidth="1.5"
              strokeDasharray="8 92" strokeDashoffset="100"
              style={{ animation: 'travelPulse 1.2s linear infinite' }}
            />
          ))}

          {/* Nodes */}
          {AGENTS.map((agent) => {
            const { x, y } = nodePos(agent)
            const status = nodeMap[agent.id] || 'pending'
            const isActive = status === 'active'
            const isDone   = status === 'done'
            const color = isDone ? '#16A34A' : isActive ? agent.color : '#2D3A50'
            return (
              <g key={agent.id} transform={`translate(${x},${y})`}>
                {isActive && (
                  <circle r="14" fill="none" stroke={agent.color} strokeWidth="1" opacity="0.25"
                    style={{ animation: 'agentPulse 1.4s ease-in-out infinite' }} />
                )}
                <circle r="9" fill="var(--bg-row)" stroke={color} strokeWidth={isActive ? 1.5 : 1} />
                {isDone && (
                  <text textAnchor="middle" dominantBaseline="central" fontSize="8" fill="#16A34A">✓</text>
                )}
                {isActive && (
                  <circle r="3" fill={agent.color} style={{ animation: 'pulseDot 1s ease-in-out infinite' }} />
                )}
                <text
                  y="16" textAnchor="middle" fontSize="8"
                  fontFamily="var(--mono)" letterSpacing="0.04em"
                  fill={isActive ? 'var(--text-primary)' : isDone ? 'var(--text-secondary)' : 'var(--text-tertiary)'}
                >
                  {agent.label}
                </text>
              </g>
            )
          })}
        </svg>

        {/* Stage list */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 3 }}>
          {pipeline.map((stage) => {
            const status = stage.status
            const agent = AGENTS.find(a => a.id === stage.name)
            const color = status === 'done' ? '#16A34A' : status === 'active' ? (agent?.color || 'var(--cyan)') : 'var(--text-tertiary)'
            return (
              <div key={stage.name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color, minWidth: 64, letterSpacing: '0.02em' }}>
                  {status === 'done' ? '✓' : status === 'active' ? '▶' : '·'} {stage.name.replace('Agent', '')}
                </span>
                {status === 'active' && (
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>
                    executing…
                  </span>
                )}
                {status === 'done' && (
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--green)' }}>
                    {(Math.random() * 0.8 + 0.2).toFixed(2)}s
                  </span>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

import InvestigationCard from '../../components/InvestigationCard'



export default function ChatV2() {
  const { v2Messages, v2Loading, v2Pipeline, sendV2Message, clearV2 } = useChatStore()
  const [input, setInput] = useState('')
  const endRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [v2Messages, v2Loading, v2Pipeline])

  const send = () => {
    const q = input.trim()
    if (!q || v2Loading) return
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = '40px'
    sendV2Message(q)
  }

  const handleKeyDown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }

  const handleInput = (e) => {
    setInput(e.target.value)
    const ta = textareaRef.current
    if (ta) { ta.style.height = '40px'; ta.style.height = Math.min(ta.scrollHeight, 120) + 'px' }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 52px - 48px - 80px)', minHeight: 480, background: 'var(--bg-panel)', border: '1px solid var(--border-dim)', borderRadius: 4, overflow: 'hidden' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 14px', height: 44, borderBottom: '1px solid var(--border-dim)', flexShrink: 0, background: 'var(--bg-row)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Zap size={12} style={{ color: 'var(--cyan)' }} />
          <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>VigilX CORE AI</span>
          <span className="tag-cyan">Multi-Agent V2</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>7 agents · DAG v2.0</span>
        </div>
        <button onClick={clearV2} className="btn-danger" style={{ padding: '4px 10px', fontSize: 11 }}>
          <Trash2 size={11} /> Clear
        </button>
      </div>

      {/* Pipeline DAG — shown while loading */}
      <AnimatePresence>
        {v2Loading && v2Pipeline.length > 0 && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }} style={{ flexShrink: 0, overflow: 'hidden' }}>
            <PipelineDAG pipeline={v2Pipeline} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 16px 8px', display: 'flex', flexDirection: 'column', gap: 14 }}>

        {v2Messages.length === 0 && (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '32px 16px' }}>
            <Brain size={28} style={{ color: 'var(--text-tertiary)', marginBottom: 14 }} />
            <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>Multi-Agent Intelligence Engine</p>
            <p style={{ fontSize: 11, color: 'var(--text-tertiary)', maxWidth: 360, lineHeight: 1.6, marginBottom: 20 }}>
              Routes queries across 7 specialized agents — SQL, Graph, Geo, Timeline, Critic.
            </p>
            <div style={{ width: '100%', maxWidth: 520, display: 'flex', flexDirection: 'column', gap: 4 }}>
              {SUGGESTIONS.map((s) => (
                <button key={s.q} onClick={() => setInput(s.q)} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '9px 12px', background: 'var(--bg-row)', border: '1px solid var(--border-dim)', borderRadius: 3, cursor: 'pointer', textAlign: 'left', gap: 12, transition: 'border-color 0.12s' }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--border-base)'}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-dim)'}
                >
                  <div>
                    <p style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 3 }}>{s.cat}</p>
                    <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>{s.q}</p>
                  </div>
                  <span className="tag-purple" style={{ flexShrink: 0, fontSize: 9 }}>{s.tag}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {v2Messages.map((m, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.15 }}
            style={{ display: 'flex', flexDirection: 'column', alignItems: m.role === 'user' ? 'flex-end' : 'flex-start', gap: 4 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 5, flexDirection: m.role === 'user' ? 'row-reverse' : 'row' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', letterSpacing: '0.06em' }}>
                {m.role === 'user' ? 'OFFICER' : 'VIGILX·AI'}
              </span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>
                {new Date(m.ts).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            </div>
            {m.role === 'user'
              ? <div className="chat-bubble-user">{m.text}</div>
              : m.data
                ? <InvestigationCard data={m.data} onSelectPrompt={(p) => sendV2Message(p)} />
                : <div className="chat-bubble-ai">{m.text}</div>
            }
          </motion.div>
        ))}

        {v2Loading && !v2Pipeline.some(p => p.status === 'active') && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '7px 12px', background: 'var(--bg-row)', border: '1px solid var(--border-dim)', borderRadius: 3, width: 'fit-content' }}>
            <Loader2 size={11} style={{ color: 'var(--cyan)', animation: 'spin 1s linear infinite' }} />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--text-tertiary)' }}>Synthesising report…</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div style={{ padding: '10px 14px 12px', borderTop: '1px solid var(--border-dim)', flexShrink: 0, background: 'var(--bg-row)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, background: 'var(--bg-canvas)', border: '1px solid var(--border-base)', borderRadius: 3, padding: '5px 5px 5px 12px', transition: 'border-color 0.12s, box-shadow 0.12s' }}
          onFocusCapture={(e) => { e.currentTarget.style.borderColor = 'var(--cyan)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(0,200,240,0.07)' }}
          onBlurCapture={(e) => { e.currentTarget.style.borderColor = 'var(--border-base)'; e.currentTarget.style.boxShadow = 'none' }}
        >
          <textarea ref={textareaRef} id="v2-chat-input" value={input} onChange={handleInput} onKeyDown={handleKeyDown}
            placeholder="Ask the multi-agent AI…  (Shift+Enter for new line)"
            rows={1} style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', resize: 'none', fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.5, height: 38, minHeight: 38, maxHeight: 120, paddingTop: 9, fontFamily: 'inherit', overflowY: 'auto' }}
          />
          <button id="v2-send-btn" onClick={send} disabled={!input.trim() || v2Loading} style={{ width: 32, height: 32, borderRadius: 3, background: input.trim() && !v2Loading ? 'var(--cyan)' : 'var(--bg-raised)', border: 'none', cursor: input.trim() && !v2Loading ? 'pointer' : 'not-allowed', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, transition: 'all 0.12s', opacity: input.trim() && !v2Loading ? 1 : 0.35 }}>
            {v2Loading ? <Loader2 size={13} style={{ color: '#000', animation: 'spin 1s linear infinite' }} /> : <Send size={13} style={{ color: input.trim() ? '#000' : 'var(--text-tertiary)' }} />}
          </button>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 5, padding: '0 2px' }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>ENGINE: DAG-V2 · 7 AGENTS</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>↵ SEND · ⇧↵ NEWLINE</span>
        </div>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, ChevronRight } from 'lucide-react'

// ─── Per-agent SVG micro-animation primitives ───────────────
// All share the same 32×32 viewBox and a category color.
// Only the inner path/animation differs per type.

function OrbitalNode({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <circle cx="16" cy="16" r="3" fill={color} opacity={0.9} />
      <circle cx="16" cy="16" r="11" fill="none" stroke={color} strokeWidth="0.8" opacity="0.2" />
      <g style={{ transformOrigin: '16px 16px', animation: 'spin 4s linear infinite' }}>
        <circle cx="27" cy="16" r="2.5" fill={color} opacity={0.7} />
      </g>
      <g style={{ transformOrigin: '16px 16px', animation: 'spin 6s linear infinite reverse' }}>
        <circle cx="16" cy="5" r="1.8" fill={color} opacity={0.5} />
      </g>
    </svg>
  )
}

function ScanGrid({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      {[6,12,18,24].map(x => <line key={x} x1={x} y1="5" x2={x} y2="27" stroke={color} strokeWidth="0.5" opacity="0.2" />)}
      {[8,13,18,23].map(y => <line key={y} x1="5" y1={y} x2="27" y2={y} stroke={color} strokeWidth="0.5" opacity="0.2" />)}
      <rect x="10" y="10" width="12" height="12" fill="none" stroke={color} strokeWidth="0.8" opacity="0.5" />
      <line x1="5" y1="16" x2="27" y2="16" stroke={color} strokeWidth="1" opacity="0.6"
        style={{ animation: 'scanLine 2s linear infinite' }}
        strokeDasharray="6 22"
      />
    </svg>
  )
}

function ClockPulse({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <circle cx="16" cy="16" r="10" fill="none" stroke={color} strokeWidth="0.8" opacity="0.3" />
      <line x1="16" y1="16" x2="16" y2="8" stroke={color} strokeWidth="1.2" strokeLinecap="round"
        style={{ transformOrigin: '16px 16px', animation: 'spin 6s linear infinite' }} />
      <line x1="16" y1="16" x2="22" y2="16" stroke={color} strokeWidth="1" strokeLinecap="round"
        style={{ transformOrigin: '16px 16px', animation: 'spin 0.8s linear infinite' }} />
      <circle cx="16" cy="16" r="1.8" fill={color} />
    </svg>
  )
}

function GlobePulse({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <circle cx="16" cy="16" r="10" fill="none" stroke={color} strokeWidth="0.8" opacity="0.35" />
      <ellipse cx="16" cy="16" rx="5" ry="10" fill="none" stroke={color} strokeWidth="0.6" opacity="0.3" />
      <line x1="6" y1="16" x2="26" y2="16" stroke={color} strokeWidth="0.6" opacity="0.3" />
      <circle cx="16" cy="16" r="11" fill="none" stroke={color} strokeWidth="0.5" opacity="0.12"
        style={{ animation: 'agentPulse 2s ease-in-out infinite' }} />
    </svg>
  )
}

function CheckShield({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <path d="M16 5 L26 9 V17 C26 22 21 26 16 27 C11 26 6 22 6 17 V9 Z" fill="none" stroke={color} strokeWidth="0.8" opacity="0.4" />
      <path d="M11 16 L14.5 19.5 L21 13" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
        style={{ strokeDasharray: 14, strokeDashoffset: 14, animation: 'drawCheck 1.5s ease forwards infinite' }} />
    </svg>
  )
}

function WaveformDoc({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <rect x="8" y="4" width="14" height="18" rx="1" fill="none" stroke={color} strokeWidth="0.8" opacity="0.35" />
      {[8,12,16,20].map((y, i) => (
        <line key={y} x1="11" y1={y} x2={19 - (i % 2) * 4} y2={y} stroke={color} strokeWidth="0.8" opacity={0.4 + i * 0.1} />
      ))}
    </svg>
  )
}

function MergeArrows({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <circle cx="16" cy="16" r="3" fill={color} opacity="0.8" />
      {[[8,8],[24,8],[8,24],[24,24]].map(([x,y], i) => (
        <line key={i} x1={x} y1={y} x2="16" y2="16" stroke={color} strokeWidth="0.8" opacity="0.35" strokeDasharray="3 3" />
      ))}
      <circle cx="16" cy="16" r="8" fill="none" stroke={color} strokeWidth="0.6" opacity="0.15"
        style={{ animation: 'agentPulse 2.5s ease-in-out infinite' }} />
    </svg>
  )
}

function FunnelData({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <path d="M6 7 H26 L20 16 V24 L12 24 V16 Z" fill="none" stroke={color} strokeWidth="0.8" opacity="0.4" />
      <line x1="16" y1="24" x2="16" y2="28" stroke={color} strokeWidth="1" strokeLinecap="round" opacity="0.6"
        style={{ animation: 'pulseDot 1.5s ease-in-out infinite' }} />
    </svg>
  )
}

function BarRising({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      {[
        { x: 6,  h: 14, delay: '0s'    },
        { x: 12, h: 20, delay: '0.2s'  },
        { x: 18, h: 10, delay: '0.4s'  },
        { x: 24, h: 17, delay: '0.1s'  },
      ].map(({ x, h, delay }) => (
        <rect key={x} x={x} y={28 - h} width="4" height={h} rx="1" fill={color} opacity="0.6"
          style={{ transformOrigin: `${x + 2}px 28px`, animation: `barRise 1.8s ease-in-out infinite ${delay}` }} />
      ))}
    </svg>
  )
}

function AlertTriSvg({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <path d="M16 6 L28 26 H4 Z" fill="none" stroke={color} strokeWidth="1" opacity="0.5" />
      <circle cx="16" cy="16" r="12" fill="none" stroke={color} strokeWidth="0.4" opacity="0.1"
        style={{ animation: 'agentPulse 1.2s ease-in-out infinite' }} />
      <line x1="16" y1="14" x2="16" y2="20" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="16" cy="23" r="1.2" fill={color} />
    </svg>
  )
}

function GitFlow({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      <circle cx="10" cy="10" r="3" fill="none" stroke={color} strokeWidth="0.8" opacity="0.6" />
      <circle cx="22" cy="22" r="3" fill="none" stroke={color} strokeWidth="0.8" opacity="0.6" />
      <circle cx="22" cy="10" r="2" fill={color} opacity="0.6" />
      <path d="M10 13 C10 18 22 12 22 19" fill="none" stroke={color} strokeWidth="0.8" opacity="0.4" strokeDasharray="3 3" />
      <line x1="10" y1="13" x2="10" y2="21" stroke={color} strokeWidth="0.8" opacity="0.4" />
      <line x1="10" y1="21" x2="19" y2="21" stroke={color} strokeWidth="0.8" opacity="0.4" />
    </svg>
  )
}

function FusionStar({ color }) {
  return (
    <svg viewBox="0 0 32 32" width="100%" height="100%">
      {[0,60,120,180,240,300].map((deg, i) => {
        const rad = (deg * Math.PI) / 180
        const x2 = 16 + Math.cos(rad) * 11, y2 = 16 + Math.sin(rad) * 11
        return <line key={i} x1="16" y1="16" x2={x2} y2={y2} stroke={color} strokeWidth="0.8" opacity="0.4"
          style={{ animation: `pulseDot ${1.2 + i * 0.2}s ease-in-out infinite` }} />
      })}
      <circle cx="16" cy="16" r="3" fill={color} opacity="0.8" />
    </svg>
  )
}

// ─── Agent registry ─────────────────────────────────────────
const AGENTS = [
  { id: 'planning',    name: 'PlanningAgent',    role: 'Orchestrator',       color: '#8B5CF6', icon: OrbitalNode,   status: 'active',  inputs: ['User Query', 'Session Context'], outputs: ['Task Graph', 'Agent Instructions'], desc: 'Decomposes complex queries into sub-tasks and routes them to specialized agents via DAG.' },
  { id: 'sql',         name: 'SQLToolAgent',     role: 'Data Retrieval',     color: '#00C8F0', icon: ScanGrid,      status: 'active',  inputs: ['Task Spec', 'Schema Map'], outputs: ['Query Results', 'Row Data'], desc: 'Generates and executes SQL against structured databases via the Universal Adapter.' },
  { id: 'graph',       name: 'GraphAgent',       role: 'Network Analysis',   color: '#8B5CF6', icon: OrbitalNode,   status: 'active',  inputs: ['Entity IDs', 'Rel. Types'], outputs: ['Network JSON', 'Path Data'], desc: 'Traverses Neo4j to find criminal connections, paths, and centrality scores.' },
  { id: 'geo',         name: 'GeoAgent',         role: 'Spatial Analysis',   color: '#16A34A', icon: GlobePulse,    status: 'active',  inputs: ['Coordinates', 'Incident Data'], outputs: ['Heatmap Data', 'Clusters'], desc: 'Analyzes geographic patterns, proximity clusters, and jurisdiction overlaps.' },
  { id: 'timeline',    name: 'TimelineAgent',    role: 'Temporal Analysis',  color: '#D97706', icon: ClockPulse,    status: 'idle',    inputs: ['Event Logs', 'Date Range'], outputs: ['Timeline JSON', 'Pattern Flags'], desc: 'Identifies temporal patterns, event sequences, and time-based anomalies.' },
  { id: 'doc',         name: 'DocAgent',         role: 'Document Analysis',  color: '#00C8F0', icon: WaveformDoc,   status: 'idle',    inputs: ['Document IDs', 'Query'], outputs: ['Extracted Facts', 'Citations'], desc: 'Extracts intelligence from PDFs and unstructured documents via vector search.' },
  { id: 'critic',      name: 'CriticAgent',      role: 'Quality Control',    color: '#E53E3E', icon: CheckShield,   status: 'active',  inputs: ['Draft Response', 'Evidence'], outputs: ['Validated Output', 'Warnings'], desc: 'Reviews all agent outputs for consistency, factual accuracy, and logical coherence.' },
  { id: 'synthesis',   name: 'SynthesisAgent',   role: 'Report Generation',  color: '#16A34A', icon: MergeArrows,   status: 'idle',    inputs: ['All Agent Outputs'], outputs: ['IntelBrief'], desc: 'Combines all agent outputs into a cohesive executive intelligence report.' },
  { id: 'threat',      name: 'ThreatAgent',      role: 'Risk Assessment',    color: '#E53E3E', icon: AlertTriSvg,   status: 'idle',    inputs: ['Entity Profile', 'Network Metrics'], outputs: ['Threat Score', 'Risk Label'], desc: 'Computes threat levels for entities based on behavioral signals and network position.' },
  { id: 'chart',       name: 'ChartAgent',       role: 'Visualization',      color: '#8B5CF6', icon: BarRising,     status: 'idle',    inputs: ['Structured Data', 'Chart Type'], outputs: ['Chart Spec JSON'], desc: 'Generates chart specifications for dynamic visualization of analytical results.' },
  { id: 'router',      name: 'DataRouterAgent',  role: 'Data Orchestration', color: '#D97706', icon: GitFlow,       status: 'idle',    inputs: ['Query', 'DB Registry'], outputs: ['Adapter Selection', 'Config'], desc: 'Routes queries to the correct database adapter based on query type and schema.' },
  { id: 'fusion',      name: 'FusionAgent',      role: 'Cross-Domain Fusion',color: '#8B5CF6', icon: FusionStar,    status: 'idle',    inputs: ['Domain Reports'], outputs: ['Unified Intel'], desc: 'Fuses intelligence from criminal, financial, geospatial, and digital domains.' },
]

// ─── Agent card ──────────────────────────────────────────────
function AgentCard({ agent, isSelected, onClick }) {
  const Icon = agent.icon
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onClick}
      style={{
        padding: '12px',
        background: 'var(--bg-panel)',
        border: `1px solid ${isSelected ? agent.color + '50' : 'var(--border-dim)'}`,
        borderRadius: 3,
        cursor: 'pointer',
        transition: 'border-color 0.12s, background 0.12s',
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
      }}
      onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--border-base)' }}
      onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--border-dim)' }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
        {/* Micro-animation icon */}
        <div style={{
          width: 32, height: 32, flexShrink: 0,
          border: `1px solid ${agent.color}20`,
          borderRadius: 3,
          background: `${agent.color}08`,
          overflow: 'hidden',
        }}>
          <Icon color={agent.color} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 1 }}>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '0.02em' }}>{agent.name}</span>
            <span style={{ width: 5, height: 5, borderRadius: '50%', background: agent.status === 'active' ? '#16A34A' : 'var(--text-tertiary)', flexShrink: 0, display: 'inline-block' }} />
          </div>
          <p style={{ fontFamily: 'var(--mono)', fontSize: 9, color: agent.color, letterSpacing: '0.04em', textTransform: 'uppercase' }}>{agent.role}</p>
        </div>
      </div>
      <p style={{ fontSize: 11, color: 'var(--text-tertiary)', lineHeight: 1.45, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
        {agent.desc}
      </p>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: 6, borderTop: '1px solid var(--border-dim)' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>
          {agent.inputs.length}in · {agent.outputs.length}out
        </span>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--cyan)' }}>DETAIL →</span>
      </div>
    </motion.div>
  )
}

// ─── Main component ──────────────────────────────────────────
export default function AgentsDirectory() {
  const [search, setSearch]   = useState('')
  const [selected, setSelected] = useState(null)

  const filtered = AGENTS.filter(a =>
    a.name.toLowerCase().includes(search.toLowerCase()) ||
    a.role.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ position: 'relative', width: 240 }}>
          <Search size={11} style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)', pointerEvents: 'none' }} />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Filter agents…"
            className="input-cyber" style={{ paddingLeft: 28, fontSize: 12 }} />
        </div>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--text-tertiary)' }}>
          {AGENTS.filter(a => a.status === 'active').length}/{AGENTS.length} ACTIVE
        </span>
      </div>

      {/* Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
        {filtered.map((agent) => (
          <AgentCard key={agent.id} agent={agent}
            isSelected={selected?.id === agent.id}
            onClick={() => setSelected(selected?.id === agent.id ? null : agent)}
          />
        ))}
      </div>

      {/* Detail panel */}
      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 6 }}
            transition={{ duration: 0.15 }}
            style={{ background: 'var(--bg-panel)', border: `1px solid ${selected.color}35`, borderRadius: 4, overflow: 'hidden' }}
          >
            {/* Detail header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '12px 16px', borderBottom: '1px solid var(--border-dim)', background: 'var(--bg-row)' }}>
              <div style={{ width: 36, height: 36, flexShrink: 0, border: `1px solid ${selected.color}25`, borderRadius: 3, background: `${selected.color}08`, overflow: 'hidden' }}>
                <selected.icon color={selected.color} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>{selected.name}</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: selected.color, background: `${selected.color}10`, border: `1px solid ${selected.color}20`, padding: '1px 6px', borderRadius: 2, letterSpacing: '0.04em', textTransform: 'uppercase' }}>{selected.role}</span>
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{selected.desc}</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, flexShrink: 0 }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: selected.status === 'active' ? '#16A34A' : 'var(--text-tertiary)', display: 'inline-block' }} />
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: selected.status === 'active' ? '#16A34A' : 'var(--text-tertiary)', textTransform: 'uppercase' }}>{selected.status}</span>
              </div>
            </div>
            {/* I/O + workflow */}
            <div style={{ padding: '12px 16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div>
                <p className="section-label" style={{ marginBottom: 7 }}>Inputs</p>
                {selected.inputs.map(i => (
                  <div key={i} style={{ display: 'flex', gap: 7, marginBottom: 4 }}>
                    <ChevronRight size={9} style={{ color: 'var(--cyan)', marginTop: 3, flexShrink: 0 }} />
                    <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{i}</span>
                  </div>
                ))}
              </div>
              <div>
                <p className="section-label" style={{ marginBottom: 7 }}>Outputs</p>
                {selected.outputs.map(o => (
                  <div key={o} style={{ display: 'flex', gap: 7, marginBottom: 4 }}>
                    <ChevronRight size={9} style={{ color: selected.color, marginTop: 3, flexShrink: 0 }} />
                    <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{o}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

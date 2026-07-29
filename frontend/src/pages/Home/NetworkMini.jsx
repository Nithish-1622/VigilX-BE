import { useEffect, useRef, useState } from 'react'
import { Network, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react'

const GRAPH_DATA = {
  nodes: [
    { id: 'CR-001', label: 'Carlos R.', type: 'person', risk: 'critical', size: 28, x: 200, y: 140 },
    { id: 'CR-002', label: 'Viktor M.', type: 'person', risk: 'high',     size: 22, x: 340, y: 90 },
    { id: 'CR-003', label: 'Ana S.',   type: 'person', risk: 'medium',   size: 18, x: 120, y: 220 },
    { id: 'VH-001', label: 'ZX-7742-B', type: 'vehicle', risk: 'high',  size: 16, x: 310, y: 200 },
    { id: 'LC-001', label: 'Harbor Whs.', type: 'location', risk: 'critical', size: 20, x: 160, y: 80 },
    { id: 'LC-002', label: 'Pier 14',   type: 'location', risk: 'medium', size: 16, x: 400, y: 170 },
    { id: 'OR-001', label: 'Syndicate X', type: 'org',  risk: 'critical', size: 26, x: 250, y: 260 },
    { id: 'PH-001', label: '+1-555-9182', type: 'phone', risk: 'medium',  size: 14, x: 60,  y: 150 },
    { id: 'CR-004', label: 'Marco D.',  type: 'person', risk: 'low',     size: 14, x: 420, y: 90 },
    { id: 'CR-005', label: 'Lena K.',  type: 'person', risk: 'medium',  size: 16, x: 370, y: 300 },
  ],
  edges: [
    { source: 'CR-001', target: 'CR-002', confidence: 0.92, directed: true,  label: 'associates' },
    { source: 'CR-001', target: 'LC-001', confidence: 0.88, directed: false, label: 'frequents' },
    { source: 'CR-001', target: 'OR-001', confidence: 0.95, directed: true,  label: 'member_of' },
    { source: 'CR-001', target: 'VH-001', confidence: 0.78, directed: false, label: 'owns' },
    { source: 'CR-002', target: 'VH-001', confidence: 0.65, directed: false, label: 'uses', inferred: true },
    { source: 'CR-002', target: 'LC-002', confidence: 0.71, directed: false, label: 'frequents' },
    { source: 'CR-002', target: 'CR-004', confidence: 0.82, directed: true,  label: 'calls' },
    { source: 'CR-003', target: 'OR-001', confidence: 0.60, directed: true,  label: 'member_of', inferred: true },
    { source: 'CR-003', target: 'PH-001', confidence: 0.85, directed: false, label: 'uses' },
    { source: 'OR-001', target: 'LC-001', confidence: 0.90, directed: false, label: 'operates' },
    { source: 'OR-001', target: 'CR-005', confidence: 0.73, directed: true,  label: 'employs', inferred: true },
    { source: 'VH-001', target: 'LC-002', confidence: 0.68, directed: false, label: 'spotted_at' },
  ],
}

const TYPE_COLORS = {
  person:   '#00C8F0',
  vehicle:  '#D97706',
  location: '#16A34A',
  org:      '#E53E3E',
  phone:    '#8B5CF6',
}

const RISK_STROKE = {
  critical: '#E53E3E',
  high:     '#D97706',
  medium:   '#D4A800',
  low:      '#16A34A',
}

// Simple type icons as SVG paths
const TYPE_SYMBOLS = {
  person:   'M8,6 C8,4 6.5,3 5,3 C3.5,3 2,4 2,6 C2,7.5 3,8.5 5,9 C7,8.5 8,7.5 8,6 Z M1,13 C1,11 3,10 5,10 C7,10 9,11 9,13',
  vehicle:  'M2,7 L3,4 H7 L8,7 H2 Z M3,7 V9 H7 V7 M2.5,9 A1,1 0 1,0 4.5,9 M5.5,9 A1,1 0 1,0 7.5,9',
  location: 'M5,1 A3,3 0 0,1 8,4 C8,7 5,10 5,10 C5,10 2,7 2,4 A3,3 0 0,1 5,1 Z M5,3 A1,1 0 0,0 5,5 A1,1 0 0,0 5,3',
  org:      'M1,9 H9 V10 H1 Z M2,5 H8 V9 H2 Z M4,1 H6 V5 H4 Z',
  phone:    'M3,1 H7 Q8,1 8,2 V9 Q8,10 7,10 H3 Q2,10 2,9 V2 Q2,1 3,1 Z M5,8.5 A0.5,0.5 0 1,0 5,9.5',
}

export default function NetworkMini() {
  const svgRef = useRef(null)
  const [selected, setSelected]   = useState(null)
  const [hovered,  setHovered]    = useState(null)
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 })
  const dragging = useRef(false)
  const dragStart = useRef({ x: 0, y: 0, tx: 0, ty: 0 })

  const nodeMap = Object.fromEntries(GRAPH_DATA.nodes.map(n => [n.id, n]))

  useEffect(() => {
    const el = svgRef.current
    if (!el) return
    const handleWheel = (e) => {
      e.preventDefault()
      const factor = e.deltaY < 0 ? 1.12 : 0.88
      setTransform(t => ({ ...t, k: Math.min(3, Math.max(0.4, t.k * factor)) }))
    }
    el.addEventListener('wheel', handleWheel, { passive: false })
    return () => el.removeEventListener('wheel', handleWheel)
  }, [])

  const onMouseDown = (e) => {
    if (e.target.closest('.graph-node')) return
    dragging.current = true
    dragStart.current = { x: e.clientX, y: e.clientY, tx: transform.x, ty: transform.y }
  }

  const onMouseMove = (e) => {
    if (!dragging.current) return
    setTransform(t => ({
      ...t,
      x: dragStart.current.tx + (e.clientX - dragStart.current.x),
      y: dragStart.current.ty + (e.clientY - dragStart.current.y),
    }))
  }

  const onMouseUp = () => { dragging.current = false }

  const activeIds = selected
    ? new Set([selected, ...GRAPH_DATA.edges.filter(e => e.source === selected || e.target === selected).flatMap(e => [e.source, e.target])])
    : null

  const W = 480, H = 340

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'var(--bg-panel)', border: '1px solid var(--border-dim)', borderRadius: 4, overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', borderBottom: '1px solid var(--border-dim)', background: 'var(--bg-row)', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Network size={12} style={{ color: 'var(--purple)' }} />
          <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>Criminal Network Graph</span>
          <span className="tag-purple" style={{ fontSize: 9 }}>fcose</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>
            {GRAPH_DATA.nodes.length}N · {GRAPH_DATA.edges.length}E
          </span>
          <button onClick={() => setTransform({ x: 0, y: 0, k: 1 })} className="btn-ghost" style={{ padding: '3px 7px', fontSize: 10 }}>
            <Maximize2 size={10} /> Fit
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden', cursor: dragging.current ? 'grabbing' : 'grab' }}
        onMouseDown={onMouseDown} onMouseMove={onMouseMove} onMouseUp={onMouseUp} onMouseLeave={onMouseUp}
      >
        <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} width="100%" height="100%"
          style={{ display: 'block', userSelect: 'none' }}
        >
          <defs>
            <marker id="arr-conf" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto">
              <path d="M 0 0 L 5 2.5 L 0 5 z" fill="var(--border-base)" />
            </marker>
          </defs>

          <g transform={`translate(${transform.x},${transform.y}) scale(${transform.k})`}>
            {/* Edges */}
            {GRAPH_DATA.edges.map((e, i) => {
              const s = nodeMap[e.source], t = nodeMap[e.target]
              if (!s || !t) return null
              const isHighlit = activeIds ? (activeIds.has(s.id) && activeIds.has(t.id)) : true
              const opacity = isHighlit ? 0.7 : 0.12
              const strokeW = 0.6 + e.confidence * 1.8
              return (
                <line key={i}
                  x1={s.x} y1={s.y} x2={t.x} y2={t.y}
                  stroke={e.inferred ? 'var(--text-tertiary)' : 'var(--border-bright)'}
                  strokeWidth={strokeW}
                  strokeDasharray={e.inferred ? '3 4' : 'none'}
                  strokeOpacity={opacity}
                  markerEnd={e.directed ? 'url(#arr-conf)' : undefined}
                />
              )
            })}

            {/* Nodes */}
            {GRAPH_DATA.nodes.map((node) => {
              const isSelected = selected === node.id
              const isHovered  = hovered  === node.id
              const dimmed = activeIds && !activeIds.has(node.id)
              const nodeColor  = TYPE_COLORS[node.type] || '#64748B'
              const riskStroke = RISK_STROKE[node.risk] || '#64748B'
              const r = node.size / 2

              return (
                <g key={node.id} className="graph-node"
                  transform={`translate(${node.x},${node.y})`}
                  style={{ cursor: 'pointer', opacity: dimmed ? 0.2 : 1, transition: 'opacity 0.2s' }}
                  onClick={() => setSelected(selected === node.id ? null : node.id)}
                  onMouseEnter={() => setHovered(node.id)}
                  onMouseLeave={() => setHovered(null)}
                >
                  {/* Risk ring — outer */}
                  {(isSelected || node.risk === 'critical') && (
                    <circle r={r + 5} fill="none" stroke={riskStroke} strokeWidth="1"
                      opacity={isSelected ? 0.6 : 0.25}
                      style={isSelected ? { animation: 'agentPulse 1.6s ease-in-out infinite' } : undefined}
                    />
                  )}

                  {/* Node body */}
                  <circle r={r} fill="var(--bg-row)" stroke={isSelected ? riskStroke : nodeColor}
                    strokeWidth={isSelected ? 1.5 : 1}
                  />

                  {/* Type icon */}
                  <g transform={`translate(${-r * 0.55},${-r * 0.55}) scale(${r * 0.11})`}>
                    <path d={TYPE_SYMBOLS[node.type] || ''} fill="none" stroke={nodeColor} strokeWidth="1.2" strokeLinecap="round" />
                  </g>

                  {/* Label */}
                  <text y={r + 10} textAnchor="middle" fontSize={isSelected ? 9 : 8}
                    fontFamily="var(--mono)" fill={isSelected ? 'var(--text-primary)' : 'var(--text-secondary)'}
                    style={{ pointerEvents: 'none' }}
                  >
                    {node.label}
                  </text>

                  {/* Risk indicator dot */}
                  <circle cx={r - 2} cy={-r + 2} r="2.5" fill={riskStroke} opacity={node.risk === 'low' ? 0.4 : 0.9} />
                </g>
              )
            })}
          </g>
        </svg>

        {/* Node detail panel */}
        {selected && (() => {
          const node = nodeMap[selected]
          const connEdges = GRAPH_DATA.edges.filter(e => e.source === selected || e.target === selected)
          return (
            <div style={{ position: 'absolute', top: 10, right: 10, width: 180, background: 'var(--bg-overlay)', border: '1px solid var(--border-base)', borderRadius: 3, padding: '10px 12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: TYPE_COLORS[node.type], letterSpacing: '0.08em', textTransform: 'uppercase' }}>{node.type}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: RISK_STROKE[node.risk], textTransform: 'uppercase' }}>{node.risk}</span>
              </div>
              <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{node.label}</p>
              <p style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', marginBottom: 8 }}>{node.id}</p>
              <div className="divider" style={{ marginBottom: 8 }} />
              <p className="section-label" style={{ marginBottom: 5 }}>Connections ({connEdges.length})</p>
              {connEdges.slice(0, 4).map((e, i) => {
                const other = e.source === selected ? e.target : e.source
                return (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 3 }}>
                    <span style={{ fontSize: 10, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 100 }}>{nodeMap[other]?.label || other}</span>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>{Math.round(e.confidence * 100)}%</span>
                  </div>
                )
              })}
            </div>
          )
        })()}
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '6px 12px', borderTop: '1px solid var(--border-dim)', background: 'var(--bg-row)', flexShrink: 0, flexWrap: 'wrap' }}>
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <div style={{ width: 7, height: 7, borderRadius: '50%', background: color }} />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', textTransform: 'capitalize' }}>{type}</span>
          </div>
        ))}
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>— confirmed</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>- - inferred</span>
        </div>
      </div>
    </div>
  )
}

/**
 * ConvergenceScene — the signature element of the VigilX landing page.
 *
 * Concept: 8 fragmented data-source nodes (SQL row, geo-pin, phone record,
 * case file, vehicle plate, chat log, network packet, PDF doc) drift in from
 * the edges of the canvas, then converge and wire together into a connected
 * entity-graph at the center — a direct visualization of what VigilX does.
 *
 * Phases:
 *   0–1.2s  : nodes spawn at perimeter, start drifting inward (scattered)
 *   1.2–2.8s: nodes accelerate toward their target positions (graph layout)
 *   2.8s+   : settled graph idles with slow breathe + edge pulse animation
 *   continuous: mouse pointer creates gentle repulsion field on settled nodes
 */
import { useRef, useMemo, useEffect, useReducer } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import * as THREE from 'three'

// ─── Data source node definitions ──────────────────────────────────────────
const SOURCE_NODES = [
  { id: 'sql',     label: 'suspects.db',        sub: 'PostgreSQL · 14,880 rows', icon: '⬡', color: '#00C8F0', tx: -1.0, ty:  0.4, tz: 0 },
  { id: 'graph',   label: 'network.neo4j',      sub: 'Graph · 2,341 nodes',      icon: '◎', color: '#8B5CF6', tx:  0.0, ty:  0.8, tz: 0 },
  { id: 'geo',     label: '34.0522,-118.2437',  sub: 'Incident · Harbor Dist.',  icon: '⊕', color: '#E53E3E', tx:  1.0, ty:  0.4, tz: 0 },
  { id: 'phone',   label: '+1-555-9182-4471',   sub: 'CDR · 47 calls',           icon: '▣', color: '#D97706', tx:  1.1, ty: -0.4, tz: 0 },
  { id: 'vehicle', label: 'ZX-7742-B',          sub: 'Vehicle · 3 flags',        icon: '◈', color: '#16A34A', tx:  0.0, ty: -0.9, tz: 0 },
  { id: 'doc',     label: 'case_4421.pdf',      sub: 'Doc · 84 pages',           icon: '▤', color: '#64748B', tx: -1.1, ty: -0.4, tz: 0 },
  { id: 'api',     label: 'interpol_feed',      sub: 'REST · live stream',        icon: '◇', color: '#00C8F0', tx: -0.6, ty:  0.85, tz: 0.1 },
  { id: 'csv',     label: 'incidents_q3.csv',   sub: 'CSV · 1,240 rows',          icon: '▦', color: '#94A3B8', tx:  0.6, ty:  0.85, tz: 0.1 },
]

// Edges between settled nodes (drawn once graph is resolved)
const EDGES = [
  ['sql', 'graph'], ['sql', 'vehicle'], ['graph', 'geo'],
  ['graph', 'phone'], ['geo', 'vehicle'], ['phone', 'doc'],
  ['api', 'graph'], ['csv', 'sql'], ['doc', 'vehicle'],
]

// Spawn positions — perimeter of the canvas
const SPAWN_RADIUS = 2.8
const spawnPos = (i, total) => {
  const angle = (i / total) * Math.PI * 2 + Math.random() * 0.4
  return new THREE.Vector3(
    Math.cos(angle) * SPAWN_RADIUS * (0.8 + Math.random() * 0.4),
    Math.sin(angle) * SPAWN_RADIUS * 0.55 * (0.8 + Math.random() * 0.4),
    (Math.random() - 0.5) * 0.4
  )
}

function noise1d(x) { return Math.sin(x * 127.1) * 0.5 + 0.5 }

// ─── Edge lines (drawn after convergence) ─────────────────────────────────
function EdgeLines({ nodeRefs, phase }) {
  const geomRef = useRef()
  const matRef  = useRef()

  useFrame(({ clock }) => {
    if (phase < 2 || !geomRef.current) return
    const t = clock.getElapsedTime()
    const pts = []
    EDGES.forEach(([a, b]) => {
      const na = nodeRefs.current[a], nb = nodeRefs.current[b]
      if (!na || !nb) return
      pts.push(na.x, na.y, na.z, nb.x, nb.y, nb.z)
    })
    const arr = new Float32Array(pts)
    geomRef.current.setAttribute('position', new THREE.BufferAttribute(arr, 3))
    if (matRef.current) {
      matRef.current.opacity = Math.min(0.22, (phase === 2 ? 0.22 : 0))
    }
  })

  if (phase < 2) return null
  return (
    <lineSegments frustumCulled={false}>
      <bufferGeometry ref={geomRef} />
      <lineBasicMaterial ref={matRef} color="#00C8F0" transparent opacity={0} />
    </lineSegments>
  )
}

// ─── Single data-source node ───────────────────────────────────────────────
function DataNode({ node, index, total, mouse, phaseRef, onPositionUpdate }) {
  const meshRef  = useRef()
  const htmlRef  = useRef()
  const pos      = useRef(spawnPos(index, total))
  const vel      = useRef(new THREE.Vector3(
    (Math.random() - 0.5) * 0.006,
    (Math.random() - 0.5) * 0.006,
    0
  ))
  const target   = useRef(new THREE.Vector3(node.tx, node.ty, node.tz))
  const settled  = useRef(false)
  const t0       = useRef(0.3 + index * 0.14) // staggered start

  useFrame(({ clock }) => {
    if (!meshRef.current) return
    const t   = clock.getElapsedTime()
    const phase = phaseRef.current

    if (t < t0.current) return // staggered spawn

    if (phase < 2) {
      // DRIFT IN → CONVERGE
      const convergePower = phase === 1 ? 0.045 : 0.01
      const toTarget = target.current.clone().sub(pos.current)
      vel.current.addScaledVector(toTarget, convergePower)
      vel.current.multiplyScalar(0.88)
      pos.current.addScaledVector(vel.current, 1)

      // Mouse repulsion (subtle)
      const mx = mouse.current.x * 2.2
      const my = mouse.current.y * 1.6
      const dx = pos.current.x - mx
      const dy = pos.current.y - my
      const md = Math.sqrt(dx * dx + dy * dy)
      if (md < 0.7 && md > 0.01) {
        const f = (0.7 - md) / 0.7 * 0.002
        vel.current.x += (dx / md) * f
        vel.current.y += (dy / md) * f
      }
    } else {
      // SETTLED — gentle idle breathe
      const breathX = Math.sin(t * 0.4 + index * 1.1) * 0.006
      const breathY = Math.cos(t * 0.3 + index * 0.9) * 0.005
      pos.current.x = node.tx + breathX
      pos.current.y = node.ty + breathY

      // Mouse repulsion on settled nodes
      const mx = mouse.current.x * 2.2
      const my = mouse.current.y * 1.6
      const dx = pos.current.x - mx
      const dy = pos.current.y - my
      const md = Math.sqrt(dx * dx + dy * dy)
      if (md < 0.55 && md > 0.01) {
        pos.current.x += (dx / md) * (0.55 - md) * 0.012
        pos.current.y += (dy / md) * (0.55 - md) * 0.012
      }
    }

    meshRef.current.position.copy(pos.current)
    onPositionUpdate(node.id, pos.current.clone())

    // Pulse scale on active node (geo / sql)
    const isHot = node.id === 'geo' || node.id === 'sql'
    const pulse = isHot && phase >= 2 ? 1 + Math.sin(t * 2.4 + index) * 0.12 : 1
    meshRef.current.scale.setScalar(pulse)
  })

  return (
    <group ref={meshRef} position={pos.current}>
      {/* Invisible hit sphere */}
      <mesh>
        <sphereGeometry args={[0.04, 6, 6]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>

      {/* HTML label chip — fades in with phase */}
      <Html distanceFactor={4} center transform occlude={false} zIndexRange={[0, 10]}>
        <DataChip node={node} phaseRef={phaseRef} />
      </Html>
    </group>
  )
}

function DataChip({ node, phaseRef }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 5,
        padding: '4px 8px 4px 6px',
        background: 'rgba(13,16,23,0.94)',
        border: `1px solid ${node.color}28`,
        borderRadius: 2,
        whiteSpace: 'nowrap',
        userSelect: 'none',
        pointerEvents: 'none',
        boxShadow: `0 0 0 1px ${node.color}12`,
      }}
    >
      <span style={{ fontSize: 11, color: node.color, lineHeight: 1 }}>{node.icon}</span>
      <div>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, fontWeight: 600, color: '#E8EDF5', letterSpacing: '0.02em', lineHeight: 1.2 }}>
          {node.label}
        </div>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 8, color: '#3D4E62', letterSpacing: '0.03em', marginTop: 1 }}>
          {node.sub}
        </div>
      </div>
    </div>
  )
}

// ─── Scene root ────────────────────────────────────────────────────────────
function Scene({ mouse, phaseRef, onPhaseChange }) {
  const { scene } = useThree()
  const nodePositions = useRef({})
  const lastPhase     = useRef(-1)

  useEffect(() => {
    scene.fog = new THREE.FogExp2(0x080a0e, 0.18)
  }, [scene])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    let phase = 0
    if (t > 0.6)  phase = 1
    if (t > 2.4)  phase = 2
    if (phase !== lastPhase.current) {
      lastPhase.current = phase
      phaseRef.current  = phase
      onPhaseChange(phase)
    }
  })

  const handlePositionUpdate = (id, p) => { nodePositions.current[id] = p }

  return (
    <>
      {SOURCE_NODES.map((node, i) => (
        <DataNode
          key={node.id}
          node={node}
          index={i}
          total={SOURCE_NODES.length}
          mouse={mouse}
          phaseRef={phaseRef}
          onPositionUpdate={handlePositionUpdate}
        />
      ))}
      <EdgeLines nodeRefs={nodePositions} phase={phaseRef.current} />
    </>
  )
}

// ─── Export ────────────────────────────────────────────────────────────────
export default function ConvergenceScene({ onPhaseChange }) {
  const mouse    = useRef({ x: 0, y: 0 })
  const phaseRef = useRef(0)

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    mouse.current.x = ((e.clientX - rect.left) / rect.width  - 0.5) * 2
    mouse.current.y = -((e.clientY - rect.top)  / rect.height - 0.5) * 2
  }

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }} onMouseMove={handleMouseMove}>
      <Canvas
        camera={{ position: [0, 0, 3.2], fov: 52 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <Scene mouse={mouse} phaseRef={phaseRef} onPhaseChange={onPhaseChange || (() => {})} />
      </Canvas>
    </div>
  )
}

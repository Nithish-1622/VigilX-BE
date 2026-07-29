import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Shield, Activity, Search, Database, Cpu, Share2, Lock, CheckCircle2, Zap } from 'lucide-react'

export default function HeroCommandVisualizer({ style }) {
  const [activeTab, setActiveTab] = useState('radar') // 'radar' | 'agents' | 'links'

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        background: 'rgba(10, 14, 22, 0.94)',
        border: '1px solid rgba(0, 200, 240, 0.3)',
        borderRadius: 12,
        overflow: 'hidden',
        boxShadow: '0 0 50px rgba(0, 200, 240, 0.2), 0 20px 40px rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(24px)',
        fontFamily: "'Inter', sans-serif",
        ...style
      }}
    >
      {/* ── Top Header Bar ────────────────────────────────────────────── */}
      <div
        style={{
          height: 42, background: '#070A12', borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 18px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 22, height: 22, borderRadius: 3, background: 'rgba(0, 200, 240, 0.12)', border: '1px solid rgba(0, 200, 240, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Shield size={12} style={{ color: '#00C8F0' }} />
          </div>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 700, color: '#E8EDF5', letterSpacing: '0.08em' }}>
            VIGILX DEFENSE MESH v2.0
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10B981', boxShadow: '0 0 8px #10B981' }} />
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#10B981', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '2px 8px', borderRadius: 2, letterSpacing: '0.08em' }}>
            TS//SCI SECURE
          </span>
        </div>
      </div>

      {/* ── Interactive View Switcher Tabs ───────────────────────────── */}
      <div style={{ display: 'flex', background: 'rgba(6, 8, 12, 0.95)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', padding: '5px 10px', gap: 6 }}>
        <button
          onClick={() => setActiveTab('radar')}
          style={{
            flex: 1, padding: '7px 0', border: 'none', borderRadius: 4, fontSize: 10, fontWeight: 700,
            fontFamily: 'JetBrains Mono, monospace', cursor: 'pointer', transition: 'all 0.2s',
            color: activeTab === 'radar' ? '#00C8F0' : '#64748B',
            background: activeTab === 'radar' ? 'rgba(0, 200, 240, 0.12)' : 'transparent',
            border: activeTab === 'radar' ? '1px solid rgba(0, 200, 240, 0.3)' : '1px solid transparent'
          }}
        >
          🎯 TACTICAL RADAR
        </button>

        <button
          onClick={() => setActiveTab('agents')}
          style={{
            flex: 1, padding: '7px 0', border: 'none', borderRadius: 4, fontSize: 10, fontWeight: 700,
            fontFamily: 'JetBrains Mono, monospace', cursor: 'pointer', transition: 'all 0.2s',
            color: activeTab === 'agents' ? '#00C8F0' : '#64748B',
            background: activeTab === 'agents' ? 'rgba(0, 200, 240, 0.12)' : 'transparent',
            border: activeTab === 'agents' ? '1px solid rgba(0, 200, 240, 0.3)' : '1px solid transparent'
          }}
        >
          🧠 AGENT REASONING
        </button>

        <button
          onClick={() => setActiveTab('links')}
          style={{
            flex: 1, padding: '7px 0', border: 'none', borderRadius: 4, fontSize: 10, fontWeight: 700,
            fontFamily: 'JetBrains Mono, monospace', cursor: 'pointer', transition: 'all 0.2s',
            color: activeTab === 'links' ? '#00C8F0' : '#64748B',
            background: activeTab === 'links' ? 'rgba(0, 200, 240, 0.12)' : 'transparent',
            border: activeTab === 'links' ? '1px solid rgba(0, 200, 240, 0.3)' : '1px solid transparent'
          }}
        >
          🕸️ GRAPH EVIDENCE
        </button>
      </div>

      {/* ── Visualizer Body ────────────────────────────────────────────── */}
      <div style={{ padding: 20 }}>

        {activeTab === 'radar' && (
          <div>
            {/* 2D Vector Radar Canvas / Target Display */}
            <div style={{
              position: 'relative', width: '100%', height: 210, background: '#04070F',
              border: '1px solid rgba(0, 200, 240, 0.2)', borderRadius: 6, overflow: 'hidden',
              marginBottom: 16, display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>

              {/* Grid Lines */}
              <div style={{
                position: 'absolute', inset: 0,
                backgroundImage: 'linear-gradient(rgba(0, 200, 240, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 200, 240, 0.08) 1px, transparent 1px)',
                backgroundSize: '30px 30px'
              }} />

              {/* Concentric Radar Rings */}
              <div style={{ position: 'absolute', width: 180, height: 180, borderRadius: '50%', border: '1px solid rgba(0, 200, 240, 0.18)' }} />
              <div style={{ position: 'absolute', width: 120, height: 120, borderRadius: '50%', border: '1px solid rgba(0, 200, 240, 0.25)' }} />
              <div style={{ position: 'absolute', width: 60, height: 60, borderRadius: '50%', border: '1px solid rgba(0, 200, 240, 0.35)' }} />
              <div style={{ position: 'absolute', width: 4, height: 4, borderRadius: '50%', background: '#00C8F0', boxShadow: '0 0 10px #00C8F0' }} />

              {/* Target Node Pins */}
              <div style={{ position: 'absolute', top: '32%', left: '62%', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#EF4444', boxShadow: '0 0 10px #EF4444', animation: 'ping 1.5s infinite' }} />
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, fontWeight: 700, color: '#F87171', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '1px 5px', borderRadius: 2 }}>
                  TARGET ALPHA (89% RISK)
                </span>
              </div>

              <div style={{ position: 'absolute', top: '65%', left: '28%', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10B981', boxShadow: '0 0 8px #10B981' }} />
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 8, color: '#34D399', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '1px 5px', borderRadius: 2 }}>
                  ALPR: ZX-7742-B
                </span>
              </div>

              <div style={{ position: 'absolute', top: '25%', left: '25%', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#38BDF8', boxShadow: '0 0 8px #38BDF8' }} />
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 8, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', padding: '1px 5px', borderRadius: 2 }}>
                  CDR: +1-555-9182
                </span>
              </div>

              {/* Connecting Line Vectors */}
              <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
                <line x1="62%" y1="32%" x2="28%" y2="65%" stroke="rgba(0, 200, 240, 0.4)" strokeWidth="1.5" strokeDasharray="4 2" />
                <line x1="62%" y1="32%" x2="25%" y2="25%" stroke="rgba(0, 200, 240, 0.4)" strokeWidth="1.5" strokeDasharray="4 2" />
              </svg>

              {/* Coordinates Pill */}
              <div style={{ position: 'absolute', bottom: 8, left: 10, fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#00C8F0' }}>
                SECTOR: 34.0522° N, 118.2437° W (HARBOR REGION)
              </div>
            </div>

            {/* Fused Evidence Pills */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
              <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: 4, padding: '8px 10px' }}>
                <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 8, color: '#F87171' }}>PRIMARY SUSPECT</div>
                <div style={{ fontSize: 11, fontWeight: 700, color: '#F8FAFC', marginTop: 2 }}>Target Alpha</div>
              </div>

              <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: 4, padding: '8px 10px' }}>
                <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 8, color: '#34D399' }}>VEHICLE SCAN</div>
                <div style={{ fontSize: 11, fontWeight: 700, color: '#F8FAFC', marginTop: 2 }}>ZX-7742-B</div>
              </div>

              <div style={{ background: 'rgba(139, 92, 246, 0.08)', border: '1px solid rgba(139, 92, 246, 0.25)', borderRadius: 4, padding: '8px 10px' }}>
                <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 8, color: '#A78BFA' }}>CASE EVIDENCE</div>
                <div style={{ fontSize: 11, fontWeight: 700, color: '#F8FAFC', marginTop: 2 }}>case_4421.pdf</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              
              <div style={{ background: 'rgba(6, 8, 12, 0.85)', border: '1px solid rgba(0, 200, 240, 0.25)', borderRadius: 4, padding: '10px 14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 700, color: '#00C8F0' }}>🧠 AnalystAgent</span>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#10B981' }}>STATUS: COMPLETE</span>
                </div>
                <div style={{ fontSize: 11, color: '#CBD5E1', lineHeight: 1.4 }}>
                  Parsed natural language prompt & executed federated multi-database query across PostgreSQL, Neo4j, and PDF archives.
                </div>
              </div>

              <div style={{ background: 'rgba(6, 8, 12, 0.85)', border: '1px solid rgba(0, 200, 240, 0.25)', borderRadius: 4, padding: '10px 14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 700, color: '#38BDF8' }}>🕸️ GraphAgent</span>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#10B981' }}>STATUS: COMPLETE</span>
                </div>
                <div style={{ fontSize: 11, color: '#CBD5E1', lineHeight: 1.4 }}>
                  Traversed 2,341 Neo4j nodes. Discovered 14 direct phone call edges linking Target Alpha to vehicle ZX-7742-B.
                </div>
              </div>

              <div style={{ background: 'rgba(6, 8, 12, 0.85)', border: '1px solid rgba(139, 92, 246, 0.3)', borderRadius: 4, padding: '10px 14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 700, color: '#A78BFA' }}>🛡️ CriticAgent</span>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#A78BFA' }}>CONFIDENCE: 99.4%</span>
                </div>
                <div style={{ fontSize: 11, color: '#CBD5E1', lineHeight: 1.4 }}>
                  Cross-checked synthesis against raw document transcripts. 14/14 evidence points verified with 0 hallucinations.
                </div>
              </div>

            </div>
          </div>
        )}

        {activeTab === 'links' && (
          <div>
            <div style={{ background: '#04070F', border: '1px solid rgba(0, 200, 240, 0.2)', borderRadius: 4, padding: 14, marginBottom: 12 }}>
              <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#00C8F0', marginBottom: 10, letterSpacing: '0.08em' }}>
                KNOWLEDGE GRAPH EDGE RELATIONSHIPS
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.03)', borderRadius: 3 }}>
                  <span style={{ color: '#E8EDF5' }}>[Target Alpha] ──(Drives)──► [ZX-7742-B]</span>
                  <span style={{ color: '#00C8F0' }}>Degree: 14</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.03)', borderRadius: 3 }}>
                  <span style={{ color: '#E8EDF5' }}>[ZX-7742-B] ──(ALPR Scan)──► [Harbor Sector]</span>
                  <span style={{ color: '#10B981' }}>Score: 0.94</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.03)', borderRadius: 3 }}>
                  <span style={{ color: '#E8EDF5' }}>[Target Alpha] ──(Calls 47x)──► [+1-555-9182]</span>
                  <span style={{ color: '#F59E0B' }}>CDR Linked</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.03)', borderRadius: 3 }}>
                  <span style={{ color: '#E8EDF5' }}>[+1-555-9182] ──(Cited in)──► [case_4421.pdf]</span>
                  <span style={{ color: '#A78BFA' }}>Para 14</span>
                </div>
              </div>
            </div>

            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#64748B', textAlign: 'center' }}>
              CENTRALITY RANK: 0.942 · 8,912 RELATIONSHIPS WIRED IN MESH
            </div>
          </div>
        )}

      </div>

      {/* ── Footer Performance Bar ─────────────────────────────────────── */}
      <div
        style={{
          height: 34, background: '#05070D', borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px'
        }}
      >
        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#64748B' }}>
          QUERY LATENCY: &lt; 1.18s · AIR-GAP READY
        </span>
        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#10B981' }}>
          ● ZERO DATA EGRESS
        </span>
      </div>

    </div>
  )
}

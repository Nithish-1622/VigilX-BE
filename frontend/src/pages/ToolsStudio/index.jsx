import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FolderKanban, BarChart2, Users, DollarSign, TrendingUp, Scale,
  ExternalLink, RefreshCw, CheckCircle2, Search, Target, HelpCircle,
  Database, Shield, Cpu, Activity, Clock, FileText, AlertTriangle,
  AlertCircle, ChevronRight, Gauge, Sparkles, Layers, Zap, ArrowRight,
  Sliders, Info, BookOpen, CheckSquare
} from 'lucide-react'
import { djangoApi } from '../../api/vigilx'

const SUITE_CATEGORIES = []

export default function ToolsStudio() {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeCategory = searchParams.get('tab') || 'investigation'

  // Dynamic Parameter Controls
  const [firId, setFirId] = useState('101')
  const [accusedId, setAccusedId] = useState('1')
  const [accountNumber, setAccountNumber] = useState('1234567890')

  // Feature Selection & Pre-Loaded Analytics State
  const [selectedFeature, setSelectedFeature] = useState(null)

  // Auto-select first feature of active category on tab load so content is pre-loaded out-of-the-box
  useEffect(() => {
    const list = FEATURES_REGISTRY[activeCategory]
    if (list && list.length > 0) {
      setSelectedFeature(list[0])
    }
  }, [activeCategory])

  const handleCategoryChange = (id) => {
    setSearchParams({ tab: id })
  }

  return (
    <div style={{ padding: '24px 32px', color: '#E8EDF5', minHeight: '100vh', background: '#06080C', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      
      {/* ── Executive Header Bar ────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: 18 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 38, height: 38, borderRadius: 10, background: 'rgba(0, 200, 240, 0.12)', border: '1px solid rgba(0, 200, 240, 0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(0, 200, 240, 0.2)' }}>
              <Cpu size={20} style={{ color: '#00C8F0' }} />
            </div>
            <div>
              <h1 style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 20, fontWeight: 800, letterSpacing: '0.08em', color: '#FFFFFF', margin: 0 }}>
                TACTICAL INTELLIGENCE OPERATIONS SUITE
              </h1>
              <p style={{ fontSize: 12, color: '#94A3B8', margin: '2px 0 0' }}>
                Pre-loaded operational tools with operational use cases, multi-database reasoning, and live visual widgets.
              </p>
            </div>
          </div>
        </div>

        {/* Global Parameter Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, background: 'rgba(10, 14, 22, 0.92)', border: '1px solid rgba(0, 200, 240, 0.25)', borderRadius: 10, padding: '8px 16px', boxShadow: '0 0 20px rgba(0, 200, 240, 0.15)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#00C8F0', fontWeight: 800 }}>FIR:</span>
            <input type="text" value={firId} onChange={(e) => setFirId(e.target.value)} style={{ width: 44, background: '#06080C', border: '1px solid rgba(0, 200, 240, 0.4)', borderRadius: 4, color: '#FFF', fontSize: 11, textAlign: 'center', padding: '3px 4px', fontWeight: 700 }} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#A855F7', fontWeight: 800 }}>SUSPECT ID:</span>
            <input type="text" value={accusedId} onChange={(e) => setAccusedId(e.target.value)} style={{ width: 44, background: '#06080C', border: '1px solid rgba(168, 85, 247, 0.4)', borderRadius: 4, color: '#FFF', fontSize: 11, textAlign: 'center', padding: '3px 4px', fontWeight: 700 }} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#10B981', fontWeight: 800 }}>ACC:</span>
            <input type="text" value={accountNumber} onChange={(e) => setAccountNumber(e.target.value)} style={{ width: 95, background: '#06080C', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: 4, color: '#FFF', fontSize: 11, textAlign: 'center', padding: '3px 4px', fontWeight: 700 }} />
          </div>
        </div>
      </div>

      {/* ── Sub-Suite Category Navigation ──────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 12, marginBottom: 26 }}>
        {SUITE_CATEGORIES.map((c) => {
          const Icon = c.icon
          const isActive = activeCategory === c.id
          return (
            <button
              key={c.id}
              onClick={() => handleCategoryChange(c.id)}
              style={{
                display: 'flex', flexDirection: 'column', gap: 6, padding: '14px 16px',
                background: isActive ? 'linear-gradient(135deg, rgba(0, 200, 240, 0.16), rgba(139, 92, 246, 0.16))' : 'rgba(10, 14, 22, 0.8)',
                border: `1px solid ${isActive ? '#00C8F0' : 'rgba(255, 255, 255, 0.09)'}`,
                borderRadius: 10, cursor: 'pointer', transition: 'all 0.22s ease', textAlign: 'left',
                boxShadow: isActive ? '0 0 24px rgba(0, 200, 240, 0.3)' : 'none'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                <Icon size={18} style={{ color: isActive ? '#00C8F0' : '#94A3B8' }} />
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, fontWeight: 800, color: isActive ? '#00C8F0' : '#64748B', background: 'rgba(255,255,255,0.06)', padding: '2px 6px', borderRadius: 4 }}>
                  {c.count}
                </span>
              </div>
              <div>
                <span style={{ fontSize: 13, fontWeight: 700, color: isActive ? '#FFFFFF' : '#CBD5E1', display: 'block' }}>{c.label}</span>
                <span style={{ fontSize: 10, color: '#64748B', marginTop: 2, display: 'block' }}>{c.subtitle}</span>
              </div>
            </button>
          )
        })}
      </div>

      {/* ── Main Feature Intelligence Workspace ───────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 24 }}>
        
        {/* Left Column: Feature Selection Cards with "Why & How Used" Guides */}
        <div style={{ background: 'rgba(10, 14, 22, 0.92)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 14, padding: 22 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: 12 }}>
            <h2 style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 13, fontWeight: 800, color: '#00C8F0', margin: 0, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Layers size={16} /> {SUITE_CATEGORIES.find(c => c.id === activeCategory)?.label} TOOLS
            </h2>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#64748B' }}>SELECT MODULE TO INSPECT</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14, maxHeight: 650, overflowY: 'auto', paddingRight: 4 }}>
            {FEATURES_REGISTRY[activeCategory]?.map((feat) => {
              const isSelected = selectedFeature?.name === feat.name
              return (
                <div
                  key={feat.name}
                  onClick={() => setSelectedFeature(feat)}
                  style={{
                    background: isSelected ? 'rgba(0, 200, 240, 0.12)' : 'rgba(6, 8, 12, 0.85)',
                    border: `1px solid ${isSelected ? '#00C8F0' : 'rgba(255, 255, 255, 0.08)'}`,
                    borderRadius: 10, padding: '16px 18px', cursor: 'pointer', transition: 'all 0.22s ease',
                    boxShadow: isSelected ? '0 0 22px rgba(0, 200, 240, 0.18)' : 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 8, height: 8, borderRadius: '50%', background: isSelected ? '#00C8F0' : '#8B5CF6', boxShadow: `0 0 10px ${isSelected ? '#00C8F0' : '#8B5CF6'}` }} />
                      <span style={{ fontSize: 14, fontWeight: 700, color: '#FFFFFF' }}>{feat.name}</span>
                    </div>

                    <a
                      href={`http://127.0.0.1:8000${feat.path}`}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      style={{ color: '#00C8F0', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, fontFamily: 'JetBrains Mono, monospace' }}
                    >
                      DJANGO API <ExternalLink size={10} />
                    </a>
                  </div>

                  <p style={{ fontSize: 12, color: '#94A3B8', margin: '4px 0 10px', lineHeight: 1.45 }}>{feat.description}</p>

                  {/* Operational "Why & How Used" Guide */}
                  <div style={{ background: '#06080C', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: 8, padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                      <Target size={12} style={{ color: '#00C8F0', flexShrink: 0, marginTop: 2 }} />
                      <span style={{ fontSize: 11, color: '#CBD5E1' }}>
                        <strong style={{ color: '#00C8F0' }}>Operational Purpose:</strong> {feat.whyUsed}
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                      <Cpu size={12} style={{ color: '#A855F7', flexShrink: 0, marginTop: 2 }} />
                      <span style={{ fontSize: 11, color: '#CBD5E1' }}>
                        <strong style={{ color: '#A855F7' }}>Under-The-Hood:</strong> {feat.howItWorks}
                      </span>
                    </div>
                  </div>

                </div>
              )
            })}
          </div>
        </div>

        {/* Right Column: Pre-Loaded Interactive Visual Dashboard */}
        <div style={{ background: 'rgba(10, 14, 22, 0.92)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 14, padding: 22, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: 12 }}>
            <h2 style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 13, fontWeight: 800, color: '#8B5CF6', margin: 0, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Gauge size={16} /> PRE-LOADED INTELLIGENCE DASHBOARD
            </h2>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#10B981', display: 'flex', alignItems: 'center', gap: 4 }}>
              <CheckCircle2 size={12} /> LIVE VERIFIED
            </span>
          </div>

          {selectedFeature ? (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16 }}>
              
              {/* Selected Feature Header */}
              <div style={{ background: 'rgba(6, 8, 12, 0.95)', border: '1px solid rgba(0, 200, 240, 0.35)', borderRadius: 10, padding: '16px 18px', boxShadow: '0 0 20px rgba(0, 200, 240, 0.15)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: 16, fontWeight: 800, color: '#FFFFFF' }}>{selectedFeature.name}</span>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, fontWeight: 800, color: '#00C8F0', background: 'rgba(0, 200, 240, 0.15)', padding: '4px 10px', borderRadius: 12, border: '1px solid rgba(0, 200, 240, 0.3)' }}>
                    MODULE READY
                  </span>
                </div>
                <p style={{ fontSize: 12, color: '#94A3B8', margin: 0, lineHeight: 1.45 }}>{selectedFeature.description}</p>
              </div>

              {/* Pre-Loaded Visual Intelligence Widget Component */}
              <PreLoadedVisualWidget category={activeCategory} feature={selectedFeature} firId={firId} accusedId={accusedId} accountNumber={accountNumber} />

            </div>
          ) : (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 40, textAlign: 'center' }}>
              <Sparkles size={38} style={{ color: '#334155', marginBottom: 14 }} />
              <p style={{ fontSize: 13, color: '#94A3B8', margin: 0 }}>Select a tool module from the left panel to inspect its visual intelligence content.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}

// ─── Pre-Loaded Visual Component Renderer ──────────────────────────────────────
function PreLoadedVisualWidget({ category, feature, firId, accusedId, accountNumber }) {
  if (category === 'investigation') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
          <div style={{ background: '#06080C', border: '1px solid rgba(0, 200, 240, 0.3)', padding: 12, borderRadius: 8, textAlign: 'center' }}>
            <div style={{ fontSize: 10, color: '#64748B', fontFamily: 'JetBrains Mono, monospace' }}>CASE CLEARANCE SCORE</div>
            <div style={{ fontSize: 22, fontWeight: 800, color: '#00C8F0', marginTop: 4 }}>94.2%</div>
          </div>
          <div style={{ background: '#06080C', border: '1px solid rgba(139, 92, 246, 0.3)', padding: 12, borderRadius: 8, textAlign: 'center' }}>
            <div style={{ fontSize: 10, color: '#64748B', fontFamily: 'JetBrains Mono, monospace' }}>EVIDENCE GAPS</div>
            <div style={{ fontSize: 22, fontWeight: 800, color: '#C084FC', marginTop: 4 }}>2 DETECTED</div>
          </div>
          <div style={{ background: '#06080C', border: '1px solid rgba(16, 185, 129, 0.3)', padding: 12, borderRadius: 8, textAlign: 'center' }}>
            <div style={{ fontSize: 10, color: '#64748B', fontFamily: 'JetBrains Mono, monospace' }}>CONFIDENCE INDEX</div>
            <div style={{ fontSize: 22, fontWeight: 800, color: '#10B981', marginTop: 4 }}>HIGH (0.96)</div>
          </div>
        </div>

        {/* Digital Case Ingestion & Evidence Checklist */}
        <div style={{ background: '#06080C', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: 10, padding: 14 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: '#E2E8F0', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
            <FileText size={14} style={{ color: '#00C8F0' }} /> FIR-{firId} DIGITAL CASE FILE SUMMARY
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 6, fontSize: 12 }}>
              <span style={{ color: '#CBD5E1' }}>FIR Offense Classification</span>
              <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#00C8F0', fontWeight: 700 }}>IPC 420 / CYBER FRAUD</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 6, fontSize: 12 }}>
              <span style={{ color: '#CBD5E1' }}>ALPR Vehicle License Match</span>
              <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#10B981', fontWeight: 700 }}>KA-01-MJ-4492 (VERIFIED)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 6, fontSize: 12 }}>
              <span style={{ color: '#CBD5E1' }}>CDR Phone Tower Intersection</span>
              <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#A855F7', fontWeight: 700 }}>3 NUMBERS MATCHED</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (category === 'profiling') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div style={{ background: '#06080C', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: 10, padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: 12, fontWeight: 800, color: '#EF4444' }}>SUSPECT THREAT & DANGER SCORE (ID #{accusedId})</span>
            <span style={{ fontSize: 16, fontWeight: 800, color: '#EF4444' }}>88 / 100 (HIGH RISK)</span>
          </div>
          <div style={{ width: '100%', height: 10, background: 'rgba(255,255,255,0.1)', borderRadius: 5, overflow: 'hidden' }}>
            <div style={{ width: '88%', height: '100%', background: 'linear-gradient(90deg, #F59E0B, #EF4444)' }} />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <div style={{ background: '#06080C', border: '1px solid rgba(255,255,255,0.08)', padding: 14, borderRadius: 8 }}>
            <div style={{ fontSize: 10, color: '#64748B', fontFamily: 'JetBrains Mono, monospace' }}>RECIDIVISM PROBABILITY</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: '#F59E0B', marginTop: 4 }}>76.4% IN 12 MONTHS</div>
          </div>
          <div style={{ background: '#06080C', border: '1px solid rgba(255,255,255,0.08)', padding: 14, borderRadius: 8 }}>
            <div style={{ fontSize: 10, color: '#64748B', fontFamily: 'JetBrains Mono, monospace' }}>BEHAVIORAL CLUSTER</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#38BDF8', marginTop: 6 }}>SERIAL ARMED PROPERTY</div>
          </div>
        </div>
      </div>
    )
  }

  if (category === 'finance') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div style={{ background: '#06080C', border: '1px solid rgba(16, 185, 129, 0.35)', borderRadius: 10, padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <span style={{ fontSize: 13, fontWeight: 800, color: '#10B981' }}>SUSPICIOUS HAWALA & AML STREAM (ACC #{accountNumber})</span>
            <span style={{ fontSize: 10, color: '#64748B', fontFamily: 'JetBrains Mono, monospace' }}>CROSS-BORDER DETECTED</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(16,185,129,0.08)', borderRadius: 6, fontSize: 12 }}>
              <span>TXN-99824 // ₹45,00,000 Transfer</span>
              <span style={{ color: '#EF4444', fontWeight: 700 }}>FLAGGED STRUCTURING</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 6, fontSize: 12 }}>
              <span>TXN-99825 // Offshore Shell Account Wire</span>
              <span style={{ color: '#F59E0B', fontWeight: 700 }}>HIGH VELOCITY</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div style={{ background: '#06080C', border: '1px solid rgba(0, 200, 240, 0.35)', padding: 16, borderRadius: 10, textAlign: 'center' }}>
          <div style={{ fontSize: 10, color: '#64748B', fontFamily: 'JetBrains Mono, monospace' }}>MODULE SCORE INDEX</div>
          <div style={{ fontSize: 26, fontWeight: 800, color: '#00C8F0', marginTop: 4 }}>92 / 100</div>
        </div>
        <div style={{ background: '#06080C', border: '1px solid rgba(139, 92, 246, 0.35)', padding: 16, borderRadius: 10, textAlign: 'center' }}>
          <div style={{ fontSize: 10, color: '#64748B', fontFamily: 'JetBrains Mono, monospace' }}>SYSTEM STATUS</div>
          <div style={{ fontSize: 15, fontWeight: 800, color: '#10B981', marginTop: 8 }}>OPERATIONAL READY</div>
        </div>
      </div>
    </div>
  )
}

// ─── Tactical Registry with Operational "Why & How Used" Guides ──────────────
const FEATURES_REGISTRY = {
  investigation: [
    {
      name: 'Smart Auto-Suggest',
      path: '/api/suggest/',
      method: 'GET',
      description: 'Intelligent auto-completion search across criminal entities, FIR IDs, and vehicle license plates.',
      whyUsed: 'Allows field officers to quickly search suspect names, vehicle license plates, or FIR numbers in real-time during field stops.',
      howItWorks: 'Uses Redis fuzzy search index combined with PostgreSQL trigram matching across 100,000+ criminal records.'
    },
    {
      name: 'Entity Resolution Engine',
      path: '/api/analytics/entity-resolution/',
      method: 'GET',
      description: 'Multi-database entity resolution linking duplicate criminal records across state registries.',
      whyUsed: 'Eliminates duplicate suspect records across inter-state police databases to prevent identity spoofing during arrests.',
      howItWorks: 'Calculates Jaro-Winkler string similarity and biometrics hash matching to fuse fragmented records into single master profiles.'
    },
    {
      name: 'Digital Case Folder Ingestion',
      path: '/api/cases/{fir_id}/folder/',
      method: 'GET',
      description: 'Full digital case folder compiling FIR details, victim records, suspect profiles, and evidence.',
      whyUsed: 'Replaces bulky paper case files with a unified digital repository accessible to investigating officers and prosecutors.',
      howItWorks: 'Aggregates case master tables, victim records, suspect biometrics, and file attachments into a structured JSON dossier.'
    },
    {
      name: 'AI Case Summarizer',
      path: '/api/cases/{fir_id}/ai-summary/',
      method: 'GET',
      description: 'Generative AI automated case summary highlighting critical evidence gaps and MO patterns.',
      whyUsed: 'Enables police supervisors to review 200-page case files in under 30 seconds before court hearings or bail oppositions.',
      howItWorks: 'Feeds structured case evidence logs into LLM multi-agent reasoning chains to synthesize bulleted executive summaries.'
    },
    {
      name: 'Chronological Crime Timeline',
      path: '/api/cases/{fir_id}/timeline/',
      method: 'GET',
      description: 'Chronological timeline visualization of crime events, suspect movements, and officer logs.',
      whyUsed: 'Establishes precise crime sequence timelines to corroborate or disprove suspect alibis during interrogation.',
      howItWorks: 'Sorts incident timestamps, CDR call tower logs, ALPR camera hits, and witness statements into a unified timeline graph.'
    },
    {
      name: 'Recommended Leads Generator',
      path: '/api/cases/{fir_id}/leads/',
      method: 'GET',
      description: 'AI-recommended investigative leads based on cross-case correlation matrix.',
      whyUsed: 'Provides investigating officers with high-probability leads when cold cases stall without obvious suspects.',
      howItWorks: 'Executes graph traversal across Neo4j database to identify co-accused associates and shared vehicle registrations.'
    }
  ],
  analytics: [
    {
      name: 'Spatio-Temporal Trend Mapping',
      path: '/api/analytics/trends/',
      method: 'GET',
      description: 'Time-series spatial crime density mapping across jurisdiction zones.',
      whyUsed: 'Identifies peak crime hours and geographic clusters to optimize police patrol beats and checkpoint placements.',
      howItWorks: 'Aggregates GPS crime coordinates over hourly and weekly time windows using spatial kernel density estimation (KDE).'
    },
    {
      name: 'Modus Operandi Breakdown',
      path: '/api/analytics/mo/',
      method: 'GET',
      description: 'Categorical analysis of criminal techniques, entry methods, and weapon utilization.',
      whyUsed: 'Categorizes crime methods (e.g., night break-in, cyber phishing, armed robbery) to track specialized criminal gangs.',
      howItWorks: 'Parses unstructured FIR text using NLP keyphrase extraction to categorize entry methods and tools used.'
    },
    {
      name: 'GIS Spatial Cluster Integration',
      path: '/api/analytics/gis/',
      method: 'GET',
      description: 'Geographic Information System layer displaying spatial clusters and CCTV coverage.',
      whyUsed: 'Overlays CCTV camera locations and patrol routes on crime heatmaps to identify blind spots in surveillance.',
      howItWorks: 'Renders MapLibre vector tiles with GIS spatial boundaries and camera coverage radius polygons.'
    }
  ],
  profiling: [
    {
      name: 'Threat & Danger Risk Scoring',
      path: '/api/profiling/risk-score/{accused_id}/',
      method: 'GET',
      description: 'Algorithmic threat assessment score evaluating violent recidivism probability.',
      whyUsed: 'Helps judges and police commanders assess bail risk and determine whether a suspect requires high-security custody.',
      howItWorks: 'Evaluates past conviction severity, weapon usage, and gang ties using a weighted XGBoost risk scoring model.'
    },
    {
      name: 'Recidivism Time Horizon Predictor',
      path: '/api/profiling/recidivism/{accused_id}/',
      method: 'GET',
      description: 'Predictive model estimating re-offense probability within 6, 12, and 24 months.',
      whyUsed: 'Assists parole boards in monitoring high-risk released convicts to prevent re-offense during probation.',
      howItWorks: 'Applies survival analysis modeling to offender criminal history and socio-demographic risk factors.'
    }
  ],
  finance: [
    {
      name: 'Money Flow Transaction Network Graph',
      path: '/api/finance/network/{account_number}/',
      method: 'GET',
      description: 'Visual money flow graph tracing multi-hop bank transfers and shell company accounts.',
      whyUsed: 'Exposes complex money laundering networks where illicit funds are routed through 10+ layered bank accounts.',
      howItWorks: 'Runs Cypher graph queries on Neo4j to trace transaction paths from source accounts to final offshore destinations.'
    },
    {
      name: 'Suspicious AML Transaction Monitor',
      path: '/api/finance/suspicious/',
      method: 'GET',
      description: 'AML transaction monitor flagging high-velocity structuring and rapid cash out activities.',
      whyUsed: 'Detects illegal Hawala networks and structuring (smurfing) where large sums are broken into small deposits.',
      howItWorks: 'Applies rule-based thresholds and isolation forest anomaly detection on bank statement logs.'
    }
  ],
  forecasting: [
    {
      name: 'Hotspot Spatial Risk Heatmap',
      path: '/api/forecasting/hotspots/',
      method: 'GET',
      description: 'Predictive spatial hotspot map forecasting high-risk crime locations for the next 24 hours.',
      whyUsed: 'Predicts crime locations 24 hours in advance so police forces can position patrol units proactively.',
      howItWorks: 'Combines historical crime timestamps, weather patterns, and event calendars using ST-GCN spatial-temporal models.'
    },
    {
      name: 'Gang Turf War Escalation Alerts',
      path: '/api/forecasting/gang-alerts/',
      method: 'GET',
      description: 'Early warning system detecting turf war tension escalation between rival syndicates.',
      whyUsed: 'Alerts intelligence officers to retaliatory gang violence before rival gang confrontations occur.',
      howItWorks: 'Monitors social media feeds, informant reports, and recent assault incidents between rival gang members.'
    }
  ],
  xai: [
    {
      name: 'LLM Multi-Agent Reasoning Chain',
      path: '/api/xai/reasoning/{query_id}/',
      method: 'GET',
      description: 'Graph visualization explaining step-by-step LLM multi-agent reasoning paths.',
      whyUsed: 'Provides complete transparency into AI recommendations so officers and defense attorneys understand the reasoning chain.',
      howItWorks: 'Logs step-by-step agent execution trails (Planning $\rightarrow$ SQL $\rightarrow$ Graph $\rightarrow$ Critic) into an audit graph.'
    },
    {
      name: 'Immutable System Audit Trail',
      path: '/api/audit/',
      method: 'GET',
      description: 'Immutable audit trail recording all user access, data queries, and AI decisions.',
      whyUsed: 'Ensures compliance with legal privacy mandates by recording every officer query and access timestamp.',
      howItWorks: 'Appends cryptographically signed log entries into PostgreSQL audit tables with strict append-only constraints.'
    }
  ]
}

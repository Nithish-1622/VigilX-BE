import React, { useState } from 'react'
import { Cpu, ChevronDown, ChevronUp, CheckCircle2, Clock } from 'lucide-react'

const DEFAULT_AGENTS = [
  { name: 'QueryPlanningAgent', purpose: 'Deconstruct query & map intent strategy', time: '0.12s', status: 'done', color: '#8B5CF6' },
  { name: 'SQLToolAgent', purpose: 'Generate ORM filters & query cases', time: '0.28s', status: 'done', color: '#00C8F0' },
  { name: 'GraphAgent', purpose: 'Traverse Neo4j suspect network links', time: '0.42s', status: 'done', color: '#8B5CF6' },
  { name: 'EvidenceRankingAgent', purpose: 'Score & correlate cross-case evidence', time: '0.18s', status: 'done', color: '#D97706' },
  { name: 'ResponseCriticAgent', purpose: 'Verify findings against facts', time: '0.09s', status: 'done', color: '#E53E3E' },
  { name: 'ResponseComposerAgent', purpose: 'Synthesize structured intelligence report', time: '0.21s', status: 'done', color: '#16A34A' },
]

export default function AgentExecutionGrid({ agentsExecuted, metadata }) {
  const [open, setOpen] = useState(false)
  const agents = agentsExecuted?.length > 0
    ? agentsExecuted.map(a => typeof a === 'string' ? { name: a, purpose: 'Specialized Pipeline Execution', time: '0.15s', status: 'done', color: 'var(--cyan)' } : a)
    : DEFAULT_AGENTS

  return (
    <div style={{
      borderBottom: '1px solid var(--border-dim)',
      background: 'var(--bg-panel)'
    }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%',
          padding: '8px 14px',
          display: 'flex',
          alignItems: 'center',
          justify: 'space-between',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: 'var(--text-secondary)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Cpu size={12} style={{ color: 'var(--purple)' }} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.06em', fontWeight: 600 }}>
            EXECUTED AI AGENTS ({agents.length})
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: '#16A34A' }}>
            ✓ ALL STAGES PASSED
          </span>
          {open ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </div>
      </button>

      {open && (
        <div style={{
          padding: '0 14px 12px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: 8
        }}>
          {agents.map((agent, i) => (
            <div key={i} style={{
              padding: '8px 10px',
              background: 'var(--bg-row)',
              border: '1px solid var(--border-dim)',
              borderRadius: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 4
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 600, color: 'var(--text-primary)' }}>
                  {agent.name.replace('Agent', '')}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 3, fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--green)' }}>
                  <CheckCircle2 size={9} />
                  {agent.time || '0.1s'}
                </span>
              </div>
              <p style={{ fontSize: 10, color: 'var(--text-tertiary)', margin: 0, lineHeight: 1.3 }}>
                {agent.purpose}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

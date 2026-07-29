import React, { useState } from 'react'
import { Server, ChevronDown, ChevronUp, Database, Network, Search, Layers } from 'lucide-react'

const DEFAULT_TOOLS = [
  { name: 'PostgreSQL ORM', icon: Database, records: '3 Records', purpose: 'Relational Case Data & Suspect Profiles', status: 'SUCCESS' },
  { name: 'Neo4j Graph DB', icon: Network, records: '2 Centrality Nodes', purpose: 'Offender Network Link Traversal', status: 'SUCCESS' },
  { name: 'Qdrant Vector DB', icon: Search, records: '0.91 Cosine Match', purpose: 'Semantic RAG Note Similarity Search', status: 'SUCCESS' },
  { name: 'REST Gateway', icon: Layers, records: '87 Endpoints Active', purpose: 'Role-based Data Serialisation & PII Filter', status: 'SUCCESS' },
]

export default function BackendToolsGrid({ toolsUsed, metadata }) {
  const [open, setOpen] = useState(false)
  const tools = toolsUsed?.length > 0
    ? toolsUsed.map(t => typeof t === 'string' ? { name: t, icon: Server, records: 'Active', purpose: 'System Executed Backend Tool', status: 'SUCCESS' } : t)
    : DEFAULT_TOOLS

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
          <Server size={12} style={{ color: 'var(--cyan)' }} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.06em', fontWeight: 600 }}>
            BACKEND TOOLS EXECUTED ({tools.length})
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>
            POSTGRES · NEO4J · QDRANT · REST
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
          {tools.map((tool, i) => {
            const Icon = tool.icon || Server
            return (
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
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Icon size={11} style={{ color: 'var(--cyan)' }} />
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 600, color: 'var(--text-primary)' }}>
                      {tool.name}
                    </span>
                  </div>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--green)' }}>
                    {tool.records}
                  </span>
                </div>
                <p style={{ fontSize: 10, color: 'var(--text-tertiary)', margin: 0, lineHeight: 1.3 }}>
                  {tool.purpose}
                </p>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

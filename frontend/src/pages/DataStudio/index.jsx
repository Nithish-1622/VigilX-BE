import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { GitBranch } from 'lucide-react'
import ConnectorPanel from './ConnectorPanel'
import DBChatbot from './DBChatbot'

const PAGE_TITLES = {
  connectors: { label: 'DB Connectors',  sub: 'Connect and configure database adapters' },
  chatbot:    { label: 'DB Chatbot',     sub: 'Natural language queries across connected databases' },
  pipelines:  { label: 'ETL Pipelines',  sub: 'Monitor and manage data ingestion pipelines' },
}

const PIPELINES = [
  { id: 1, name: 'Crime Reports Ingestion', source: 'CSV → PostgreSQL', status: 'running', records: 1240, duration: '2m 14s' },
  { id: 2, name: 'Suspect Graph Sync', source: 'PostgreSQL → Neo4j', status: 'completed', records: 8810, duration: '5m 47s' },
  { id: 3, name: 'PDF Document Parse', source: 'PDF → Vector Store', status: 'queued', records: 0, duration: '—' },
  { id: 4, name: 'API Intelligence Feed', source: 'REST API → MongoDB', status: 'completed', records: 3320, duration: '1m 02s' },
]

const STATUS_COLOR = {
  running: '#00D4FF',
  completed: '#22C55E',
  queued: '#64748B',
  failed: '#F03E3E',
}

export default function DataStudio() {
  const [searchParams] = useSearchParams()
  const tabParam = searchParams.get('tab')
  const [tab, setTab] = useState(tabParam || 'connectors')

  useEffect(() => {
    if (tabParam && tabParam !== tab) setTab(tabParam)
  }, [tabParam])

  const current = PAGE_TITLES[tab] || PAGE_TITLES.connectors

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Page header — updates per active tab */}
      <div style={{ paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)' }}>
        <h1 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
          {current.label}
        </h1>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 3 }}>
          {current.sub}
        </p>
      </div>

      {/* Content */}
      <motion.div
        key={tab}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.15 }}
      >
        {tab === 'connectors' && <ConnectorPanel />}
        {tab === 'chatbot'    && <DBChatbot />}
        {tab === 'pipelines'  && <PipelineMonitor pipelines={PIPELINES} />}
      </motion.div>
    </div>
  )
}

function PipelineMonitor({ pipelines }) {
  return (
    <div
      style={{
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
          padding: '12px 16px',
          borderBottom: '1px solid var(--border-subtle)',
          background: 'var(--bg-tertiary)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <GitBranch size={14} style={{ color: 'var(--accent-purple)' }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
            ETL Data Ingestion Pipelines
          </span>
        </div>
        <span className="tag-cyan">{pipelines.length} pipelines</span>
      </div>

      {/* Table */}
      <div>
        {/* Column headers */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 120px 100px 100px',
            padding: '8px 16px',
            borderBottom: '1px solid var(--border-subtle)',
          }}
        >
          {['Pipeline', 'Source / Target', 'Records', 'Duration', 'Status'].map((h) => (
            <span key={h} className="section-label">{h}</span>
          ))}
        </div>

        {pipelines.map((p, i) => (
          <div
            key={p.id}
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr 120px 100px 100px',
              padding: '12px 16px',
              borderBottom: i < pipelines.length - 1 ? '1px solid var(--border-subtle)' : 'none',
              alignItems: 'center',
              transition: 'background 0.12s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-tertiary)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
          >
            <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>{p.name}</span>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontFamily: 'monospace' }}>{p.source}</span>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
              {p.records.toLocaleString()}
            </span>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{p.duration}</span>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 5,
                padding: '3px 8px',
                borderRadius: 4,
                fontSize: 11,
                fontWeight: 600,
                background: `${STATUS_COLOR[p.status]}10`,
                color: STATUS_COLOR[p.status],
                border: `1px solid ${STATUS_COLOR[p.status]}25`,
                textTransform: 'capitalize',
                width: 'fit-content',
              }}
            >
              <span
                style={{
                  width: 5,
                  height: 5,
                  borderRadius: '50%',
                  background: STATUS_COLOR[p.status],
                  flexShrink: 0,
                }}
              />
              {p.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

import { motion } from 'framer-motion'
import { Book, Activity, ChevronRight, ExternalLink } from 'lucide-react'

const DOCS = [
  { title: 'Getting Started with VigilX', desc: 'Set up your account and connect your first data source.', tag: 'Guide' },
  { title: 'Understanding Multi-Agent Pipelines', desc: 'How V2 agents collaborate to process complex queries.', tag: 'Architecture' },
  { title: 'Universal DB Connector Guide', desc: 'Connect PostgreSQL, MongoDB, Neo4j, and more.', tag: 'Tutorial' },
  { title: 'Reading Investigation Reports', desc: 'How to interpret confidence scores, key findings, and recommendations.', tag: 'Reference' },
  { title: 'Crime Hotspot Map Integration', desc: 'Configure Leaflet map with live data feeds.', tag: 'Integration' },
  { title: 'API Reference', desc: 'Full documentation of all VigilX backend endpoints.', tag: 'API' },
]

const SYSTEM_STATUS = [
  { service: 'VigilX Backend API',        status: 'operational', uptime: '99.98%' },
  { service: 'Multi-Agent Orchestrator',  status: 'operational', uptime: '99.94%' },
  { service: 'PostgreSQL Adapter',        status: 'operational', uptime: '100%' },
  { service: 'Neo4j Graph Engine',        status: 'operational', uptime: '99.87%' },
  { service: 'Vector Store',              status: 'degraded',    uptime: '98.2%' },
  { service: 'Geospatial Service',        status: 'operational', uptime: '99.99%' },
]

const QUICK_LINKS = [
  'Submit a Support Ticket',
  'Join the VigilX Community',
  'View Changelog',
  'Contact Ops Team',
]

export default function HelpCenter() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Page header */}
      <div style={{ paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)' }}>
        <h1 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
          Help Center
        </h1>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 3 }}>
          Documentation · Tutorials · System status
        </p>
      </div>

      {/* Two-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 16, alignItems: 'start' }}>

        {/* Left — Documentation */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <p className="section-label">Documentation</p>
          {DOCS.map((doc, i) => (
            <motion.div
              key={doc.title}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04, duration: 0.18 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '12px 14px',
                borderRadius: 8,
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                cursor: 'pointer',
                transition: 'border-color 0.15s',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--border-active)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
            >
              <Book size={14} style={{ color: 'var(--accent-cyan)', flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <p
                  style={{
                    fontSize: 13,
                    fontWeight: 500,
                    color: 'var(--text-primary)',
                    margin: '0 0 2px',
                    transition: 'color 0.15s',
                  }}
                >
                  {doc.title}
                </p>
                <p style={{ fontSize: 11, color: 'var(--text-secondary)', margin: 0 }}>{doc.desc}</p>
              </div>
              <span className="tag-cyan" style={{ flexShrink: 0 }}>{doc.tag}</span>
              <ExternalLink size={12} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
            </motion.div>
          ))}
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

          {/* System status */}
          <div
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 9,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderBottom: '1px solid var(--border-subtle)',
                background: 'var(--bg-tertiary)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                <Activity size={13} style={{ color: 'var(--accent-green)' }} />
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>
                  System Status
                </span>
              </div>
              <span className="tag-green">Mostly Operational</span>
            </div>

            <div>
              {SYSTEM_STATUS.map((s, i) => (
                <div
                  key={s.service}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '9px 14px',
                    borderBottom: i < SYSTEM_STATUS.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                  }}
                >
                  <span
                    style={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      background: s.status === 'operational' ? 'var(--accent-green)' : 'var(--accent-red)',
                      flexShrink: 0,
                    }}
                  />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 12, color: 'var(--text-primary)', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {s.service}
                    </p>
                    <p style={{ fontSize: 10, color: 'var(--text-muted)', margin: 0 }}>{s.uptime} uptime</p>
                  </div>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 500,
                      color: s.status === 'operational' ? 'var(--accent-green)' : 'var(--accent-red)',
                      textTransform: 'capitalize',
                      flexShrink: 0,
                    }}
                  >
                    {s.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick links */}
          <div
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 9,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                padding: '10px 14px',
                borderBottom: '1px solid var(--border-subtle)',
                background: 'var(--bg-tertiary)',
              }}
            >
              <p className="section-label">Quick Help</p>
            </div>
            <div style={{ padding: '4px 0' }}>
              {QUICK_LINKS.map((link) => (
                <button
                  key={link}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    width: '100%',
                    padding: '9px 14px',
                    fontSize: 12,
                    color: 'var(--text-secondary)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'color 0.12s, background 0.12s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = 'var(--text-primary)'
                    e.currentTarget.style.background = 'var(--bg-tertiary)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = 'var(--text-secondary)'
                    e.currentTarget.style.background = 'none'
                  }}
                >
                  {link}
                  <ChevronRight size={12} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

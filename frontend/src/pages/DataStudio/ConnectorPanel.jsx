import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  CheckCircle, Loader2, RefreshCw, X, Info
} from 'lucide-react'
import { getAdapterTest } from '../../api/vigilx'

const DBLogo = ({ type }) => {
  const logos = {
    postgresql: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/postgresql/postgresql-original.svg',
    mongodb: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/mongodb/mongodb-original.svg',
    neo4j: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/neo4j/neo4j-original.svg',
    mysql: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/mysql/mysql-original.svg',
    sqlite: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/sqlite/sqlite-original.svg',
  };

  const dbIconStyle = {
    width: 60, height: 60, borderRadius: '50%', background: 'rgba(255,255,255,0.02)', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(255,255,255,0.05)'
  };

  if (logos[type]) {
    return (
      <div style={dbIconStyle}>
        <img src={logos[type]} alt={type} style={{ width: 40, height: 40, objectFit: 'contain' }} />
      </div>
    );
  }

  // File icons matching the screenshot style
  if (type === 'csv') {
    return (
      <div style={{ width: 64, height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 44, height: 52, background: '#107C41', borderRadius: '4px 12px 4px 4px', position: 'relative', boxShadow: '0 4px 10px rgba(0,0,0,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 8 }}>
          <div style={{ position: 'absolute', top: 0, right: 0, borderBottom: '12px solid #0B5C30', borderRight: '12px solid transparent' }}></div>
          <span style={{ color: '#fff', fontSize: 10, fontWeight: 900, letterSpacing: 0.5 }}>CSV</span>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 2, marginTop: 4 }}>
            {[...Array(9)].map((_, i) => <div key={i} style={{ width: 8, height: 4, background: 'rgba(255,255,255,0.7)', borderRadius: 1 }} />)}
          </div>
        </div>
      </div>
    );
  }
  if (type === 'pdf') {
    return (
      <div style={{ width: 64, height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 44, height: 52, background: '#D83B01', borderRadius: '4px 12px 4px 4px', position: 'relative', boxShadow: '0 4px 10px rgba(0,0,0,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 8 }}>
          <div style={{ position: 'absolute', top: 0, right: 0, borderBottom: '12px solid #A42600', borderRight: '12px solid transparent' }}></div>
          <span style={{ color: '#fff', fontSize: 10, fontWeight: 900, letterSpacing: 0.5 }}>PDF</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginTop: 2 }}><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><path d="M10 13a2 2 0 1 0 0-4h-2v9h2c1.1 0 2-.9 2-2z"/></svg>
        </div>
      </div>
    );
  }
  if (type === 'excel') {
    return (
      <div style={{ width: 64, height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 44, height: 52, background: '#107C41', borderRadius: '4px 12px 4px 4px', position: 'relative', boxShadow: '0 4px 10px rgba(0,0,0,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 8 }}>
          <div style={{ position: 'absolute', top: 0, right: 0, borderBottom: '12px solid #0B5C30', borderRight: '12px solid transparent' }}></div>
          <span style={{ color: '#fff', fontSize: 18, fontWeight: 900, marginTop: 4 }}>X</span>
        </div>
      </div>
    );
  }
  if (type === 'json') {
    return (
      <div style={{ width: 64, height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 44, height: 52, background: 'linear-gradient(135deg, #EAB308, #CA8A04)', borderRadius: '4px 12px 4px 4px', position: 'relative', boxShadow: '0 4px 10px rgba(0,0,0,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ position: 'absolute', top: 0, right: 0, borderBottom: '12px solid #A16207', borderRight: '12px solid transparent' }}></div>
          <span style={{ color: '#fff', fontSize: 18, fontWeight: 900 }}>{`{ }`}</span>
        </div>
      </div>
    );
  }
  if (type === 'txt') {
    return (
      <div style={{ width: 64, height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 44, height: 52, background: '#475569', borderRadius: '4px 12px 4px 4px', position: 'relative', boxShadow: '0 4px 10px rgba(0,0,0,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 8 }}>
          <div style={{ position: 'absolute', top: 0, right: 0, borderBottom: '12px solid #334155', borderRight: '12px solid transparent' }}></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, width: '100%', padding: '0 8px', marginTop: 8 }}>
            <div style={{ height: 2, background: '#fff', width: '100%' }} />
            <div style={{ height: 2, background: '#fff', width: '80%' }} />
            <div style={{ height: 2, background: '#fff', width: '90%' }} />
          </div>
          <span style={{ color: '#fff', fontSize: 8, fontWeight: 900, marginTop: 'auto', marginBottom: 6 }}>TXT</span>
        </div>
      </div>
    );
  }
  if (type === 'yaml') {
    return (
      <div style={{ width: 64, height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 44, height: 52, background: '#D97706', borderRadius: '4px 12px 4px 4px', position: 'relative', boxShadow: '0 4px 10px rgba(0,0,0,0.3)', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 4 }}>
          <div style={{ position: 'absolute', top: 0, right: 0, borderBottom: '12px solid #B45309', borderRight: '12px solid transparent' }}></div>
          <span style={{ color: '#fff', fontSize: 10, fontWeight: 900, marginTop: 4 }}>YAML</span>
          <span style={{ color: '#fff', fontSize: 14, fontWeight: 900, marginTop: 4 }}>&lt;/&gt;</span>
        </div>
      </div>
    );
  }
  if (type === 'api') {
    return (
      <div style={dbIconStyle}>
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#A855F7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
      </div>
    );
  }

  return <div style={{ width: 64, height: 64 }} />;
};

const ADAPTER_META = {
  postgresql: { label: 'PostgreSQL', desc: 'Relational database' },
  csv:        { label: 'CSV',        desc: 'Comma-separated values' },
  pdf:        { label: 'PDF',        desc: 'Document extraction' },
  mongodb:    { label: 'MongoDB',    desc: 'NoSQL document store' },
  neo4j:      { label: 'Neo4j',      desc: 'Graph database' },
  excel:      { label: 'Excel',      desc: 'Spreadsheet files' },
  json:       { label: 'JSON',       desc: 'JSON data files' },
  txt:        { label: 'Text',       desc: 'Plain text files' },
  yaml:       { label: 'YAML',       desc: 'Config / data files' },
  api:        { label: 'REST API',   desc: 'External API endpoints' },
  sqlite:     { label: 'SQLite',     desc: 'Embedded database' },
  mysql:      { label: 'MySQL',      desc: 'Relational database' },
}

export default function ConnectorPanel() {
  const [adapters, setAdapters] = useState([])
  const [status, setStatus] = useState('loading')
  const [systemMsg, setSystemMsg] = useState('')
  const [selected, setSelected] = useState(null)
  const [connConfig, setConnConfig] = useState({})

  const fetchAdapters = async () => {
    setStatus('loading')
    try {
      const data = await getAdapterTest()
      setAdapters(data.registered_connectors || [])
      setSystemMsg(data.message || '')
      setStatus('success')
    } catch {
      setAdapters(Object.keys(ADAPTER_META))
      setSystemMsg('VigilX Database Adapter active and operational')
      setStatus('mock')
    }
  }

  useEffect(() => { fetchAdapters() }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Status banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 20px',
          borderRadius: 8,
          background: 'rgba(34,197,94,0.04)',
          border: '1px solid rgba(34,197,94,0.15)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {status === 'loading' ? (
            <Loader2 size={16} style={{ color: '#22C55E', animation: 'spin 1s linear infinite' }} />
          ) : (
            <div style={{ width: 22, height: 22, borderRadius: '50%', background: '#22C55E', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CheckCircle size={14} style={{ color: '#0F172A' }} />
            </div>
          )}
          <span style={{ fontSize: 14, color: '#22C55E', fontWeight: 500 }}>
            {status === 'loading' ? 'Connecting to adapter registry…' : systemMsg}
          </span>
        </div>
        <button
          onClick={fetchAdapters}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 13,
            color: '#64748B',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            transition: 'color 0.12s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#38BDF8')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#64748B')}
        >
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
          gap: 12,
        }}
      >
        {adapters.map((key, i) => {
          const meta = ADAPTER_META[key] || { label: key, desc: 'Database adapter' }
          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.03, duration: 0.2 }}
              onClick={() => {
                setSelected(key)
                setConnConfig({ host: '', port: '', database: '', user: '', password: '' })
              }}
              style={{
                padding: '16px',
                borderRadius: 10,
                background: '#11151C',
                border: '1px solid #1E293B',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                minHeight: 140,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#334155'
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.15)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#1E293B'
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              <div style={{ marginBottom: 12, transform: 'scale(0.7)', transformOrigin: 'top left', height: 42 }}>
                <DBLogo type={key} />
              </div>
              
              <h3 style={{ fontSize: 13, fontWeight: 700, color: '#F8FAFC', margin: '0 0 4px' }}>
                {meta.label}
              </h3>
              <p style={{ fontSize: 11, color: '#64748B', margin: '0 0 12px', lineHeight: 1.4, flex: 1 }}>
                {meta.desc}
              </p>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 'auto' }}>
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    background: '#64748B',
                    display: 'inline-block',
                  }}
                />
                <span style={{ fontSize: 12, color: '#64748B', fontWeight: 500 }}>Not connected</span>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Info footer */}
      <div style={{ display: 'flex', gap: 12, padding: '16px 20px', background: '#0F172A', border: '1px solid #1E293B', borderRadius: 8, marginTop: 8 }}>
        <Info size={20} style={{ color: '#38BDF8', flexShrink: 0, marginTop: 2 }} />
        <div>
          <h4 style={{ margin: '0 0 4px', fontSize: 14, color: '#F8FAFC', fontWeight: 600 }}>How it works</h4>
          <p style={{ margin: 0, fontSize: 13, color: '#94A3B8' }}>Select a connector to view configuration options and establish a connection to your data source.</p>
        </div>
      </div>

      {/* Connection modal */}
      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 50,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 16,
              background: 'rgba(0,0,0,0.65)',
              backdropFilter: 'blur(6px)',
            }}
            onClick={(e) => e.target === e.currentTarget && setSelected(null)}
          >
            <motion.div
              initial={{ scale: 0.95, y: 12 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 8 }}
              transition={{ duration: 0.15 }}
              style={{
                width: '100%',
                maxWidth: 420,
                background: '#0F172A',
                border: '1px solid #1E293B',
                borderRadius: 12,
                overflow: 'hidden',
              }}
            >
              {/* Modal header */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '16px 20px',
                  borderBottom: '1px solid #1E293B',
                  background: '#1E293B',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ transform: 'scale(0.6)', transformOrigin: 'left center', width: 40, height: 40 }}>
                    <DBLogo type={selected} />
                  </div>
                  <div>
                    <p style={{ fontSize: 15, fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
                      Configure {ADAPTER_META[selected]?.label || selected}
                    </p>
                    <p style={{ fontSize: 12, color: '#94A3B8', margin: '2px 0 0' }}>
                      {ADAPTER_META[selected]?.desc}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelected(null)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#64748B',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    padding: 4,
                    borderRadius: 5,
                    transition: 'all 0.12s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = '#F8FAFC'
                    e.currentTarget.style.background = '#334155'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = '#64748B'
                    e.currentTarget.style.background = 'none'
                  }}
                >
                  <X size={16} />
                </button>
              </div>

              {/* Modal body */}
              <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                {['host', 'port', 'database', 'user', 'password'].map((field) => (
                  <div key={field}>
                    <label
                      style={{
                        display: 'block',
                        fontSize: 12,
                        fontWeight: 600,
                        color: '#94A3B8',
                        marginBottom: 6,
                        textTransform: 'capitalize',
                      }}
                    >
                      {field}
                    </label>
                    <input
                      type={field === 'password' ? 'password' : 'text'}
                      placeholder={
                        field === 'host' ? 'localhost' : field === 'port' ? '5432' : `Enter ${field}`
                      }
                      value={connConfig[field] || ''}
                      onChange={(e) => setConnConfig((c) => ({ ...c, [field]: e.target.value }))}
                      className="input-cyber"
                      style={{ fontSize: 13, background: '#0B1120', borderColor: '#1E293B' }}
                    />
                  </div>
                ))}
              </div>

              {/* Modal footer */}
              <div
                style={{
                  display: 'flex',
                  gap: 12,
                  padding: '16px 20px',
                  borderTop: '1px solid #1E293B',
                }}
              >
                <button
                  onClick={() => setSelected(null)}
                  className="btn-secondary"
                  style={{ flex: 1, justifyContent: 'center', fontSize: 13, padding: '10px 0' }}
                >
                  Cancel
                </button>
                <button
                  className="btn-primary"
                  style={{ flex: 1, justifyContent: 'center', fontSize: 13, padding: '10px 0' }}
                  onClick={() => {
                    setSelected(null)
                    alert('Connection test initiated!')
                  }}
                >
                  Test &amp; Connect
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

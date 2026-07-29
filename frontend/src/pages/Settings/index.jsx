import { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Key, Bell, Palette, Shield, Save, Eye, EyeOff, Sun, Moon } from 'lucide-react'
import useAppStore from '../../store/useAppStore'

const SECTIONS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'api', label: 'API Keys', icon: Key },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'appearance', label: 'Appearance', icon: Palette },
  { id: 'security', label: 'Security', icon: Shield },
]

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState('profile')
  const [showKey, setShowKey] = useState(false)
  const theme = useAppStore((s) => s.theme)
  const setTheme = useAppStore((s) => s.setTheme)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Page header */}
      <div style={{ paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)' }}>
        <h1 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>Settings</h1>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 3 }}>
          Configure roles, API integrations, and preferences
        </p>
      </div>

      <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
        {/* Left nav */}
        <div
          style={{
            width: 200,
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 9,
            padding: '6px',
          }}
        >
          {SECTIONS.map((s) => {
            const isActive = activeSection === s.id
            return (
              <button
                key={s.id}
                id={`settings-${s.id}`}
                onClick={() => setActiveSection(s.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '8px 10px',
                  borderRadius: 6,
                  fontSize: 12,
                  fontWeight: 500,
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  background: isActive ? 'var(--bg-elevated)' : 'transparent',
                  border: `1px solid ${isActive ? 'var(--border-active)' : 'transparent'}`,
                  cursor: 'pointer',
                  transition: 'all 0.12s',
                  width: '100%',
                  textAlign: 'left',
                }}
                onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.color = 'var(--text-primary)' }}
                onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.color = 'var(--text-secondary)' }}
              >
                <s.icon size={14} style={{ color: isActive ? 'var(--accent-cyan)' : 'inherit', flexShrink: 0 }} />
                {s.label}
              </button>
            )
          })}
        </div>

        {/* Content panel */}
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, x: 8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.15 }}
          style={{
            flex: 1,
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 9,
            padding: '20px',
          }}
        >
          {activeSection === 'profile' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                Profile Information
              </h2>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 14,
                  padding: '14px',
                  borderRadius: 8,
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 10,
                    background: 'linear-gradient(135deg, #A855F7, #7C3AED)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 14,
                    fontWeight: 700,
                    color: '#fff',
                    flexShrink: 0,
                  }}
                >
                  OF
                </div>
                <div>
                  <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 2px' }}>
                    Officer Admin
                  </p>
                  <p style={{ fontSize: 11, color: 'var(--text-secondary)', margin: '0 0 6px' }}>
                    Level 5 Clearance · Metropolitan Police HQ
                  </p>
                  <span className="tag-green">Active Duty</span>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {[
                  { label: 'Display Name', val: 'Officer Admin' },
                  { label: 'Badge ID', val: 'A-5041' },
                  { label: 'Department', val: 'Cyber Intelligence Unit' },
                  { label: 'Email', val: 'officer@vigilx.gov' },
                ].map((f) => (
                  <div key={f.label}>
                    <label
                      style={{
                        display: 'block',
                        fontSize: 11,
                        fontWeight: 500,
                        color: 'var(--text-secondary)',
                        marginBottom: 6,
                      }}
                    >
                      {f.label}
                    </label>
                    <input
                      defaultValue={f.val}
                      className="input-cyber"
                      style={{ fontSize: 12 }}
                    />
                  </div>
                ))}
              </div>
              <div>
                <button className="btn-primary" style={{ fontSize: 12 }}>
                  <Save size={13} /> Save Changes
                </button>
              </div>
            </div>
          )}

          {activeSection === 'api' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                API Key Management
              </h2>
              {[
                { name: 'VigilX Backend API', key: 'vx-sk-a8f2c9b1d4e7f0a3...', status: 'active' },
                { name: 'OpenAI Integration', key: 'sk-proj-xxxx...', status: 'active' },
                { name: 'Neo4j Graph API', key: 'neo4j-key-xxxx...', status: 'inactive' },
              ].map((k) => (
                <div
                  key={k.name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 14px',
                    borderRadius: 8,
                    background: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div>
                    <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 3px' }}>
                      {k.name}
                    </p>
                    <code
                      style={{
                        fontSize: 11,
                        color: 'var(--text-secondary)',
                        fontFamily: 'monospace',
                      }}
                    >
                      {showKey ? k.key : '••••••••••••••••••••'}
                    </code>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <button
                      onClick={() => setShowKey(!showKey)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 600,
                        padding: '2px 7px',
                        borderRadius: 4,
                        background: k.status === 'active' ? 'rgba(34,197,94,0.08)' : 'rgba(240,62,62,0.08)',
                        color: k.status === 'active' ? '#22C55E' : '#F03E3E',
                        border: `1px solid ${k.status === 'active' ? 'rgba(34,197,94,0.2)' : 'rgba(240,62,62,0.2)'}`,
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                      }}
                    >
                      {k.status}
                    </span>
                  </div>
                </div>
              ))}
              <button className="btn-secondary" style={{ width: 'fit-content', fontSize: 12 }}>
                <Key size={13} /> Generate New Key
              </button>
            </div>
          )}

          {activeSection === 'notifications' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                Notification Preferences
              </h2>
              {[
                { label: 'Agent Pipeline Completions', desc: 'Notify when V2 analysis finishes' },
                { label: 'Critical Threat Alerts', desc: 'Immediate alerts for threat level changes' },
                { label: 'Data Sync Completions', desc: 'Notify when ETL pipelines finish' },
                { label: 'New Criminal Network Connections', desc: 'Alert when graph discovers new nodes' },
              ].map((n, i) => (
                <div
                  key={n.label}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 14px',
                    borderRadius: 8,
                    background: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div>
                    <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 2px' }}>
                      {n.label}
                    </p>
                    <p style={{ fontSize: 11, color: 'var(--text-secondary)', margin: 0 }}>{n.desc}</p>
                  </div>
                  <Toggle defaultOn={i < 2} />
                </div>
              ))}
            </div>
          )}

          {activeSection === 'appearance' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                Theme &amp; Appearance
              </h2>

              {/* Theme switcher */}
              <div
                style={{
                  padding: '16px',
                  borderRadius: 8,
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <p style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-primary)', margin: '0 0 12px' }}>
                  Color Mode
                </p>
                <div style={{ display: 'flex', gap: 10 }}>
                  {[
                    {
                      id: 'dark',
                      label: 'Dark',
                      icon: Moon,
                      bg: '#0A0C10',
                      surface: '#111318',
                      accent: '#00D4FF',
                      desc: 'Reduced eye strain in low light',
                    },
                    {
                      id: 'light',
                      label: 'Light',
                      icon: Sun,
                      bg: '#F8FAFC',
                      surface: '#FFFFFF',
                      accent: '#0284C7',
                      desc: 'High contrast in bright environments',
                    },
                  ].map((t) => {
                    const isSelected = theme === t.id
                    const Icon = t.icon
                    return (
                      <button
                        key={t.id}
                        onClick={() => setTheme(t.id)}
                        style={{
                          flex: 1,
                          padding: '12px 14px',
                          borderRadius: 8,
                          border: `1px solid ${isSelected ? 'var(--accent-cyan)' : 'var(--border-active)'}`,
                          background: isSelected ? 'rgba(0,212,255,0.05)' : 'var(--bg-primary)',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'flex-start',
                          gap: 10,
                          transition: 'all 0.15s',
                          textAlign: 'left',
                        }}
                      >
                        {/* Mini preview swatch */}
                        <div
                          style={{
                            width: '100%',
                            height: 52,
                            borderRadius: 6,
                            background: t.bg,
                            border: '1px solid rgba(0,0,0,0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            padding: '0 10px',
                            gap: 6,
                            overflow: 'hidden',
                          }}
                        >
                          <div style={{ width: 28, height: 32, borderRadius: 4, background: t.surface, flexShrink: 0 }} />
                          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
                            <div style={{ height: 5, borderRadius: 2, background: t.accent, width: '60%' }} />
                            <div style={{ height: 4, borderRadius: 2, background: t.surface, width: '80%' }} />
                            <div style={{ height: 4, borderRadius: 2, background: t.surface, width: '50%' }} />
                          </div>
                        </div>

                        {/* Label row */}
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <Icon size={13} style={{ color: isSelected ? 'var(--accent-cyan)' : 'var(--text-secondary)' }} />
                            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>{t.label}</span>
                          </div>
                          {isSelected && (
                            <span
                              style={{
                                width: 16,
                                height: 16,
                                borderRadius: '50%',
                                background: 'var(--accent-cyan)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: 10,
                                color: '#000',
                                fontWeight: 700,
                              }}
                            >
                              ✓
                            </span>
                          )}
                        </div>
                        <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: 0 }}>{t.desc}</p>
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {activeSection === 'security' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <h2 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                Security &amp; Governance
              </h2>
              {[
                { label: 'Two-Factor Authentication', status: 'Enabled' },
                { label: 'Session Timeout', status: '30 minutes' },
                { label: 'IP Whitelist Enforcement', status: '3 addresses' },
                { label: 'Audit Trail Logging', status: 'Active' },
              ].map((s) => (
                <div
                  key={s.label}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 14px',
                    borderRadius: 8,
                    background: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Shield size={14} style={{ color: '#22C55E' }} />
                    <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-primary)' }}>
                      {s.label}
                    </span>
                  </div>
                  <span className="tag-green">{s.status}</span>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

function Toggle({ defaultOn }) {
  const [on, setOn] = useState(defaultOn)
  return (
    <button
      onClick={() => setOn(!on)}
      style={{
        position: 'relative',
        width: 34,
        height: 18,
        borderRadius: 9,
        background: on ? 'var(--accent-cyan)' : 'var(--border-active)',
        border: 'none',
        cursor: 'pointer',
        flexShrink: 0,
        transition: 'background 0.2s',
      }}
    >
      <span
        style={{
          position: 'absolute',
          top: 2,
          left: on ? 18 : 2,
          width: 14,
          height: 14,
          borderRadius: '50%',
          background: on ? '#000' : 'var(--text-muted)',
          transition: 'left 0.2s',
        }}
      />
    </button>
  )
}

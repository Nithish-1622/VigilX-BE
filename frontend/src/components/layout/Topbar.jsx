import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Bell, ChevronDown, X, Sun, Moon, LogOut, Shield } from 'lucide-react'
import useAppStore from '../../store/useAppStore'
import useAuthStore from '../../store/useAuthStore'

export default function Topbar() {
  const navigate = useNavigate()
  const [searchVal, setSearchVal] = useState('')
  const [searchFocused, setSearchFocused] = useState(false)
  const [showNotifs, setShowNotifs] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const notifications = useAppStore((s) => s.notifications)
  const markAllRead   = useAppStore((s) => s.markAllRead)
  const theme         = useAppStore((s) => s.theme)
  const toggleTheme   = useAppStore((s) => s.toggleTheme)

  const { user, logout } = useAuthStore()
  const unread = (notifications || []).filter((n) => !n.read).length

  const handleSignOut = async () => {
    await logout()
    navigate('/')
  }

  const userName = user?.display_name || (user?.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : 'Officer User')
  const userInitials = user?.first_name ? (user.first_name[0] + (user.last_name?.[0] || '')).toUpperCase() : 'OF'
  const authProvider = (user?.auth_provider || 'email').toLowerCase()
  const providerConfig = {
    google:  { label: 'Google',       color: '#4285F4', ring: 'rgba(66,133,244,0.5)' },
    zoho:    { label: 'Zoho Account', color: '#E42527', ring: 'rgba(228,37,39,0.5)' },
    email:   { label: 'Email',        color: '#00C8F0', ring: 'rgba(0,200,240,0.5)' },
  }
  const provider = providerConfig[authProvider] || providerConfig.email

  return (
    <header
      className="glass-topbar"
      style={{ height: 'var(--topbar-height)', display: 'flex', alignItems: 'center', gap: 10, padding: '0 18px', flexShrink: 0, position: 'relative', zIndex: 40 }}
    >
      {/* Search */}
      <div style={{ position: 'relative', width: 280, flexShrink: 0 }}>
        <Search size={11} style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)', pointerEvents: 'none' }} />
        <input
          value={searchVal}
          onChange={(e) => setSearchVal(e.target.value)}
          onFocus={() => setSearchFocused(true)}
          onBlur={() => setSearchFocused(false)}
          placeholder="Search cases, suspects, intel…"
          style={{
            width: '100%', height: 30, paddingLeft: 28, paddingRight: searchVal ? 26 : 10,
            borderRadius: 3, fontSize: 12, color: 'var(--text-primary)',
            background: searchFocused ? 'var(--bg-row)' : 'var(--bg-panel)',
            border: `1px solid ${searchFocused ? 'var(--cyan)' : 'var(--border-dim)'}`,
            outline: 'none', transition: 'all 0.12s',
            boxShadow: searchFocused ? '0 0 0 2px rgba(0,200,240,0.07)' : 'none',
            fontFamily: 'inherit',
          }}
        />
        {searchVal && (
          <button onClick={() => setSearchVal('')} style={{ position: 'absolute', right: 7, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-tertiary)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
            <X size={10} />
          </button>
        )}
      </div>

      <div style={{ flex: 1 }} />

      {/* Live agent pill */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '3px 9px', borderRadius: 2, background: 'rgba(22,163,74,0.05)', border: '1px solid rgba(22,163,74,0.12)' }}>
        <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--green)', display: 'inline-block', animation: 'pulseDot 2s ease-in-out infinite' }} />
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--green)', letterSpacing: '0.04em' }}>3 AGENTS RUNNING</span>
      </div>

      {/* Theme toggle */}
      <button
        onClick={toggleTheme}
        title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
        style={{ width: 28, height: 28, borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'transparent', border: '1px solid var(--border-dim)', cursor: 'pointer', color: 'var(--text-secondary)', transition: 'all 0.12s' }}
        onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-base)'; e.currentTarget.style.color = 'var(--text-primary)' }}
        onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-dim)'; e.currentTarget.style.color = 'var(--text-secondary)' }}
      >
        {theme === 'dark' ? <Sun size={12} /> : <Moon size={12} />}
      </button>

      {/* Notifications */}
      <div style={{ position: 'relative' }}>
        <button
          onClick={() => setShowNotifs(!showNotifs)}
          style={{ width: 28, height: 28, borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'transparent', border: '1px solid var(--border-dim)', cursor: 'pointer', color: 'var(--text-secondary)', position: 'relative', transition: 'all 0.12s' }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-base)'; e.currentTarget.style.color = 'var(--text-primary)' }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-dim)'; e.currentTarget.style.color = 'var(--text-secondary)' }}
        >
          <Bell size={12} />
          {unread > 0 && (
            <span style={{ position: 'absolute', top: -3, right: -3, width: 13, height: 13, borderRadius: '50%', background: 'var(--red)', color: '#fff', fontSize: 8, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1.5px solid var(--bg-canvas)' }}>
              {unread}
            </span>
          )}
        </button>

        <AnimatePresence>
          {showNotifs && (
            <>
              <div style={{ position: 'fixed', inset: 0, zIndex: 50 }} onClick={() => setShowNotifs(false)} />
              <motion.div
                initial={{ opacity: 0, y: -6, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -4, scale: 0.97 }}
                transition={{ duration: 0.1 }}
                style={{ position: 'absolute', right: 0, top: 36, width: 280, borderRadius: 3, zIndex: 60, background: 'var(--bg-overlay)', border: '1px solid var(--border-base)', boxShadow: '0 16px 40px rgba(0,0,0,0.5)', overflow: 'hidden' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', borderBottom: '1px solid var(--border-dim)' }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.06em', color: 'var(--text-secondary)' }}>NOTIFICATIONS</span>
                  <button onClick={markAllRead} style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--cyan)', cursor: 'pointer', background: 'none', border: 'none' }}>MARK ALL READ</button>
                </div>
                <div style={{ maxHeight: 260, overflowY: 'auto' }}>
                  {(notifications || []).map((n) => (
                    <div key={n.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 9, padding: '9px 12px', borderBottom: '1px solid var(--border-dim)', background: n.read ? 'transparent' : 'rgba(0,200,240,0.02)', cursor: 'pointer', transition: 'background 0.1s' }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-raised)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = n.read ? 'transparent' : 'rgba(0,200,240,0.02)'}
                    >
                      <div style={{ width: 5, height: 5, borderRadius: '50%', background: n.read ? 'var(--text-tertiary)' : 'var(--cyan)', marginTop: 5, flexShrink: 0 }} />
                      <div>
                        <p style={{ fontSize: 11, color: n.read ? 'var(--text-secondary)' : 'var(--text-primary)', lineHeight: 1.4 }}>{n.text}</p>
                        <p style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', marginTop: 2 }}>{n.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>

      {/* User Dropdown */}
      <div style={{ position: 'relative' }}>
        <button
          onClick={() => setShowUserMenu(!showUserMenu)}
          style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '3px 9px 3px 3px', borderRadius: 3, background: 'transparent', border: '1px solid var(--border-dim)', cursor: 'pointer', transition: 'all 0.12s' }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--border-base)' }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-dim)' }}
        >
          <div style={{ width: 24, height: 24, borderRadius: 3, background: 'linear-gradient(135deg, #00C8F0, #0284C7)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 9, fontWeight: 700, color: '#06080C', fontFamily: 'var(--mono)', flexShrink: 0, boxShadow: `0 0 0 2px ${provider.ring}` }}>
            {userInitials}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 1 }}>
            <span style={{ fontSize: 11, color: 'var(--text-primary)', fontWeight: 600, letterSpacing: '0.01em', lineHeight: 1 }}>{userName}</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 8, color: provider.color, letterSpacing: '0.04em', lineHeight: 1 }}>{provider.label.toUpperCase()}</span>
          </div>
          <ChevronDown size={10} style={{ color: 'var(--text-tertiary)' }} />
        </button>

        <AnimatePresence>
          {showUserMenu && (
            <>
              <div style={{ position: 'fixed', inset: 0, zIndex: 50 }} onClick={() => setShowUserMenu(false)} />
              <motion.div
                initial={{ opacity: 0, y: -6, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -4, scale: 0.97 }}
                transition={{ duration: 0.1 }}
                style={{ position: 'absolute', right: 0, top: 36, width: 220, borderRadius: 4, zIndex: 60, background: 'var(--bg-overlay)', border: '1px solid var(--border-base)', boxShadow: '0 16px 40px rgba(0,0,0,0.5)', overflow: 'hidden' }}
              >
                <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border-dim)', background: 'rgba(0,200,240,0.02)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 8 }}>
                    <div style={{ width: 34, height: 34, borderRadius: 6, background: 'linear-gradient(135deg, #00C8F0, #0284C7)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 800, color: '#06080C', fontFamily: 'var(--mono)', flexShrink: 0, boxShadow: `0 0 0 2px ${provider.ring}` }}>
                      {userInitials}
                    </div>
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2 }}>{userName}</div>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 140 }}>{user?.email || 'catalyst.user@agency.gov'}</div>
                      {user?.role && <div style={{ fontFamily: 'var(--mono)', fontSize: 8, color: '#64748B', marginTop: 2 }}>{user.role}</div>}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5, padding: '4px 8px', borderRadius: 4, background: `${provider.color}12`, border: `1px solid ${provider.color}30` }}>
                    <span style={{ width: 5, height: 5, borderRadius: '50%', background: provider.color, display: 'inline-block' }} />
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 8, color: provider.color, textTransform: 'uppercase', letterSpacing: '0.06em' }}>SIGNED IN VIA {provider.label}</span>
                  </div>
                </div>

                <div style={{ padding: 4 }}>
                  <button
                    onClick={handleSignOut}
                    style={{
                      width: '100%', display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
                      borderRadius: 3, background: 'transparent', border: 'none', color: '#F87171',
                      fontSize: 11, fontFamily: 'var(--mono)', cursor: 'pointer', textAlign: 'left',
                      transition: 'background 0.12s'
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(239,68,68,0.1)' }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
                  >
                    <LogOut size={12} /> SIGN OUT FROM CATALYST
                  </button>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>
    </header>
  )
}

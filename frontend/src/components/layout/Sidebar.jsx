import { useState, useEffect } from 'react'
import { NavLink, useNavigate, useLocation, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Database, Brain, FlaskConical, MessageSquare,
  GitBranch, Settings, HelpCircle, ChevronLeft, ChevronDown, Shield,
  Zap, Users, Cpu, BarChart2, Wrench, FolderKanban, DollarSign, TrendingUp, Scale, Fingerprint,
} from 'lucide-react'
import useAppStore from '../../store/useAppStore'

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Home', path: '/app/home' },
  {
    icon: Database, label: 'Data Studio', path: '/app/data-studio',
    children: [
      { icon: Database, label: 'DB Connectors', tab: 'connectors', path: '/app/data-studio?tab=connectors' },
      { icon: MessageSquare, label: 'DB Chatbot', tab: 'chatbot', path: '/app/data-studio?tab=chatbot' },
      { icon: GitBranch, label: 'ETL Pipelines', tab: 'pipelines', path: '/app/data-studio?tab=pipelines' },
    ],
  },
  {
    icon: Brain, label: 'AI Studio', path: '/app/ai-studio',
    children: [
      { icon: Zap, label: 'Multi Agent Orchestration', tab: 'v2', path: '/app/ai-studio?tab=v2' },
      { icon: MessageSquare, label: 'Conversation AI', tab: 'v1', path: '/app/ai-studio?tab=v1' },
      { icon: Users, label: 'Agents Fleet', tab: 'agents', path: '/app/ai-studio?tab=agents' },
      { icon: Cpu, label: 'ML Studio', tab: 'ml', path: '/app/ai-studio?tab=ml' },
    ],
  },
  {
    icon: FlaskConical, label: 'Experimental', path: '/app/experimental',
    children: [
      { icon: GitBranch, label: 'Experiments', tab: 'experiment', path: '/app/experimental?tab=experiment' },
      { icon: BarChart2, label: 'Simulations', tab: 'simulation', path: '/app/experimental?tab=simulation' },
    ],
  },
  {
    icon: Wrench, label: 'Tools', path: '/app/tools',
    children: [
      { icon: FolderKanban, label: 'Investigation Hub', tab: 'investigation', path: '/app/tools?tab=investigation' },
      { icon: BarChart2, label: 'Analytics & GIS', tab: 'analytics', path: '/app/tools?tab=analytics' },
      { icon: Users, label: 'Suspect Profiling', tab: 'profiling', path: '/app/tools?tab=profiling' },
      { icon: DollarSign, label: 'Financial Tracing', tab: 'finance', path: '/app/tools?tab=finance' },
      { icon: TrendingUp, label: 'Forecasting', tab: 'forecasting', path: '/app/tools?tab=forecasting' },
      { icon: Scale, label: 'XAI & Auditing', tab: 'xai', path: '/app/tools?tab=xai' },
    ],
  },
]

const BOTTOM_ITEMS = [
  { icon: Settings, label: 'Settings', path: '/app/settings' },
  { icon: HelpCircle, label: 'Help', path: '/app/help' },
]

export default function Sidebar() {
  const collapsed = useAppStore((s) => s.sidebarCollapsed)
  const toggleSidebar = useAppStore((s) => s.toggleSidebar)
  const navigate = useNavigate()

  return (
    <motion.aside
      animate={{ width: collapsed ? 52 : 240 }}
      transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
      style={{ position: 'fixed', top: 0, left: 0, height: '100%', zIndex: 50, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg-panel)', borderRight: '1px solid var(--border-dim)' }}
    >
      {/* Logo row */}
      <div style={{ display: 'flex', alignItems: 'center', height: 'var(--topbar-height)', padding: '0 10px', borderBottom: '1px solid var(--border-dim)', flexShrink: 0, gap: 8 }}>
        <button
          onClick={() => navigate('/')}
          style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0, background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
        >
          <div style={{ width: 28, height: 28, borderRadius: 6, background: '#0a1017', border: '1px solid #00d4ff', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flexShrink: 0, position: 'relative', boxShadow: '0 0 8px rgba(0,212,255,0.25)', overflow: 'hidden' }}>
            <Fingerprint size={10} style={{ color: '#00d4ff', position: 'absolute', top: 3 }} />
            <svg width="22" height="22" viewBox="0 0 24 24" style={{ position: 'absolute', top: 5 }}>
              <defs>
                <linearGradient id="vxGrad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#475569" />
                  <stop offset="100%" stopColor="#0f172a" />
                </linearGradient>
                <linearGradient id="vxCyan" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#00E5FF" />
                  <stop offset="100%" stopColor="#0088CC" />
                </linearGradient>
              </defs>
              <polygon points="3,4 12,21 16,21 7,4" fill="url(#vxGrad)" stroke="#1e293b" strokeWidth="0.5" />
              <polygon points="21,4 12,21 8,21 17,4" fill="url(#vxGrad)" stroke="#1e293b" strokeWidth="0.5" />
              <polygon points="5,21 12,12 15,12 8,21" fill="url(#vxGrad)" stroke="#1e293b" strokeWidth="0.5" />
              <polygon points="12,12 21,21 17,21 8,12" fill="url(#vxCyan)" />
            </svg>
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -6 }} transition={{ duration: 0.12 }} style={{ lineHeight: 1, minWidth: 0 }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 13, fontWeight: 800, letterSpacing: '0.08em', color: 'var(--text-primary)' }}>
                  VIGIL<span style={{ color: 'var(--cyan)' }}>X</span>
                </span>
                <p style={{ fontFamily: 'var(--mono)', fontSize: 8, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--text-tertiary)', marginTop: 1 }}>Intelligence</p>
              </motion.div>
            )}
          </AnimatePresence>
        </button>

        <button
          onClick={toggleSidebar}
          style={{ width: 22, height: 22, borderRadius: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-tertiary)', flexShrink: 0, transition: 'all 0.12s' }}
          onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.background = 'var(--bg-raised)' }}
          onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-tertiary)'; e.currentTarget.style.background = 'none' }}
        >
          <motion.div animate={{ rotate: collapsed ? 180 : 0 }} transition={{ duration: 0.22 }}>
            <ChevronLeft size={12} />
          </motion.div>
        </button>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: '6px 5px', display: 'flex', flexDirection: 'column', gap: 0 }}>
        {!collapsed && (
          <p className="section-label" style={{ padding: '4px 6px 5px', marginBottom: 2 }}>Navigation</p>
        )}
        {NAV_ITEMS.map((item) => (
          <SidebarItem key={item.path} item={item} collapsed={collapsed} />
        ))}
      </nav>

      {/* Bottom */}
      <div style={{ flexShrink: 0, padding: '5px', borderTop: '1px solid var(--border-dim)', display: 'flex', flexDirection: 'column', gap: 0 }}>
        {BOTTOM_ITEMS.map((item) => (
          <SidebarItem key={item.path} item={item} collapsed={collapsed} />
        ))}

        {/* User chip */}
        <div
          style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 7px', borderRadius: 2, marginTop: 4, cursor: 'pointer', transition: 'background 0.12s' }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-raised)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <div style={{ width: 26, height: 26, borderRadius: 2, background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 9, fontWeight: 700, color: '#fff', fontFamily: 'var(--mono)', flexShrink: 0 }}>OF</div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -6 }} transition={{ duration: 0.12 }} style={{ minWidth: 0 }}>
                <p style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.2 }}>Officer Admin</p>
                <p style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', marginTop: 1, letterSpacing: '0.04em' }}>L5 · CLEARANCE</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  )
}

function SidebarItem({ item, collapsed }) {
  const { icon: Icon, label, path, children } = item
  const location = useLocation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const isParentActive = location.pathname.startsWith(path)
  const [expanded, setExpanded] = useState(isParentActive)

  useEffect(() => { if (isParentActive) setExpanded(true) }, [isParentActive])

  const base = {
    display: 'flex', alignItems: 'center',
    justifyContent: collapsed ? 'center' : 'flex-start',
    gap: 8, padding: collapsed ? '7px' : '6px 8px',
    borderRadius: 2, cursor: 'pointer',
    transition: 'all 0.1s', position: 'relative',
    border: '1px solid transparent', userSelect: 'none',
    width: '100%', textAlign: 'left', background: 'none', outline: 'none',
    marginBottom: 1,
  }

  if (children?.length) {
    return (
      <div>
        <div
          onClick={() => { if (!isParentActive) navigate(path); setExpanded(!expanded) }}
          style={{ ...base, background: isParentActive ? 'rgba(139,92,246,0.07)' : 'transparent', borderColor: isParentActive ? 'rgba(139,92,246,0.14)' : 'transparent' }}
          onMouseEnter={(e) => { if (!isParentActive) e.currentTarget.style.background = 'var(--bg-raised)' }}
          onMouseLeave={(e) => { if (!isParentActive) e.currentTarget.style.background = 'transparent' }}
        >
          {isParentActive && <span style={{ position: 'absolute', left: 0, top: '50%', transform: 'translateY(-50%)', width: 2, height: 14, background: '#8B5CF6', borderRadius: '0 1px 1px 0' }} />}
          <Icon size={13} style={{ color: isParentActive ? '#8B5CF6' : 'var(--text-secondary)', flexShrink: 0 }} />
          {!collapsed && (
            <>
              <span style={{ flex: 1, fontSize: 12, fontWeight: 500, color: isParentActive ? 'var(--text-primary)' : 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{label}</span>
              <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.18 }} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }}>
                <ChevronDown size={11} />
              </motion.div>
            </>
          )}
        </div>

        <AnimatePresence>
          {expanded && !collapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.16 }}
              style={{ overflow: 'hidden', marginLeft: 12, paddingLeft: 10, borderLeft: '1px solid var(--border-dim)', marginTop: 1, marginBottom: 2 }}
            >
              {children.map((child) => {
                const raw = searchParams.get('tab')
                const def = path.includes('data-studio') ? 'connectors' : path.includes('ai-studio') ? 'v2' : 'experiment'
                const cur = raw || def
                const isActive = isParentActive && cur === child.tab
                const CI = child.icon
                return (
                  <NavLink key={child.path} to={child.path} style={{ textDecoration: 'none' }}>
                    <div
                      style={{ display: 'flex', alignItems: 'center', gap: 7, padding: '5px 7px', borderRadius: 2, marginBottom: 1, background: isActive ? 'rgba(0,200,240,0.06)' : 'transparent', border: `1px solid ${isActive ? 'rgba(0,200,240,0.1)' : 'transparent'}`, transition: 'all 0.1s', cursor: 'pointer' }}
                      onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = 'var(--bg-raised)' }}
                      onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = 'transparent' }}
                    >
                      <CI size={11} style={{ color: isActive ? 'var(--cyan)' : 'var(--text-tertiary)', flexShrink: 0 }} />
                      <span style={{ fontSize: 11, color: isActive ? 'var(--cyan)' : 'var(--text-secondary)', fontWeight: isActive ? 500 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{child.label}</span>
                    </div>
                  </NavLink>
                )
              })}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }

  return (
    <NavLink to={path} style={{ textDecoration: 'none' }}>
      {({ isActive }) => (
        <div
          style={{ ...base, background: isActive ? 'rgba(0,200,240,0.06)' : 'transparent', borderColor: isActive ? 'rgba(0,200,240,0.1)' : 'transparent' }}
          onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = 'var(--bg-raised)' }}
          onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = 'transparent' }}
        >
          {isActive && <span style={{ position: 'absolute', left: 0, top: '50%', transform: 'translateY(-50%)', width: 2, height: 14, background: 'var(--cyan)', borderRadius: '0 1px 1px 0' }} />}
          <Icon size={13} style={{ color: isActive ? 'var(--cyan)' : 'var(--text-secondary)', flexShrink: 0 }} />
          {!collapsed && (
            <span style={{ fontSize: 12, fontWeight: 500, color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>
              {label}
            </span>
          )}
        </div>
      )}
    </NavLink>
  )
}

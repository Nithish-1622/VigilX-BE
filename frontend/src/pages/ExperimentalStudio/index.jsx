import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FlaskConical, Play, Lock } from 'lucide-react'

const PAGE_TITLES = {
  experiment: { label: 'Experiments',  sub: 'A/B test prompt strategies and agent configurations' },
  simulation: { label: 'Simulations',  sub: 'Predictive scenario modeling and disruption analysis' },
}

const EXPERIMENTS = [
  {
    id: 1,
    name: 'Prompt Strategy A/B Test',
    desc: 'Compare accuracy of PlanningAgent with different system prompts.',
    status: 'ready',
  },
  {
    id: 2,
    name: 'Agent Configuration Alpha',
    desc: 'Test 5-agent pipeline vs 7-agent full pipeline on narcotics cases.',
    status: 'draft',
  },
]

const SIMULATIONS = [
  {
    id: 1,
    name: 'Harbor District — Gang Activity Surge',
    desc: 'Simulate 30% increase in gang activity based on Q2 historical data.',
    status: 'ready',
  },
  {
    id: 2,
    name: 'Narcotics Network Disruption',
    desc: 'What-if: Remove top 3 nodes from trafficking network.',
    status: 'draft',
  },
]

export default function ExperimentalStudio() {
  const [searchParams] = useSearchParams()
  const tabParam = searchParams.get('tab')
  const [tab, setTab] = useState(tabParam || 'experiment')

  useEffect(() => {
    if (tabParam && tabParam !== tab) setTab(tabParam)
  }, [tabParam])

  const current = PAGE_TITLES[tab] || PAGE_TITLES.experiment
  const items = tab === 'experiment' ? EXPERIMENTS : SIMULATIONS

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Page header */}
      <div style={{ paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <h1 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
            {current.label}
          </h1>
          <span className="tag-red" style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            <FlaskConical size={9} /> Beta
          </span>
        </div>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0 }}>{current.sub}</p>
      </div>

      {/* Item list */}
      <motion.div
        key={tab}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.15 }}
        style={{ display: 'flex', flexDirection: 'column', gap: 8 }}
      >
        {items.map((item, i) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06, duration: 0.18 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 14,
              padding: '14px 16px',
              borderRadius: 9,
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              transition: 'border-color 0.15s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'rgba(245,158,11,0.25)')}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
          >
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 8,
                background: 'rgba(245,158,11,0.08)',
                border: '1px solid rgba(245,158,11,0.18)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <FlaskConical size={16} style={{ color: 'var(--accent-orange)' }} />
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 3px' }}>
                {item.name}
              </p>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
                {item.desc}
              </p>
            </div>

            <span
              className={item.status === 'ready' ? 'tag-green' : 'tag-cyan'}
              style={{ textTransform: 'capitalize', flexShrink: 0 }}
            >
              {item.status}
            </span>

            <button
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 5,
                padding: '6px 12px',
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 500,
                color: 'var(--accent-orange)',
                background: 'rgba(245,158,11,0.07)',
                border: '1px solid rgba(245,158,11,0.2)',
                cursor: 'pointer',
                flexShrink: 0,
                transition: 'all 0.15s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(245,158,11,0.14)'
                e.currentTarget.style.borderColor = 'rgba(245,158,11,0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(245,158,11,0.07)'
                e.currentTarget.style.borderColor = 'rgba(245,158,11,0.2)'
              }}
            >
              <Play size={11} /> Run
            </button>
          </motion.div>
        ))}

        {/* Coming soon card */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 8,
            padding: '24px 16px',
            borderRadius: 9,
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            marginTop: 4,
            textAlign: 'center',
          }}
        >
          <Lock size={18} style={{ color: 'var(--text-muted)' }} />
          <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0 }}>
            Advanced simulation engine — coming in the next release.
          </p>
        </div>
      </motion.div>
    </div>
  )
}

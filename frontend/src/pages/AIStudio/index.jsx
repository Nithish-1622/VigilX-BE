import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import ChatV1 from './ChatV1'
import ChatV2 from './ChatV2'
import AgentsDirectory from './AgentsDirectory'
import MLPage from './MLPage'

const PAGE_TITLES = {
  v2: { label: 'Multi Agent Orchestration', sub: 'Coordinated AI agent pipeline with DAG execution' },
  v1: { label: 'Conversation AI', sub: 'Standard LLM conversational interface' },
  agents: { label: 'Agents Fleet', sub: '12 specialized agents · architecture & live status' },
  ml: { label: 'ML Studio', sub: 'Predictive models · training · evaluation' },
}

export default function AIStudio() {
  const [searchParams] = useSearchParams()
  const tabParam = searchParams.get('tab')
  const [tab, setTab] = useState(tabParam || 'v2')

  useEffect(() => {
    if (tabParam && tabParam !== tab) setTab(tabParam)
  }, [tabParam])

  const current = PAGE_TITLES[tab] || PAGE_TITLES.v2

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, height: '100%', padding: '32px 40px' }}>
      {/* Page header — title updates based on active tab */}
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
        style={{ flex: 1 }}
      >
        {tab === 'v2' && <ChatV2 />}
        {tab === 'v1' && <ChatV1 />}
        {tab === 'agents' && <AgentsDirectory />}
        {tab === 'ml' && <MLPage />}
      </motion.div>
    </div>
  )
}

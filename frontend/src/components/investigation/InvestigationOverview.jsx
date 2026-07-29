import React from 'react'
import { Target, Cpu, Compass } from 'lucide-react'

export default function InvestigationOverview({ intent, complexity = 'standard', userQuery }) {
  const formattedIntent = intent ? intent.replace(/_/g, ' ').toUpperCase() : 'MULTI-AGENT INVESTIGATION'
  
  return (
    <div style={{
      padding: '10px 14px',
      background: 'rgba(0, 200, 240, 0.03)',
      borderBottom: '1px solid var(--border-dim)',
      display: 'flex',
      flexDirection: 'column',
      gap: 6
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Target size={12} style={{ color: 'var(--cyan)' }} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.08em', color: 'var(--cyan)', fontWeight: 600 }}>
            INTENT: {formattedIntent}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Compass size={11} style={{ color: 'var(--purple)' }} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>
            STRATEGY: HYBRID (SQL + GRAPH + RAG)
          </span>
          <span className="tag-purple" style={{ fontSize: 9, padding: '1px 5px' }}>
            {complexity.toUpperCase()}
          </span>
        </div>
      </div>

      {userQuery && (
        <div style={{ fontSize: 11, color: 'var(--text-secondary)', fontStyle: 'italic', lineHeight: 1.4 }}>
          "{userQuery}"
        </div>
      )}
    </div>
  )
}

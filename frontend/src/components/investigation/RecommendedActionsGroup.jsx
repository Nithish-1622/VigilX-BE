import React from 'react'
import { TrendingUp, ArrowRight, ShieldCheck } from 'lucide-react'

const DEFAULT_RECOMMENDATIONS = [
  'Issue arrest warrant for suspect John Doe (Prior Robbery Conviction 2024)',
  'Impound escape vehicle motorcycle plate KA03MJ7890',
  'Cross-reference cell tower pings for burner phone +919876543210 near Indiranagar',
]

export default function RecommendedActionsGroup({ recommendations = [] }) {
  const list = recommendations.length > 0 ? recommendations : DEFAULT_RECOMMENDATIONS

  return (
    <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-dim)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <ShieldCheck size={12} style={{ color: 'var(--green)' }} />
        <span className="section-label" style={{ margin: 0 }}>RECOMMENDED INVESTIGATIVE ACTIONS</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {list.map((rec, i) => (
          <div key={i} style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 8,
            padding: '6px 10px',
            background: 'rgba(22, 163, 74, 0.04)',
            border: '1px solid rgba(22, 163, 74, 0.15)',
            borderRadius: 3
          }}>
            <ArrowRight size={11} style={{ color: 'var(--green)', marginTop: 2, flexShrink: 0 }} />
            <span style={{ fontSize: 11, color: 'var(--text-primary)', lineHeight: 1.4 }}>
              {rec}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

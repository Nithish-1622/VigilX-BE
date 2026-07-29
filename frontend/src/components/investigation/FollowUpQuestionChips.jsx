import React from 'react'
import { Sparkles, ArrowUpRight } from 'lucide-react'

const DEFAULT_FOLLOWUPS = [
  'Show Timeline of Case FIR-123',
  'Trace Associates of Suspect John Doe',
  'Export Full Intelligence Report (PDF)',
  'Find Similar Burglary Cases in Bengaluru',
]

export default function FollowUpQuestionChips({ onSelectPrompt }) {
  return (
    <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-dim)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <Sparkles size={11} style={{ color: 'var(--cyan)' }} />
        <span className="section-label" style={{ margin: 0 }}>SUGGESTED FOLLOW-UP INVESTIGATION QUERIES</span>
      </div>

      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {DEFAULT_FOLLOWUPS.map((q, i) => (
          <button
            key={i}
            onClick={() => onSelectPrompt && onSelectPrompt(q)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              padding: '4px 8px',
              background: 'var(--bg-row)',
              border: '1px solid var(--border-base)',
              borderRadius: 3,
              fontSize: 11,
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'border-color 0.12s, color 0.12s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--cyan)'
              e.currentTarget.style.color = 'var(--text-primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-base)'
              e.currentTarget.style.color = 'var(--text-secondary)'
            }}
          >
            <span>{q}</span>
            <ArrowUpRight size={10} style={{ color: 'var(--cyan)' }} />
          </button>
        ))}
      </div>
    </div>
  )
}

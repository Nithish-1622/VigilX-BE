import React from 'react'
import { Shield } from 'lucide-react'

function ConfBar({ value, color }) {
  return (
    <div className="conf-bar-track" style={{ width: 64, height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3, overflow: 'hidden' }}>
      <div className="conf-bar-fill" style={{ width: `${Math.min(100, Math.max(0, value * 100))}%`, background: color, height: '100%', transition: 'width 0.3s ease' }} />
    </div>
  )
}

function getThreatStyle(confidence = 0.85, criticPassed = true) {
  if (!criticPassed) return { label: 'CRITIC WARNING', tagClass: 'tag-amber', color: 'var(--amber)' }
  if (confidence >= 0.85) return { label: 'HIGH THREAT', tagClass: 'tag-red', color: 'var(--red)' }
  if (confidence >= 0.65) return { label: 'ELEVATED RISK', tagClass: 'tag-amber', color: 'var(--amber)' }
  return { label: 'ROUTINE INTEL', tagClass: 'tag-purple', color: 'var(--purple)' }
}

function getConfColor(val) {
  if (val >= 0.85) return 'var(--green)'
  if (val >= 0.65) return 'var(--amber)'
  return 'var(--red)'
}

export default function InvestigationHeader({ responseId, confidence = 0.88, confidenceLabel = 'high', criticPassed = true }) {
  const pct = Math.round(confidence * 100)
  const confColor = getConfColor(confidence)
  const threat = getThreatStyle(confidence, criticPassed)

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justify: 'space-between',
      padding: '8px 14px',
      background: 'var(--bg-row)',
      borderBottom: '1px solid var(--border-dim)',
      flexWrap: 'wrap',
      gap: 8
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Shield size={13} style={{ color: 'var(--cyan)' }} />
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, letterSpacing: '0.08em', color: 'var(--text-primary)' }}>
          CRIME INTELLIGENCE WORKSPACE
        </span>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--text-tertiary)' }}>
          #{responseId ? responseId.slice(0, 8).toUpperCase() : 'VX-2026'}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span className={threat.tagClass} style={{ fontSize: 9, letterSpacing: '0.06em', padding: '2px 7px' }}>
          {threat.label}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--text-tertiary)' }}>
            {confidenceLabel.toUpperCase()}
          </span>
          <ConfBar value={confidence} color={confColor} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 600, color: confColor }}>
            {pct}%
          </span>
        </div>
      </div>
    </div>
  )
}

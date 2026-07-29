import React from 'react'
import { Activity, Clock, ShieldAlert, BarChart3 } from 'lucide-react'

export default function DynamicVisualizationPanel({ timeline = [], chartSpecs = [] }) {
  const defaultTimeline = [
    { timestamp: '2026-07-10 02:00 AM', event: 'Commercial break-in & backpack theft', source: 'FIR-123' },
    { timestamp: '2026-07-10 02:15 AM', event: 'Suspect escaped on motorcycle plate KA03MJ7890', source: 'CCTV Feed' },
    { timestamp: '2026-07-11 10:30 AM', event: 'Burner phone +919876543210 pinged near Koramangala', source: 'Cell Tower' },
  ]

  const events = timeline.length > 0 ? timeline : defaultTimeline

  return (
    <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border-dim)', background: 'var(--bg-canvas)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
        <Activity size={12} style={{ color: 'var(--cyan)' }} />
        <span className="section-label" style={{ margin: 0 }}>INVESTIGATION TIMELINE & CHRONOLOGY</span>
      </div>

      <div style={{ position: 'relative', paddingLeft: 14, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {/* Vertical line track */}
        <div style={{
          position: 'absolute',
          left: 4,
          top: 4,
          bottom: 4,
          width: 2,
          background: 'var(--border-dim)'
        }} />

        {events.map((item, i) => (
          <div key={i} style={{ position: 'relative', display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Dot */}
            <div style={{
              position: 'absolute',
              left: -14,
              top: 4,
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: 'var(--cyan)',
              boxShadow: '0 0 6px var(--cyan)'
            }} />
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--cyan)', fontWeight: 600 }}>
                {item.timestamp || '2026-07-10'}
              </span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', background: 'var(--bg-row)', padding: '1px 5px', borderRadius: 2 }}>
                {item.source}
              </span>
            </div>
            <p style={{ fontSize: 11, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
              {item.event}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

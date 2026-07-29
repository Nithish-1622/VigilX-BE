import React, { useState } from 'react'
import { Filter, ChevronDown, ChevronUp, Search, Database } from 'lucide-react'

export default function QueryInterpretationCard({ metadata, intent }) {
  const [open, setOpen] = useState(false)
  const filters = metadata?.filters || metadata?.query_filters || {}
  const entities = metadata?.extracted_entities || []
  const hasDetails = Object.keys(filters).length > 0 || entities.length > 0

  if (!hasDetails && !intent) return null

  return (
    <div style={{
      borderBottom: '1px solid var(--border-dim)',
      background: 'var(--bg-panel)'
    }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%',
          padding: '8px 14px',
          display: 'flex',
          alignItems: 'center',
          justify: 'space-between',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: 'var(--text-secondary)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Search size={12} style={{ color: 'var(--cyan)' }} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.06em', fontWeight: 600 }}>
            QUERY INTERPRETATION & FILTERS
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>
            {entities.length} ENTITIES · {Object.keys(filters).length} FILTERS
          </span>
          {open ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </div>
      </button>

      {open && (
        <div style={{ padding: '0 14px 10px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {entities.length > 0 && (
            <div>
              <span className="section-label" style={{ fontSize: 9, marginBottom: 4, display: 'block' }}>Extracted Query Entities</span>
              <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                {entities.map((ent, i) => (
                  <span key={i} style={{
                    fontFamily: 'var(--mono)',
                    fontSize: 9,
                    color: 'var(--cyan)',
                    background: 'rgba(0, 200, 240, 0.08)',
                    border: '1px solid rgba(0, 200, 240, 0.2)',
                    padding: '2px 6px',
                    borderRadius: 2
                  }}>
                    {ent.type ? `${ent.type}: ` : ''}{ent.value || ent}
                  </span>
                ))}
              </div>
            </div>
          )}

          {Object.keys(filters).length > 0 && (
            <div>
              <span className="section-label" style={{ fontSize: 9, marginBottom: 4, display: 'block' }}>Active Search Constraints</span>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 6 }}>
                {Object.entries(filters).map(([k, v]) => (
                  <div key={k} style={{
                    padding: '4px 8px',
                    background: 'var(--bg-row)',
                    border: '1px solid var(--border-dim)',
                    borderRadius: 3,
                    fontFamily: 'var(--mono)',
                    fontSize: 10
                  }}>
                    <span style={{ color: 'var(--text-tertiary)' }}>{k}: </span>
                    <span style={{ color: 'var(--text-primary)' }}>{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

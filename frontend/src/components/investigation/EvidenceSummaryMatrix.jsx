import React, { useState } from 'react'
import { FileText, UserX, UserCheck, Car, Key, ChevronDown, ChevronUp } from 'lucide-react'

export default function EvidenceSummaryMatrix({ evidenceBundle }) {
  const [open, setOpen] = useState(false)
  const cases = evidenceBundle?.cases || evidenceBundle?.ranked_evidence?.filter(e => e.type === 'case') || []
  const suspects = evidenceBundle?.suspects || evidenceBundle?.ranked_evidence?.filter(e => e.type === 'suspect') || []
  const victims = evidenceBundle?.victims || evidenceBundle?.ranked_evidence?.filter(e => e.type === 'victim') || []
  const vehicles = evidenceBundle?.vehicles || []
  const clues = evidenceBundle?.clues || []

  const stats = [
    { label: 'CASES', count: cases.length || 3, icon: FileText, color: 'var(--cyan)' },
    { label: 'SUSPECTS', count: suspects.length || 2, icon: UserX, color: 'var(--red)' },
    { label: 'VICTIMS', count: victims.length || 1, icon: UserCheck, color: 'var(--green)' },
    { label: 'VEHICLES', count: vehicles.length || 2, icon: Car, color: 'var(--purple)' },
    { label: 'CLUES', count: clues.length || 1, icon: Key, color: 'var(--amber)' },
  ]

  return (
    <div style={{
      borderBottom: '1px solid var(--border-dim)',
      background: 'var(--bg-panel)'
    }}>
      <div style={{ padding: '10px 14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.06em', color: 'var(--text-secondary)', fontWeight: 600 }}>
            EVIDENCE CORRELATION MATRIX
          </span>
          <button
            onClick={() => setOpen(!open)}
            style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', color: 'var(--cyan)', fontSize: 10, cursor: 'pointer', fontFamily: 'var(--mono)' }}
          >
            {open ? 'HIDE DETAILS' : 'EXPAND DETAILS'}
            {open ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 6 }}>
          {stats.map((s, i) => {
            const Icon = s.icon
            return (
              <div key={i} style={{
                background: 'var(--bg-row)',
                border: '1px solid var(--border-dim)',
                borderRadius: 3,
                padding: '6px 8px',
                display: 'flex',
                alignItems: 'center',
                justify: 'space-between'
              }}>
                <div>
                  <p style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', margin: 0 }}>{s.label}</p>
                  <p style={{ fontFamily: 'var(--mono)', fontSize: 14, fontWeight: 700, color: s.color, margin: 0 }}>{s.count}</p>
                </div>
                <Icon size={14} style={{ color: s.color, opacity: 0.8 }} />
              </div>
            )
          })}
        </div>
      </div>

      {open && (
        <div style={{ padding: '0 14px 10px', display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-dim)', borderRadius: 3, padding: 8, fontFamily: 'var(--mono)', fontSize: 10 }}>
            <p style={{ color: 'var(--cyan)', margin: '0 0 4px 0' }}>• CASE: FIR-123 (Theft in Koramangala, Bengaluru)</p>
            <p style={{ color: 'var(--red)', margin: '0 0 4px 0' }}>• SUSPECT: John Doe (Prior Robbery Record in 2024)</p>
            <p style={{ color: 'var(--green)', margin: '0 0 4px 0' }}>• VICTIM: Jane Smith (Statement Recorded)</p>
            <p style={{ color: 'var(--amber)', margin: 0 }}>• CLUE: Phone +919876543210 (Linked to John Doe)</p>
          </div>
        </div>
      )}
    </div>
  )
}

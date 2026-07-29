import React from 'react'
import { FileText, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react'

function ConfBar({ value, color }) {
  return (
    <div style={{ width: 48, height: 5, background: 'rgba(255,255,255,0.1)', borderRadius: 2, overflow: 'hidden' }}>
      <div style={{ width: `${value * 100}%`, background: color, height: '100%' }} />
    </div>
  )
}

function getConfColor(val) {
  if (val >= 0.85) return '#16A34A'
  if (val >= 0.65) return '#D97706'
  return '#E53E3E'
}

export default function IntelligenceReportSection({ executiveSummary, keyFindings = [], criticPassed = true, criticWarnings = [] }) {
  return (
    <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border-dim)' }}>
      {/* Executive Summary */}
      <div style={{ marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 5 }}>
          <FileText size={12} style={{ color: 'var(--cyan)' }} />
          <span className="section-label" style={{ margin: 0 }}>Executive Summary</span>
        </div>
        <p style={{ fontSize: 12, color: 'var(--text-primary)', lineHeight: 1.6, margin: 0 }}>
          {executiveSummary || 'Based on multi-agent intelligence retrieval across database records and network graphs, the investigation identified linked suspects, modus operandi matches, and associated vehicles.'}
        </p>
      </div>

      {/* Critic Warnings Banner if any */}
      {(!criticPassed || criticWarnings.length > 0) && (
        <div style={{
          marginBottom: 12,
          padding: '8px 10px',
          background: 'rgba(217, 119, 6, 0.08)',
          border: '1px solid rgba(217, 119, 6, 0.25)',
          borderRadius: 3,
          display: 'flex',
          gap: 8,
          alignItems: 'flex-start'
        }}>
          <ShieldAlert size={14} style={{ color: 'var(--amber)', marginTop: 1, flexShrink: 0 }} />
          <div>
            <p style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 600, color: 'var(--amber)', margin: '0 0 2px 0' }}>
              RESPONSE CRITIC AUDIT WARN
            </p>
            {criticWarnings.map((w, i) => (
              <p key={i} style={{ fontSize: 11, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
                • {w}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Key Findings Table */}
      {keyFindings.length > 0 && (
        <div>
          <span className="section-label" style={{ marginBottom: 6, display: 'block' }}>Key Intelligence Findings</span>
          <table className="data-table" style={{ width: '100%' }}>
            <thead>
              <tr>
                <th style={{ width: '55%' }}>Finding</th>
                <th>Confidence</th>
                <th>Source Agents</th>
              </tr>
            </thead>
            <tbody>
              {keyFindings.map((f, i) => {
                const conf = f.confidence || 0.9
                const fc = getConfColor(conf)
                return (
                  <tr key={i}>
                    <td style={{ color: 'var(--text-primary)', fontSize: 12, whiteSpace: 'normal', lineHeight: 1.4 }}>
                      {f.finding}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <ConfBar value={conf} color={fc} />
                        <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: fc }}>{Math.round(conf * 100)}%</span>
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                        {f.source_agents?.map(a => (
                          <span key={a} style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--purple)', background: 'rgba(139,92,246,0.07)', border: '1px solid rgba(139,92,246,0.15)', padding: '1px 5px', borderRadius: 2 }}>
                            {a.replace('Agent', '')}
                          </span>
                        )) || (
                          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--cyan)', background: 'rgba(0,200,240,0.07)', padding: '1px 5px', borderRadius: 2 }}>
                            SQL+Graph
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

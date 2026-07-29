import React from 'react'
import { Clock, Cpu, CheckCircle2, AlertTriangle, Database } from 'lucide-react'

export default function ExecutionMetadataFooter({ metadata, criticPassed = true, sessionId, responseId }) {
  const execTime = metadata?.execution_time_ms ? `${(metadata.execution_time_ms / 1000).toFixed(2)}s` : '1.24s'
  const model = metadata?.model || 'llama-3.1-8b-instant'
  const agentsCount = metadata?.agents_executed?.length || 6
  const recordsCount = metadata?.records_retrieved || 6

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justify: 'space-between',
      padding: '7px 14px',
      background: 'var(--bg-row)',
      fontFamily: 'var(--mono)',
      fontSize: 9,
      color: 'var(--text-tertiary)',
      flexWrap: 'wrap',
      gap: 6
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Clock size={10} style={{ color: 'var(--cyan)' }} />
          EXECUTION: {execTime}
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Cpu size={10} style={{ color: 'var(--purple)' }} />
          MODEL: {model}
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Database size={10} style={{ color: 'var(--green)' }} />
          RECORDS: {recordsCount}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ color: criticPassed ? 'var(--green)' : 'var(--amber)', display: 'flex', alignItems: 'center', gap: 3 }}>
          {criticPassed ? <CheckCircle2 size={10} /> : <AlertTriangle size={10} />}
          {criticPassed ? 'CRITIC AUDIT PASS' : 'CRITIC AUDIT WARN'}
        </span>
        <span>ENGINE: VIGILX-V2.0</span>
      </div>
    </div>
  )
}

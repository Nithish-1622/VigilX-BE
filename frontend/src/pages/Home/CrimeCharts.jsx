import {
  ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'

const WEEKLY = [
  { day: 'MON', narcotics: 12, assault: 7,  gang: 4,  theft: 18 },
  { day: 'TUE', narcotics: 9,  assault: 11, gang: 6,  theft: 14 },
  { day: 'WED', narcotics: 15, assault: 8,  gang: 9,  theft: 21 },
  { day: 'THU', narcotics: 18, assault: 13, gang: 11, theft: 16 },
  { day: 'FRI', narcotics: 22, assault: 17, gang: 14, theft: 28 },
  { day: 'SAT', narcotics: 31, assault: 24, gang: 19, theft: 35 },
  { day: 'SUN', narcotics: 27, assault: 19, gang: 15, theft: 29 },
]

const MONTHLY = [
  { month: 'JAN', resolved: 28, open: 14 },
  { month: 'FEB', resolved: 34, open: 11 },
  { month: 'MAR', resolved: 29, open: 17 },
  { month: 'APR', resolved: 42, open: 9 },
  { month: 'MAY', resolved: 38, open: 13 },
  { month: 'JUN', resolved: 47, open: 8 },
  { month: 'JUL', resolved: 28, open: 19 },
]

const SERIES = [
  { key: 'narcotics', color: '#E53E3E', label: 'Narcotics' },
  { key: 'assault',   color: '#D97706', label: 'Assault' },
  { key: 'gang',      color: '#8B5CF6', label: 'Gang' },
  { key: 'theft',     color: '#00C8F0', label: 'Theft' },
]

const monoStyle = { fontFamily: "'JetBrains Mono', monospace", fontSize: 10, letterSpacing: '0.04em' }

function MonoAxisTick({ x, y, payload }) {
  return (
    <text x={x} y={y + 10} textAnchor="middle" style={monoStyle} fill="var(--text-tertiary)">
      {payload.value}
    </text>
  )
}

function MonoYTick({ x, y, payload }) {
  return (
    <text x={x - 6} y={y + 4} textAnchor="end" style={monoStyle} fill="var(--text-tertiary)">
      {payload.value}
    </text>
  )
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: 'var(--bg-overlay)', border: '1px solid var(--border-base)', borderRadius: 3, padding: '8px 12px', minWidth: 140 }}>
      <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, color: 'var(--text-tertiary)', letterSpacing: '0.08em', marginBottom: 6, textTransform: 'uppercase' }}>{label}</p>
      {payload.map(p => (
        <div key={p.dataKey} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, marginBottom: 2 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <div style={{ width: 6, height: 6, borderRadius: 1, background: p.color }} />
            <span style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{p.dataKey}</span>
          </div>
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: 'var(--text-primary)', fontWeight: 600 }}>{p.value}</span>
        </div>
      ))}
    </div>
  )
}

function BarTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: 'var(--bg-overlay)', border: '1px solid var(--border-base)', borderRadius: 3, padding: '8px 12px' }}>
      <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, color: 'var(--text-tertiary)', letterSpacing: '0.08em', marginBottom: 6 }}>{label}</p>
      {payload.map(p => (
        <div key={p.dataKey} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 14, marginBottom: 2 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <div style={{ width: 6, height: 6, borderRadius: 1, background: p.color || p.fill }} />
            <span style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{p.dataKey}</span>
          </div>
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: 'var(--text-primary)', fontWeight: 600 }}>{p.value}</span>
        </div>
      ))}
    </div>
  )
}

const GRID_STYLE = { stroke: 'var(--border-dim)', strokeDasharray: '2 4' }

export default function CrimeCharts() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, height: '100%' }}>

      {/* Area chart */}
      <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-dim)', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 14px', borderBottom: '1px solid var(--border-dim)', background: 'var(--bg-row)' }}>
          <div>
            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>Incident Frequency</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', marginLeft: 8 }}>7-DAY · BY TYPE</span>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            {SERIES.map(s => (
              <div key={s.key} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <div style={{ width: 12, height: 2, background: s.color, borderRadius: 1 }} />
                <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>{s.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div style={{ padding: '12px 4px 8px 0' }}>
          <ResponsiveContainer width="100%" height={160}>
            <AreaChart data={WEEKLY} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
              <defs>
                {SERIES.map(s => (
                  <linearGradient key={s.key} id={`g-${s.key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={s.color} stopOpacity={0.18} />
                    <stop offset="100%" stopColor={s.color} stopOpacity={0} />
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid vertical={false} {...GRID_STYLE} />
              <XAxis dataKey="day" tick={<MonoAxisTick />} axisLine={false} tickLine={false} />
              <YAxis tick={<MonoYTick />} axisLine={false} tickLine={false} width={28} />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'var(--border-base)', strokeWidth: 1 }} />
              {SERIES.map(s => (
                <Area key={s.key} type="monotone" dataKey={s.key}
                  stroke={s.color} strokeWidth={1.5}
                  fill={`url(#g-${s.key})`}
                  dot={false} activeDot={{ r: 3, strokeWidth: 0, fill: s.color }}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bar chart */}
      <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-dim)', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 14px', borderBottom: '1px solid var(--border-dim)', background: 'var(--bg-row)' }}>
          <div>
            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>Case Resolution</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', marginLeft: 8 }}>7-MONTH · RESOLVED vs OPEN</span>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            {[['resolved', '#16A34A'], ['open', '#E53E3E']].map(([k, c]) => (
              <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <div style={{ width: 8, height: 8, borderRadius: 1, background: c }} />
                <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>{k}</span>
              </div>
            ))}
          </div>
        </div>
        <div style={{ padding: '12px 4px 8px 0' }}>
          <ResponsiveContainer width="100%" height={120}>
            <BarChart data={MONTHLY} barSize={10} barCategoryGap="35%" margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid vertical={false} {...GRID_STYLE} />
              <XAxis dataKey="month" tick={<MonoAxisTick />} axisLine={false} tickLine={false} />
              <YAxis tick={<MonoYTick />} axisLine={false} tickLine={false} width={28} />
              <Tooltip content={<BarTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
              <Bar dataKey="resolved" fill="#16A34A" opacity={0.8} radius={[1, 1, 0, 0]} />
              <Bar dataKey="open"     fill="#E53E3E" opacity={0.8} radius={[1, 1, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  )
}

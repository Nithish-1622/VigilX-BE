import React from 'react'
import { User, MapPin, Car, Phone, Mail, FileText, Key, Shield, Tag } from 'lucide-react'

const DEFAULT_ENTITIES = [
  { type: 'person', name: 'John Doe', role: 'Suspect', icon: User, color: 'var(--red)', bg: 'rgba(229, 62, 62, 0.08)', border: 'rgba(229, 62, 62, 0.25)' },
  { type: 'person', name: 'Jane Smith', role: 'Victim', icon: User, color: 'var(--green)', bg: 'rgba(22, 163, 74, 0.08)', border: 'rgba(22, 163, 74, 0.25)' },
  { type: 'location', name: 'Koramangala, Bengaluru', role: 'Crime Scene', icon: MapPin, color: 'var(--cyan)', bg: 'rgba(0, 200, 240, 0.08)', border: 'rgba(0, 200, 240, 0.25)' },
  { type: 'phone', name: '+919876543210', role: 'Burner Phone', icon: Phone, color: 'var(--amber)', bg: 'rgba(217, 119, 6, 0.08)', border: 'rgba(217, 119, 6, 0.25)' },
  { type: 'fir', name: 'FIR-123', role: 'Primary Case', icon: FileText, color: 'var(--purple)', bg: 'rgba(139, 92, 246, 0.08)', border: 'rgba(139, 92, 246, 0.25)' },
]

function getEntityConfig(ent) {
  const type = (ent.entity_type || ent.type || '').toLowerCase()
  if (type.includes('person') || type.includes('suspect') || type.includes('accused')) {
    return { icon: User, color: 'var(--red)', bg: 'rgba(229, 62, 62, 0.08)', border: 'rgba(229, 62, 62, 0.25)' }
  }
  if (type.includes('victim')) {
    return { icon: User, color: 'var(--green)', bg: 'rgba(22, 163, 74, 0.08)', border: 'rgba(22, 163, 74, 0.25)' }
  }
  if (type.includes('loc') || type.includes('address')) {
    return { icon: MapPin, color: 'var(--cyan)', bg: 'rgba(0, 200, 240, 0.08)', border: 'rgba(0, 200, 240, 0.25)' }
  }
  if (type.includes('veh') || type.includes('plate') || type.includes('car')) {
    return { icon: Car, color: 'var(--purple)', bg: 'rgba(139, 92, 246, 0.08)', border: 'rgba(139, 92, 246, 0.25)' }
  }
  if (type.includes('phone') || type.includes('contact')) {
    return { icon: Phone, color: 'var(--amber)', bg: 'rgba(217, 119, 6, 0.08)', border: 'rgba(217, 119, 6, 0.25)' }
  }
  if (type.includes('mail')) {
    return { icon: Mail, color: 'var(--cyan)', bg: 'rgba(0, 200, 240, 0.08)', border: 'rgba(0, 200, 240, 0.25)' }
  }
  return { icon: Tag, color: 'var(--cyan)', bg: 'rgba(0, 200, 240, 0.08)', border: 'rgba(0, 200, 240, 0.25)' }
}

export default function EntityBadgesGroup({ relatedEntities = [] }) {
  const entities = relatedEntities.length > 0 ? relatedEntities : DEFAULT_ENTITIES

  return (
    <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-dim)' }}>
      <span className="section-label" style={{ marginBottom: 8, display: 'block' }}>IDENTIFIED CASE ENTITIES & RELATIONS</span>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {entities.map((ent, i) => {
          const cfg = getEntityConfig(ent)
          const Icon = ent.icon || cfg.icon
          const color = ent.color || cfg.color
          const bg = ent.bg || cfg.bg
          const border = ent.border || cfg.border

          return (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '4px 8px',
              background: bg,
              border: `1px solid ${border}`,
              borderRadius: 3,
              fontSize: 11
            }}>
              <Icon size={11} style={{ color }} />
              <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{ent.name}</span>
              {ent.role && (
                <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color, opacity: 0.85, background: 'rgba(0,0,0,0.2)', padding: '1px 4px', borderRadius: 2 }}>
                  {ent.role}
                </span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

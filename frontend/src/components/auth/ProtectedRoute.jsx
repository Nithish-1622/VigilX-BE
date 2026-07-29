import { useEffect } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { Shield, Loader2 } from 'lucide-react'
import useAuthStore from '../../store/useAuthStore'

export default function ProtectedRoute() {
  const location = useLocation()
  const { isAuthenticated, loading, checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [])

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', background: '#06080C', color: '#E8EDF5'
      }}>
        <div style={{
          width: 44, height: 44, borderRadius: 6, background: 'rgba(0, 200, 240, 0.08)',
          border: '1px solid rgba(0, 200, 240, 0.25)', display: 'flex', alignItems: 'center',
          justifyContent: 'center', marginBottom: 20, boxShadow: '0 0 20px rgba(0, 200, 240, 0.2)'
        }}>
          <Shield size={22} style={{ color: '#00C8F0' }} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <Loader2 size={16} className="animate-spin" style={{ color: '#00C8F0' }} />
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 12, fontWeight: 700, letterSpacing: '0.12em', color: '#E8EDF5' }}>
            VERIFYING CATALYST SESSION...
          </span>
        </div>
        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#475569', letterSpacing: '0.08em' }}>
          CLASSIFIED ENVIRONMENT · AUTHORIZED ACCESS ONLY
        </span>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}

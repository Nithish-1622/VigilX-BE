import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import useAuthStore from '../../store/useAuthStore'

/**
 * OAuthCallback — handles the browser return from Google / Zoho OAuth redirect.
 *
 * Zoho Catalyst sets the ZGS session cookie on the browser after OAuth.
 * This page reads the session via checkIsAuthenticated(), updates Zustand state,
 * and redirects the user to the app dashboard.
 */
export default function OAuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { handleOAuthCallback } = useAuthStore()

  const [status, setStatus] = useState('loading')   // 'loading' | 'success' | 'error'
  const [errorMsg, setErrorMsg] = useState('')
  const provider = searchParams.get('provider') || 'OAuth'
  const isMock = searchParams.get('mock') === '1'

  useEffect(() => {
    const processCallback = async () => {
      try {
        // Small delay to let the ZGS cookie settle after redirect
        await new Promise(r => setTimeout(r, 800))

        const result = await handleOAuthCallback()

        if (result.success) {
          setStatus('success')
          setTimeout(() => navigate('/app/home', { replace: true }), 1200)
        } else {
          setStatus('error')
          setErrorMsg(result.error || 'Authentication failed. Please try again.')
          setTimeout(() => navigate('/login', { replace: true }), 2500)
        }
      } catch (err) {
        setStatus('error')
        setErrorMsg(err?.message || 'An unexpected error occurred.')
        setTimeout(() => navigate('/login', { replace: true }), 2500)
      }
    }

    processCallback()
  }, [])

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      background: '#06080C', color: '#E8EDF5',
      fontFamily: "'Plus Jakarta Sans', sans-serif",
    }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.35 }}
        style={{
          textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18,
          background: 'rgba(10, 14, 22, 0.92)', border: '1px solid rgba(0, 200, 240, 0.25)',
          borderRadius: 16, padding: '40px 48px',
          boxShadow: '0 0 50px rgba(0, 200, 240, 0.15)',
        }}
      >
        {/* Icon */}
        {status === 'loading' && (
          <div style={{ width: 52, height: 52, borderRadius: 14, background: 'rgba(0, 200, 240, 0.1)', border: '1px solid rgba(0, 200, 240, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 24px rgba(0, 200, 240, 0.25)' }}>
            <Loader2 size={26} style={{ color: '#00C8F0', animation: 'spin 1s linear infinite' }} />
          </div>
        )}
        {status === 'success' && (
          <div style={{ width: 52, height: 52, borderRadius: 14, background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <CheckCircle2 size={26} style={{ color: '#10B981' }} />
          </div>
        )}
        {status === 'error' && (
          <div style={{ width: 52, height: 52, borderRadius: 14, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <AlertCircle size={26} style={{ color: '#EF4444' }} />
          </div>
        )}

        {/* Text */}
        <div>
          <h2 style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 15, fontWeight: 800, color: '#FFFFFF', margin: '0 0 8px', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            {status === 'loading' && `Verifying ${provider} Session...`}
            {status === 'success' && 'Authentication Successful'}
            {status === 'error' && 'Authentication Failed'}
          </h2>
          <p style={{ fontSize: 12, color: '#64748B', margin: 0, lineHeight: 1.5 }}>
            {status === 'loading' && 'Establishing secure Catalyst session. Please wait.'}
            {status === 'success' && 'ZGS session verified. Redirecting to Intelligence Portal...'}
            {status === 'error' && (errorMsg || 'Redirecting to login page...')}
          </p>
        </div>

        {/* Progress bar */}
        {status === 'loading' && (
          <div style={{ width: 220, height: 3, background: 'rgba(255,255,255,0.08)', borderRadius: 4, overflow: 'hidden' }}>
            <motion.div
              initial={{ width: '0%' }} animate={{ width: '100%' }}
              transition={{ duration: 1.5, ease: 'easeInOut', repeat: Infinity }}
              style={{ height: '100%', background: 'linear-gradient(90deg, #00C8F0, #8B5CF6)', borderRadius: 4 }}
            />
          </div>
        )}

        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#1E293B', letterSpacing: '0.06em' }}>
          TS//SCI · ZOHO CATALYST ZGS SESSION
        </span>
      </motion.div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

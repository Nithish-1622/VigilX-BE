import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Mail, ArrowLeft, CheckCircle2, AlertCircle, Loader2, KeyRound } from 'lucide-react'
import useAuthStore from '../../store/useAuthStore'
import ParticleNetwork from '../../components/three/ParticleNetwork'

export default function ForgotPassword() {
  const navigate = useNavigate()
  const location = useLocation()

  const { forgotPassword, error, clearError } = useAuthStore()

  const initialEmail = new URLSearchParams(location.search).get('email') || ''
  const [email, setEmail] = useState(initialEmail)
  const [sent, setSent] = useState(false)
  const [localError, setLocalError] = useState('')
  const [formLoading, setFormLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLocalError('')
    clearError()

    if (!email) { setLocalError('Please enter your email address.'); return }

    setFormLoading(true)
    const res = await forgotPassword(email)
    setFormLoading(false)
    if (res.success) {
      setSent(true)
    } else {
      setLocalError(res.error || 'Failed to send reset email. Please try again.')
    }
  }

  const displayError = localError || error

  return (
    <div style={{
      position: 'relative', minHeight: '100vh', background: '#06080C', color: '#E8EDF5',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: "'Plus Jakarta Sans', 'Inter', sans-serif", overflow: 'hidden',
    }}>
      {/* Background */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
        <ParticleNetwork style={{ opacity: 0.35 }} />
        <div style={{ position: 'absolute', top: -100, left: -100, width: 600, height: 600, borderRadius: '50%', background: 'radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.35) 0%, rgba(0, 200, 240, 0.1) 45%, transparent 70%)', filter: 'blur(70px)' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(6, 8, 12, 0.75)' }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 18, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.38 }}
        style={{
          position: 'relative', zIndex: 10, width: '100%', maxWidth: 430, margin: '24px',
          background: 'rgba(10, 14, 22, 0.94)', border: '1px solid rgba(0, 200, 240, 0.28)',
          borderRadius: 18, padding: '38px 34px',
          boxShadow: '0 0 55px rgba(0, 200, 240, 0.16), inset 0 1px 0 rgba(255,255,255,0.05)',
          backdropFilter: 'blur(28px)',
        }}
      >
        {/* Back Button */}
        <button onClick={() => navigate('/login')} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', color: '#64748B', fontSize: 12, cursor: 'pointer', padding: 0, marginBottom: 24 }}>
          <ArrowLeft size={13} /> Back to Sign In
        </button>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 48, height: 48, borderRadius: 13, background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)', marginBottom: 14, boxShadow: '0 0 24px rgba(139, 92, 246, 0.2)' }}>
            <KeyRound size={24} style={{ color: '#A855F7' }} />
          </div>
          <h1 style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 16, fontWeight: 800, letterSpacing: '0.1em', color: '#FFFFFF', margin: '0 0 8px' }}>
            RESET PASSWORD
          </h1>
          <p style={{ fontSize: 12, color: '#64748B', margin: 0, lineHeight: 1.55 }}>
            Enter your registered email. Catalyst will send a secure reset link to your inbox.
          </p>
        </div>

        {/* Success State */}
        {sent ? (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, padding: '24px 16px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: 12, textAlign: 'center', marginBottom: 20 }}>
              <CheckCircle2 size={32} style={{ color: '#10B981' }} />
              <div>
                <p style={{ fontSize: 14, fontWeight: 700, color: '#10B981', margin: '0 0 6px' }}>Reset Link Sent!</p>
                <p style={{ fontSize: 12, color: '#6EE7B7', margin: 0, lineHeight: 1.5 }}>
                  A password reset link has been sent to <strong>{email}</strong>. Check your inbox and follow the link to set a new password.
                </p>
              </div>
            </div>
            <p style={{ fontSize: 11, color: '#475569', textAlign: 'center', lineHeight: 1.5 }}>
              Didn't receive the email? Check your spam folder or{' '}
              <button onClick={() => setSent(false)} style={{ background: 'none', border: 'none', color: '#00C8F0', cursor: 'pointer', fontSize: 11, padding: 0 }}>try again</button>.
            </p>
          </motion.div>
        ) : (
          <>
            {/* Error Alert */}
            <AnimatePresence>
              {displayError && (
                <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '11px 14px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.28)', borderRadius: 8, marginBottom: 18 }}>
                  <AlertCircle size={15} style={{ color: '#EF4444', flexShrink: 0, marginTop: 1 }} />
                  <span style={{ fontSize: 12, color: '#FCA5A5', lineHeight: 1.45 }}>{displayError}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Form */}
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'block', fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#94A3B8', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 7 }}>
                  OFFICIAL EMAIL ADDRESS
                </label>
                <div style={{ position: 'relative' }}>
                  <Mail size={15} style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', color: '#64748B', pointerEvents: 'none' }} />
                  <input
                    type="email" value={email} onChange={e => setEmail(e.target.value)}
                    placeholder="officer@agency.gov" required
                    style={{ width: '100%', height: 44, paddingLeft: 38, paddingRight: 14, background: 'rgba(6, 8, 12, 0.95)', border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: 8, color: '#E8EDF5', fontSize: 13, outline: 'none', transition: 'all 0.18s', boxSizing: 'border-box' }}
                    onFocus={e => { e.target.style.borderColor = '#A855F7'; e.target.style.boxShadow = '0 0 0 3px rgba(168, 85, 247, 0.12)' }}
                    onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'; e.target.style.boxShadow = 'none' }}
                  />
                </div>
              </div>

              <button type="submit" disabled={loading}
                style={{
                  width: '100%', height: 44, background: loading ? 'rgba(139, 92, 246, 0.4)' : 'linear-gradient(135deg, #8B5CF6, #00C8F0)', border: 'none', borderRadius: 8,
                  color: '#FFF', fontSize: 12, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.08em',
                  cursor: loading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  boxShadow: loading ? 'none' : '0 0 22px rgba(139, 92, 246, 0.35)', transition: 'all 0.2s',
                }}>
                {loading ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> SENDING RESET LINK...</> : <><KeyRound size={14} /> SEND RESET LINK</>}
              </button>
            </form>
          </>
        )}

        <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.07)', textAlign: 'center' }}>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#1E293B', letterSpacing: '0.07em' }}>
            ZOHO CATALYST SECURE PASSWORD RESET
          </span>
        </div>
      </motion.div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

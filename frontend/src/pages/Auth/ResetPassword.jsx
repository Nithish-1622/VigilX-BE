import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Lock, Eye, EyeOff, CheckCircle2, AlertCircle, Loader2, ShieldCheck, ArrowRight } from 'lucide-react'
import useAuthStore from '../../store/useAuthStore'
import ParticleNetwork from '../../components/three/ParticleNetwork'

export default function ResetPassword() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const { resetPassword, loading, error, clearError } = useAuthStore()

  const token = searchParams.get('token') || searchParams.get('reset_token') || ''
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [done, setDone] = useState(false)
  const [localError, setLocalError] = useState('')

  const strength = getPasswordStrength(password)

  useEffect(() => {
    if (!token) {
      setLocalError('Invalid or expired reset link. Please request a new one.')
    }
  }, [token])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLocalError('')
    clearError()

    if (password.length < 8) { setLocalError('Password must be at least 8 characters.'); return }
    if (password !== confirmPassword) { setLocalError('Passwords do not match.'); return }
    if (!token) { setLocalError('Invalid reset token. Please request a new reset link.'); return }

    const res = await resetPassword(token, password)
    if (res.success) {
      setDone(true)
      setTimeout(() => navigate('/login'), 3000)
    } else {
      setLocalError(res.error || 'Password reset failed. The link may have expired.')
    }
  }

  const displayError = localError || error

  return (
    <div style={{
      position: 'relative', minHeight: '100vh', background: '#06080C', color: '#E8EDF5',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: "'Plus Jakarta Sans', 'Inter', sans-serif", overflow: 'hidden',
    }}>
      <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
        <ParticleNetwork style={{ opacity: 0.35 }} />
        <div style={{ position: 'absolute', top: -100, right: -100, width: 550, height: 550, borderRadius: '50%', background: 'radial-gradient(circle at 70% 30%, rgba(16, 185, 129, 0.2) 0%, rgba(0, 200, 240, 0.1) 45%, transparent 70%)', filter: 'blur(70px)' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(6, 8, 12, 0.75)' }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 18, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.38 }}
        style={{
          position: 'relative', zIndex: 10, width: '100%', maxWidth: 430, margin: '24px',
          background: 'rgba(10, 14, 22, 0.94)', border: '1px solid rgba(16, 185, 129, 0.28)',
          borderRadius: 18, padding: '38px 34px',
          boxShadow: '0 0 55px rgba(16, 185, 129, 0.12), inset 0 1px 0 rgba(255,255,255,0.05)',
          backdropFilter: 'blur(28px)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 48, height: 48, borderRadius: 13, background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', marginBottom: 14, boxShadow: '0 0 24px rgba(16, 185, 129, 0.2)' }}>
            <ShieldCheck size={24} style={{ color: '#10B981' }} />
          </div>
          <h1 style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 16, fontWeight: 800, letterSpacing: '0.1em', color: '#FFFFFF', margin: '0 0 8px' }}>
            SET NEW PASSWORD
          </h1>
          <p style={{ fontSize: 12, color: '#64748B', margin: 0, lineHeight: 1.55 }}>
            Create a new strong password for your VigilX intelligence account.
          </p>
        </div>

        {done ? (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, padding: '24px 16px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: 12, textAlign: 'center' }}>
              <CheckCircle2 size={32} style={{ color: '#10B981' }} />
              <div>
                <p style={{ fontSize: 14, fontWeight: 700, color: '#10B981', margin: '0 0 6px' }}>Password Reset Successful!</p>
                <p style={{ fontSize: 12, color: '#6EE7B7', margin: 0, lineHeight: 1.5 }}>Your new password has been set. Redirecting to sign-in page...</p>
              </div>
            </div>
          </motion.div>
        ) : (
          <>
            <AnimatePresence>
              {displayError && (
                <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '11px 14px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.28)', borderRadius: 8, marginBottom: 18 }}>
                  <AlertCircle size={15} style={{ color: '#EF4444', flexShrink: 0, marginTop: 1 }} />
                  <span style={{ fontSize: 12, color: '#FCA5A5', lineHeight: 1.45 }}>{displayError}</span>
                </motion.div>
              )}
            </AnimatePresence>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#94A3B8', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 7 }}>NEW PASSWORD</label>
                <div style={{ position: 'relative' }}>
                  <Lock size={15} style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', color: '#64748B', pointerEvents: 'none' }} />
                  <input type={showPassword ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="Minimum 8 characters" required
                    style={{ width: '100%', height: 44, paddingLeft: 38, paddingRight: 42, background: 'rgba(6, 8, 12, 0.95)', border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: 8, color: '#E8EDF5', fontSize: 13, outline: 'none', transition: 'all 0.18s', boxSizing: 'border-box' }}
                    onFocus={e => { e.target.style.borderColor = '#10B981'; e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.12)' }}
                    onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'; e.target.style.boxShadow = 'none' }}
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#64748B', cursor: 'pointer', padding: 2 }}>
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
                {password.length > 0 && (
                  <div style={{ marginTop: 8 }}>
                    <div style={{ display: 'flex', gap: 4, marginBottom: 4 }}>
                      {[0, 1, 2, 3].map(i => (
                        <div key={i} style={{ flex: 1, height: 3, borderRadius: 2, background: i < strength.score ? strength.color : 'rgba(255,255,255,0.1)', transition: 'background 0.2s' }} />
                      ))}
                    </div>
                    <span style={{ fontSize: 10, color: strength.color, fontFamily: 'JetBrains Mono, monospace' }}>{strength.label}</span>
                  </div>
                )}
              </div>

              <div style={{ marginBottom: 22 }}>
                <label style={{ display: 'block', fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#94A3B8', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 7 }}>CONFIRM PASSWORD</label>
                <div style={{ position: 'relative' }}>
                  <Lock size={15} style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', color: '#64748B', pointerEvents: 'none' }} />
                  <input type={showConfirm ? 'text' : 'password'} value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="Re-enter your new password" required
                    style={{ width: '100%', height: 44, paddingLeft: 38, paddingRight: 42, background: 'rgba(6, 8, 12, 0.95)', border: `1px solid ${confirmPassword && confirmPassword !== password ? 'rgba(239,68,68,0.5)' : 'rgba(255, 255, 255, 0.12)'}`, borderRadius: 8, color: '#E8EDF5', fontSize: 13, outline: 'none', transition: 'all 0.18s', boxSizing: 'border-box' }}
                    onFocus={e => { e.target.style.borderColor = '#10B981'; e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.12)' }}
                    onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'; e.target.style.boxShadow = 'none' }}
                  />
                  <button type="button" onClick={() => setShowConfirm(!showConfirm)} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#64748B', cursor: 'pointer', padding: 2 }}>
                    {showConfirm ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={loading || !token}
                style={{ width: '100%', height: 44, background: loading ? 'rgba(16, 185, 129, 0.4)' : 'linear-gradient(135deg, #10B981, #00C8F0)', border: 'none', borderRadius: 8, color: '#FFF', fontSize: 12, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.08em', cursor: loading || !token ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, boxShadow: loading || !token ? 'none' : '0 0 22px rgba(16, 185, 129, 0.35)', transition: 'all 0.2s' }}>
                {loading ? <><Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> RESETTING PASSWORD...</> : <>SET NEW PASSWORD <ArrowRight size={14} /></>}
              </button>
            </form>
          </>
        )}

        <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.07)', textAlign: 'center' }}>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#1E293B', letterSpacing: '0.07em' }}>ZOHO CATALYST SECURE CREDENTIAL RESET</span>
        </div>
      </motion.div>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

function getPasswordStrength(pwd) {
  if (!pwd) return { score: 0, label: '', color: '#64748B' }
  let score = 0
  if (pwd.length >= 8) score++
  if (pwd.length >= 12) score++
  if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) score++
  if (/[0-9]/.test(pwd) && /[^A-Za-z0-9]/.test(pwd)) score++
  const map = [
    { label: 'Very Weak', color: '#EF4444' },
    { label: 'Weak', color: '#F97316' },
    { label: 'Fair', color: '#EAB308' },
    { label: 'Strong', color: '#22C55E' },
    { label: 'Very Strong', color: '#10B981' },
  ]
  return { score, ...map[score] }
}

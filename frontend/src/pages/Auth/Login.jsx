import { useState, useEffect } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield, ArrowRight, Lock, Mail, AlertCircle, CheckCircle2, Eye, EyeOff, Sparkles,
  Loader2, KeyRound, ArrowLeft
} from 'lucide-react'
import useAuthStore from '../../store/useAuthStore'
import ParticleNetwork from '../../components/three/ParticleNetwork'
import { getAuthProviders } from '../../api/vigilx'

// ── Zoho logo SVG ──────────────────────────────────────────────────────────────
const ZohoIcon = () => (
  <svg width="18" height="18" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="120" height="120" rx="20" fill="#E42527" />
    <text x="50%" y="58%" dominantBaseline="middle" textAnchor="middle"
      fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="52" fill="white">Z</text>
  </svg>
)

// ── Field Input Component ──────────────────────────────────────────────────────
function AuthInput({ label, type = 'text', value, onChange, placeholder, icon: Icon, rightEl, onFocus, onBlur }) {
  return (
    <div style={{ marginBottom: 16 }}>
      {label && (
        <label style={{ display: 'block', fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#94A3B8', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6 }}>
          {label}
        </label>
      )}
      <div style={{ position: 'relative' }}>
        {Icon && <Icon size={15} style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', color: '#64748B', pointerEvents: 'none' }} />}
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          style={{
            width: '100%', height: 44, paddingLeft: Icon ? 38 : 14, paddingRight: rightEl ? 42 : 14,
            background: 'rgba(6, 8, 12, 0.95)', border: '1px solid rgba(255, 255, 255, 0.13)',
            borderRadius: 8, color: '#E8EDF5', fontSize: 13, outline: 'none',
            transition: 'all 0.18s', boxSizing: 'border-box', fontFamily: "'Plus Jakarta Sans', sans-serif",
          }}
          onFocus={(e) => { e.target.style.borderColor = '#00C8F0'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 200, 240, 0.12)'; onFocus?.(e) }}
          onBlur={(e) => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.13)'; e.target.style.boxShadow = 'none'; onBlur?.(e) }}
        />
        {rightEl && <div style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)' }}>{rightEl}</div>}
      </div>
    </div>
  )
}

// ── Main Login Component ───────────────────────────────────────────────────────
export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/app/home'

  const { login, loginWithGoogle, loginWithZoho, signUp, error, clearError } = useAuthStore()

  const [mode, setMode] = useState('login')       // 'login' | 'signup' | 'forgot'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(true)
  const [successMsg, setSuccessMsg] = useState('')
  const [localError, setLocalError] = useState('')
  const [oauthLoading, setOAuthLoading] = useState(null)   // 'google' | 'zoho' | null
  const [formLoading, setFormLoading] = useState(false)    // only true while a form action is in-flight
  const [providers, setProviders] = useState(['email', 'google', 'zoho'])

  // Load enabled providers from backend dynamically
  useEffect(() => {
    getAuthProviders()
      .then((res) => {
        if (res?.providers?.length) {
          setProviders(res.providers.map(p => p.id))
        }
      })
      .catch(() => {}) // Silently fail — defaults cover local dev
  }, [])

  const showEmail  = providers.includes('email')
  const showGoogle = providers.includes('google')
  const showZoho   = providers.includes('zoho')

  // ── Event Handlers ──────────────────────────────────────────────────────────

  const handleLoginSubmit = async (e) => {
    e.preventDefault()
    setLocalError('')
    setSuccessMsg('')
    clearError()
    if (!email || !password) { setLocalError('Please enter both email and password.'); return }

    setFormLoading(true)
    const res = await login(email, password)
    setFormLoading(false)
    if (res.success) navigate(from, { replace: true })
  }

  const handleSignUpSubmit = async (e) => {
    e.preventDefault()
    setLocalError('')
    setSuccessMsg('')
    clearError()
    if (!email || !password) { setLocalError('Please provide an email and password.'); return }
    if (password !== confirmPassword) { setLocalError('Passwords do not match.'); return }
    if (password.length < 8) { setLocalError('Password must be at least 8 characters.'); return }

    setFormLoading(true)
    const res = await signUp(email, password, firstName, lastName)
    setFormLoading(false)
    if (res.success) {
      setSuccessMsg('Account registered! Check your email for a verification link before signing in.')
      setMode('login')
    }
  }

  const handleForgotSubmit = async (e) => {
    e.preventDefault()
    setLocalError('')
    setSuccessMsg('')
    clearError()
    if (!email) { setLocalError('Please enter your email address.'); return }

    // Navigate to full forgot password page
    navigate(`/forgot-password?email=${encodeURIComponent(email)}`)
  }

  const handleGoogleSignIn = () => {
    setOAuthLoading('google')
    clearError()
    loginWithGoogle()
  }

  const handleZohoSignIn = () => {
    setOAuthLoading('zoho')
    clearError()
    loginWithZoho()
  }

  const displayError = localError || error

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div style={{ position: 'relative', minHeight: '100vh', background: '#06080C', color: '#E8EDF5', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Plus Jakarta Sans', 'Inter', sans-serif", overflow: 'hidden' }}>

      {/* Background */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
        <ParticleNetwork style={{ opacity: 0.4 }} />
        <div style={{ position: 'absolute', top: -120, left: -120, width: 650, height: 650, borderRadius: '50%', background: 'radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.4) 0%, rgba(0, 200, 240, 0.14) 45%, transparent 70%)', filter: 'blur(70px)' }} />
        <div style={{ position: 'absolute', bottom: -80, right: -80, width: 450, height: 450, borderRadius: '50%', background: 'radial-gradient(circle at 70% 70%, rgba(16, 185, 129, 0.12) 0%, transparent 60%)', filter: 'blur(60px)' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(6, 8, 12, 0.7)' }} />
      </div>

      {/* Portal Card */}
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4 }}
        style={{
          position: 'relative', zIndex: 10, width: '100%', maxWidth: 460, margin: '24px',
          background: 'rgba(10, 14, 22, 0.94)', border: '1px solid rgba(0, 200, 240, 0.3)',
          borderRadius: 18, padding: '38px 34px',
          boxShadow: '0 0 60px rgba(0, 200, 240, 0.18), 0 0 0 1px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)',
          backdropFilter: 'blur(28px)',
        }}
      >
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 50, height: 50, borderRadius: 13, background: 'rgba(0, 200, 240, 0.1)', border: '1px solid rgba(0, 200, 240, 0.3)', marginBottom: 14, boxShadow: '0 0 28px rgba(0, 200, 240, 0.25)' }}>
            <Shield size={26} style={{ color: '#00C8F0' }} />
          </div>
          <h1 style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 19, fontWeight: 800, letterSpacing: '0.14em', color: '#FFFFFF', margin: 0 }}>
            VIGIL<span style={{ color: '#00C8F0' }}>X</span>
          </h1>
          <p style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#64748B', letterSpacing: '0.12em', marginTop: 6 }}>
            INTELLIGENCE OPERATIONS PORTAL
          </p>
        </div>

        {/* Mode Tab Switcher — only for login/signup */}
        {mode !== 'forgot' && (
          <div style={{ display: 'flex', background: 'rgba(6, 8, 12, 0.9)', border: '1px solid rgba(255, 255, 255, 0.09)', borderRadius: 9, padding: 4, marginBottom: 24 }}>
            {[['login', 'SIGN IN'], ['signup', 'CREATE ACCOUNT']].map(([m, label]) => (
              <button key={m} onClick={() => { setMode(m); setLocalError(''); clearError(); setSuccessMsg('') }}
                style={{
                  flex: 1, padding: '9px 0', border: 'none', borderRadius: 6, fontSize: 10, fontWeight: 700,
                  fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.06em', cursor: 'pointer', transition: 'all 0.2s',
                  color: mode === m ? '#06080C' : '#64748B',
                  background: mode === m ? '#00C8F0' : 'transparent',
                  boxShadow: mode === m ? '0 0 18px rgba(0, 200, 240, 0.4)' : 'none',
                }}
              >{label}</button>
            ))}
          </div>
        )}

        {/* Error / Success Alerts */}
        <AnimatePresence>
          {displayError && (
            <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '11px 14px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 8, marginBottom: 18 }}>
              <AlertCircle size={15} style={{ color: '#EF4444', flexShrink: 0, marginTop: 1 }} />
              <span style={{ fontSize: 12, color: '#FCA5A5', lineHeight: 1.45 }}>{displayError}</span>
            </motion.div>
          )}
          {successMsg && (
            <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '11px 14px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 8, marginBottom: 18 }}>
              <CheckCircle2 size={15} style={{ color: '#10B981', flexShrink: 0, marginTop: 1 }} />
              <span style={{ fontSize: 12, color: '#6EE7B7', lineHeight: 1.45 }}>{successMsg}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── FORGOT PASSWORD MODE ───────────────────────────────────────────── */}
        {mode === 'forgot' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div style={{ marginBottom: 20 }}>
              <p style={{ fontSize: 13, color: '#94A3B8', lineHeight: 1.55, margin: 0 }}>
                Enter your registered email address. We will send a secure password reset link via Zoho Catalyst.
              </p>
            </div>
            <form onSubmit={handleForgotSubmit}>
              <AuthInput label="Official Email Address" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="officer@agency.gov" icon={Mail} />
              <button type="submit" disabled={formLoading}
                style={{ width: '100%', height: 44, background: 'linear-gradient(135deg, #00C8F0, #8B5CF6)', border: 'none', borderRadius: 8, color: '#FFF', fontSize: 12, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.08em', cursor: formLoading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 16, boxShadow: '0 0 22px rgba(0, 200, 240, 0.35)', transition: 'all 0.2s' }}>
                {formLoading ? <><Loader2 size={14} className="animate-spin" /> SENDING RESET LINK...</> : <><KeyRound size={14} /> SEND RESET LINK</>}
              </button>
            </form>
            <button onClick={() => { setMode('login'); setLocalError(''); clearError() }}
              style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', color: '#64748B', fontSize: 12, cursor: 'pointer', padding: 0 }}>
              <ArrowLeft size={13} /> Back to Sign In
            </button>
          </motion.div>
        )}

        {/* ── LOGIN MODE ────────────────────────────────────────────────────── */}
        {mode === 'login' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {/* OAuth Buttons */}
            {(showGoogle || showZoho) && (
              <div style={{ display: 'grid', gridTemplateColumns: showGoogle && showZoho ? '1fr 1fr' : '1fr', gap: 10, marginBottom: 20 }}>
                {showGoogle && (
                  <OAuthButton
                    label={oauthLoading === 'google' ? 'Redirecting...' : 'Google'}
                    icon={oauthLoading === 'google' ? <Loader2 size={16} className="animate-spin" /> : <GoogleSVG />}
                    onClick={handleGoogleSignIn}
                    disabled={formLoading || !!oauthLoading}
                    hoverColor="#4285F4"
                  />
                )}
                {showZoho && (
                  <OAuthButton
                    label={oauthLoading === 'zoho' ? 'Redirecting...' : 'Zoho'}
                    icon={oauthLoading === 'zoho' ? <Loader2 size={16} className="animate-spin" /> : <ZohoIcon />}
                    onClick={handleZohoSignIn}
                    disabled={formLoading || !!oauthLoading}
                    hoverColor="#E42527"
                  />
                )}
              </div>
            )}

            {/* Divider */}
            {(showGoogle || showZoho) && showEmail && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
                <div style={{ flex: 1, height: 1, background: 'rgba(255, 255, 255, 0.09)' }} />
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#475569', letterSpacing: '0.08em' }}>OR WITH CREDENTIALS</span>
                <div style={{ flex: 1, height: 1, background: 'rgba(255, 255, 255, 0.09)' }} />
              </div>
            )}

            {/* Email/Password Form */}
            {showEmail && (
              <form onSubmit={handleLoginSubmit}>
                <AuthInput label="Official Email Address" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="officer@agency.gov" icon={Mail} />
                <div style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <label style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#94A3B8', letterSpacing: '0.08em', textTransform: 'uppercase' }}>PASSWORD</label>
                    <button type="button" onClick={() => setMode('forgot')}
                      style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#00C8F0', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
                      Forgot Password?
                    </button>
                  </div>
                  <AuthInput
                    type={showPassword ? 'text' : 'password'}
                    value={password} onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••••••" icon={Lock}
                    rightEl={
                      <button type="button" onClick={() => setShowPassword(!showPassword)}
                        style={{ background: 'none', border: 'none', color: '#64748B', cursor: 'pointer', padding: 2 }}>
                        {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                      </button>
                    }
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
                  <input type="checkbox" id="remember" checked={rememberMe} onChange={e => setRememberMe(e.target.checked)} style={{ accentColor: '#00C8F0', cursor: 'pointer', width: 14, height: 14 }} />
                  <label htmlFor="remember" style={{ fontSize: 12, color: '#94A3B8', cursor: 'pointer' }}>Remember officer session</label>
                </div>

                <PrimaryButton type="submit" loading={formLoading} loadingText="AUTHENTICATING..." text="AUTHENTICATE & ENTER PORTAL" />
              </form>
            )}
          </motion.div>
        )}

        {/* ── SIGNUP MODE ───────────────────────────────────────────────────── */}
        {mode === 'signup' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <form onSubmit={handleSignUpSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 2 }}>
                <div>
                  <label style={{ display: 'block', fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#64748B', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 5 }}>FIRST NAME</label>
                  <input type="text" value={firstName} onChange={e => setFirstName(e.target.value)} placeholder="Officer"
                    style={{ width: '100%', height: 40, padding: '0 12px', background: '#06080C', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 7, color: '#E8EDF5', fontSize: 13, outline: 'none', boxSizing: 'border-box' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#64748B', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 5 }}>LAST NAME</label>
                  <input type="text" value={lastName} onChange={e => setLastName(e.target.value)} placeholder="Smith"
                    style={{ width: '100%', height: 40, padding: '0 12px', background: '#06080C', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 7, color: '#E8EDF5', fontSize: 13, outline: 'none', boxSizing: 'border-box' }} />
                </div>
              </div>

              <div style={{ marginTop: 12 }}>
                <AuthInput label="Email Address" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="officer@agency.gov" icon={Mail} />
              </div>
              <AuthInput label="Create Password (min. 8 chars)" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••••••" icon={Lock} />
              <AuthInput label="Confirm Password" type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="••••••••••••" icon={Lock} />

              <div style={{ marginTop: 4 }}>
                <PrimaryButton type="submit" loading={formLoading} loadingText="REGISTERING CLEARANCE..." text="REGISTER OFFICER ACCOUNT" />
              </div>
            </form>
          </motion.div>
        )}

        {/* Footer */}
        <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid rgba(255, 255, 255, 0.07)', textAlign: 'center' }}>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: '#334155', letterSpacing: '0.07em' }}>
            TS//SCI CLEARANCE · ZOHO CATALYST SESSION MESH
          </span>
        </div>
      </motion.div>
    </div>
  )
}

// ── Reusable Sub-Components ────────────────────────────────────────────────────

function OAuthButton({ label, icon, onClick, disabled, hoverColor }) {
  const [hovered, setHovered] = useState(false)
  return (
    <button onClick={onClick} disabled={disabled}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: '11px 0',
        background: hovered ? `${hoverColor}18` : 'rgba(255, 255, 255, 0.04)',
        border: `1px solid ${hovered ? hoverColor : 'rgba(255, 255, 255, 0.12)'}`,
        borderRadius: 8, color: '#F1F5F9', fontSize: 12, fontWeight: 600, cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'all 0.18s', opacity: disabled ? 0.65 : 1,
      }}>
      {icon}
      {label}
    </button>
  )
}

function PrimaryButton({ type = 'button', loading, loadingText, text, onClick }) {
  return (
    <button type={type} disabled={loading} onClick={onClick}
      style={{
        width: '100%', height: 44, background: loading ? 'rgba(0, 200, 240, 0.5)' : 'linear-gradient(135deg, #00C8F0, #7C3AED)',
        border: 'none', borderRadius: 8, color: '#FFF', fontSize: 12, fontWeight: 700,
        fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.08em',
        cursor: loading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        transition: 'all 0.2s', boxShadow: loading ? 'none' : '0 0 24px rgba(0, 200, 240, 0.35)',
      }}>
      {loading ? <><Loader2 size={14} className="animate-spin" /> {loadingText}</> : <>{text} <ArrowRight size={14} /></>}
    </button>
  )
}

function GoogleSVG() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
    </svg>
  )
}

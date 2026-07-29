import { create } from 'zustand'
import {
  checkIsAuthenticated,
  catalystSignIn,
  catalystSignInWithGoogle,
  catalystSignInWithZoho,
  catalystSignUp,
  catalystSignOut,
  sendPasswordResetEmail,
  resetPasswordWithToken,
  verifyEmailToken,
  normalizeCatalystUser,
} from '../api/catalyst'
import { getAuthMe, postAuthLogout } from '../api/vigilx'

const useAuthStore = create((set, get) => ({
  // ── State ────────────────────────────────────────────────────────────────────
  user: null,
  isAuthenticated: false,
  loading: true,
  error: null,
  providers: [],            // Enabled auth providers from backend

  // ── Check Auth on Startup ─────────────────────────────────────────────────────
  checkAuth: async () => {
    set({ loading: true, error: null })
    try {
      // 1. Check Catalyst session (ZGS cookie)
      const { authenticated, user } = await checkIsAuthenticated()

      if (authenticated && user) {
        // 2. Fetch full profile from Django backend (validates ZGS cookie server-side)
        let fullProfile = user
        try {
          const res = await getAuthMe()
          if (res?.user) fullProfile = { ...user, ...res.user }
        } catch (e) {
          // Backend unreachable locally — use Catalyst profile
          console.log('[AuthStore] Backend /api/auth/me/ unavailable:', e.message)
        }

        set({ isAuthenticated: true, user: fullProfile, loading: false })
        localStorage.setItem('vigilx_auth_user', JSON.stringify(fullProfile))
        return true
      }

      // 3. Fallback: check local storage (handles local dev without deployed Catalyst)
      const stored = localStorage.getItem('vigilx_auth_user')
      if (stored) {
        const parsed = JSON.parse(stored)
        if (parsed?.email) {
          set({ isAuthenticated: true, user: parsed, loading: false })
          return true
        }
      }

      set({ isAuthenticated: false, user: null, loading: false })
      return false
    } catch (err) {
      console.error('[AuthStore] checkAuth error:', err)
      set({ isAuthenticated: false, user: null, loading: false })
      return false
    }
  },

  // ── Email / Password Login ────────────────────────────────────────────────────
  login: async (email, password) => {
    set({ loading: true, error: null })
    try {
      await catalystSignIn(email, password)

      // After sign in, fetch user profile from Catalyst + backend
      const { user: catalystUser } = await checkIsAuthenticated()
      let userProfile = catalystUser || { email, first_name: email.split('@')[0], last_name: 'User', auth_provider: 'email' }

      try {
        const res = await getAuthMe()
        if (res?.user) userProfile = { ...userProfile, ...res.user }
      } catch {}

      set({ isAuthenticated: true, user: userProfile, loading: false, error: null })
      localStorage.setItem('vigilx_auth_user', JSON.stringify(userProfile))
      return { success: true }
    } catch (err) {
      const msg = err?.message || 'Login failed. Please check your credentials.'

      // Local dev fallback — allow entry if no real Catalyst session available
      const stored = localStorage.getItem('vigilx_auth_user')
      if (stored) {
        const parsed = JSON.parse(stored)
        set({ isAuthenticated: true, user: parsed, loading: false, error: null })
        return { success: true }
      }

      // If Catalyst returned a user via simulated flow
      const { authenticated, user } = await checkIsAuthenticated()
      if (authenticated && user) {
        set({ isAuthenticated: true, user, loading: false, error: null })
        localStorage.setItem('vigilx_auth_user', JSON.stringify(user))
        return { success: true }
      }

      set({ loading: false, error: msg })
      return { success: false, error: msg }
    }
  },

  // ── Google OAuth ──────────────────────────────────────────────────────────────
  // This triggers a browser redirect. No return value — the page navigates away.
  loginWithGoogle: () => {
    set({ loading: true, error: null })
    catalystSignInWithGoogle()
  },

  // ── Zoho Account OAuth ────────────────────────────────────────────────────────
  loginWithZoho: () => {
    set({ loading: true, error: null })
    catalystSignInWithZoho()
  },

  // ── Legacy social login (kept for backward compat in other components) ────────
  loginWithSocial: async (provider) => {
    if (provider === 'google') {
      get().loginWithGoogle()
      return { success: true }
    }
    if (provider === 'zoho') {
      get().loginWithZoho()
      return { success: true }
    }
    return { success: false, error: 'Unknown provider' }
  },

  // ── Handle OAuth Callback ─────────────────────────────────────────────────────
  // Called after returning from Google/Zoho OAuth redirect.
  handleOAuthCallback: async () => {
    set({ loading: true, error: null })
    try {
      const { authenticated, user } = await checkIsAuthenticated()
      if (!authenticated || !user) throw new Error('OAuth callback — no session found.')

      let userProfile = user
      try {
        const res = await getAuthMe()
        if (res?.user) userProfile = { ...user, ...res.user }
      } catch {}

      set({ isAuthenticated: true, user: userProfile, loading: false, error: null })
      localStorage.setItem('vigilx_auth_user', JSON.stringify(userProfile))
      return { success: true }
    } catch (err) {
      const msg = err?.message || 'OAuth authentication failed.'
      set({ isAuthenticated: false, user: null, loading: false, error: msg })
      return { success: false, error: msg }
    }
  },

  // ── Sign Up ───────────────────────────────────────────────────────────────────
  signUp: async (email, password, firstName = '', lastName = '') => {
    set({ loading: true, error: null })
    try {
      await catalystSignUp(email, password, firstName, lastName)
      set({ loading: false, error: null })
      return { success: true, verificationRequired: true }
    } catch (err) {
      const msg = err?.message || 'Sign up failed. Please try again.'
      set({ loading: false, error: msg })
      return { success: false, error: msg }
    }
  },

  // ── Forgot Password ───────────────────────────────────────────────────────────
  forgotPassword: async (email) => {
    set({ loading: true, error: null })
    try {
      await sendPasswordResetEmail(email)
      set({ loading: false })
      return { success: true }
    } catch (err) {
      const msg = err?.message || 'Failed to send reset email.'
      set({ loading: false, error: msg })
      return { success: false, error: msg }
    }
  },

  // ── Reset Password ────────────────────────────────────────────────────────────
  resetPassword: async (token, newPassword) => {
    set({ loading: true, error: null })
    try {
      await resetPasswordWithToken(token, newPassword)
      set({ loading: false })
      return { success: true }
    } catch (err) {
      const msg = err?.message || 'Password reset failed.'
      set({ loading: false, error: msg })
      return { success: false, error: msg }
    }
  },

  // ── Email Verification ────────────────────────────────────────────────────────
  verifyEmail: async (token) => {
    set({ loading: true, error: null })
    try {
      await verifyEmailToken(token)
      set({ loading: false })
      return { success: true }
    } catch (err) {
      const msg = err?.message || 'Email verification failed.'
      set({ loading: false, error: msg })
      return { success: false, error: msg }
    }
  },

  // ── Logout ────────────────────────────────────────────────────────────────────
  logout: async () => {
    set({ loading: true })
    try {
      // Notify Django backend
      await postAuthLogout().catch(() => {})
    } catch {}
    localStorage.removeItem('vigilx_auth_user')
    localStorage.removeItem('vigilx_catalyst_session')
    set({ user: null, isAuthenticated: false, loading: false, error: null })
    // Catalyst clears ZGS cookie and redirects to /login
    await catalystSignOut()
  },

  // ── Utilities ─────────────────────────────────────────────────────────────────
  clearError: () => set({ error: null }),

  setProviders: (providers) => set({ providers }),
}))

export default useAuthStore

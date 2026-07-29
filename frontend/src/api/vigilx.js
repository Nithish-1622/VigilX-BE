import axios from 'axios'
import { checkIsAuthenticated, getCatalystSDK } from './catalyst'

const DJANGO_BASE_URL   = import.meta.env.VITE_DJANGO_API_URL || 'http://localhost:8000'
const FASTAPI_BASE_URL  = import.meta.env.VITE_FASTAPI_URL    || 'http://localhost:8001'

// ── Django API Client (Port 8000) ──────────────────────────────────────────────
export const djangoApi = axios.create({
  baseURL: DJANGO_BASE_URL,
  timeout: 60000,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

// ── FastAPI AI Engine Client (Port 8001) ───────────────────────────────────────
export const fastApi = axios.create({
  baseURL: FASTAPI_BASE_URL,
  timeout: 60000,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request Interceptors ───────────────────────────────────────────────────────

djangoApi.interceptors.request.use(
  async (config) => {
    // Only generate token if we have an active local session to avoid SDK crash
    if (localStorage.getItem('vigilx_auth_user')) {
      const sdk = getCatalystSDK()
      if (sdk?.auth?.generateAuthToken) {
        try {
          const res = await sdk.auth.generateAuthToken()
          if (res?.access_token) {
            config.headers['Authorization'] = res.access_token
          }
        } catch (e) {
          console.warn('[Django API] Failed to generate auth token:', e.message)
        }
      }
    }
    return config
  },
  (err) => Promise.reject(err)
)

fastApi.interceptors.request.use(
  async (config) => {
    if (localStorage.getItem('vigilx_auth_user')) {
      const sdk = getCatalystSDK()
      if (sdk?.auth?.generateAuthToken) {
        try {
          const res = await sdk.auth.generateAuthToken()
          if (res?.access_token) {
            config.headers['Authorization'] = res.access_token
          }
        } catch (e) {
          console.warn('[FastAPI API] Failed to generate auth token:', e.message)
        }
      }
    }
    return config
  },
  (err) => Promise.reject(err)
)

// ── Response Interceptors ─────────────────────────────────────────────────────
// Handle 401 Unauthorized: Catalyst session expired.
// Clear local session and redirect to /login.

const handle401 = async (error) => {
  if (error?.response?.status === 401) {
    console.warn('[Catalyst Auth] 401 Unauthorized — session expired. Redirecting to login.')
    localStorage.removeItem('vigilx_auth_user')
    localStorage.removeItem('vigilx_catalyst_session')

    // Only redirect if not already on login page
    if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/auth/')) {
      window.location.href = '/login'
    }
  }
  return Promise.reject(error)
}

djangoApi.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status !== 401) {
      console.warn('[Django API]', err?.response?.status, err.message)
    }
    return handle401(err)
  }
)

fastApi.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status !== 401) {
      console.warn('[FastAPI Engine]', err?.response?.status, err.message)
    }
    return handle401(err)
  }
)

// ── AI Studio Endpoints ────────────────────────────────────────────────────────

export const postV1Ask = (payload) =>
  fastApi.post('/ai/ask', payload).then((r) => r.data).catch(() => {
    return djangoApi.post('/ai/ask', payload).then((r) => r.data)
  })

export const postV2Ask = (payload) =>
  fastApi.post('/ai/v2/ask', payload).then((r) => r.data).catch(() => {
    return djangoApi.post('/ai/v2/ask', payload).then((r) => r.data)
  })

// ── Auth Endpoints ─────────────────────────────────────────────────────────────

/** GET /api/auth/me/ — Fetch the authenticated user's profile from Django backend */
export const getAuthMe = () =>
  djangoApi.get('/api/auth/me/').then((r) => r.data)

/** GET /api/auth/providers/ — Fetch enabled auth providers list from backend */
export const getAuthProviders = () =>
  djangoApi.get('/api/auth/providers/').then((r) => r.data)

/** POST /api/auth/logout/ — Terminate backend session */
export const postAuthLogout = () =>
  djangoApi.post('/api/auth/logout/').then((r) => r.data).catch(() => ({}))

// ── Data Studio Endpoints ──────────────────────────────────────────────────────

export const getAdapterTest = () =>
  djangoApi.get('/adapter-test').then((r) => r.data)

// ── Dashboard Endpoints ────────────────────────────────────────────────────────

export const getGeography = () =>
  fastApi.get('/ai/graph/geography').then((r) => r.data).catch(() => {
    return djangoApi.get('/ai/graph/geography').then((r) => r.data)
  })

export const getVisualize = () =>
  fastApi.get('/ai/graph/visualize').then((r) => r.data).catch(() => {
    return djangoApi.get('/ai/graph/visualize').then((r) => r.data)
  })

export default djangoApi

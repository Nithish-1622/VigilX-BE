import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Landing from './pages/Landing'
import Login from './pages/Auth/Login'
import OAuthCallback from './pages/Auth/OAuthCallback'
import ForgotPassword from './pages/Auth/ForgotPassword'
import ResetPassword from './pages/Auth/ResetPassword'
import ProtectedRoute from './components/auth/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'
import Home from './pages/Home'
import DataStudio from './pages/DataStudio'
import AIStudio from './pages/AIStudio'
import ExperimentalStudio from './pages/ExperimentalStudio'
import ToolsStudio from './pages/ToolsStudio'
import Settings from './pages/Settings'
import HelpCenter from './pages/HelpCenter'

export default function App() {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />

          {/* Zoho Catalyst OAuth Callback — handles return from Google / Zoho redirect */}
          <Route path="/auth/callback" element={<OAuthCallback />} />

          {/* Password Reset Flow */}
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          {/* Protected Routes — Guarded by Zoho Catalyst Authentication */}
          <Route element={<ProtectedRoute />}>
            <Route path="/app" element={<AppLayout />}>
              <Route index element={<Navigate to="/app/home" replace />} />
              <Route path="home" element={<Home />} />
              <Route path="data-studio/*" element={<DataStudio />} />
              <Route path="ai-studio/*" element={<AIStudio />} />
              <Route path="experimental/*" element={<ExperimentalStudio />} />
              <Route path="tools/*" element={<ToolsStudio />} />
              <Route path="settings" element={<Settings />} />
              <Route path="help" element={<HelpCenter />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  )
}

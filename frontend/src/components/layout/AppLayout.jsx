import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import useAppStore from '../../store/useAppStore'

export default function AppLayout() {
  const collapsed = useAppStore((s) => s.sidebarCollapsed)
  const sidebarW  = collapsed ? 52 : 240

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', background: 'var(--bg-canvas)' }}>
      <Sidebar />

      <div
        style={{
          display: 'flex', flexDirection: 'column', flex: 1, minWidth: 0,
          height: '100vh', overflow: 'hidden',
          marginLeft: sidebarW,
          transition: 'margin-left 0.22s ease',
        }}
      >
        <Topbar />

        <main
          className="dot-grid"
          style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', background: 'var(--bg-canvas)' }}
        >
          <div style={{ padding: '20px', minHeight: 'calc(100vh - var(--topbar-height))' }}>
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

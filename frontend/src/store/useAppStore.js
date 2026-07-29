import { create } from 'zustand'

const useAppStore = create((set) => ({
  // Sidebar
  sidebarCollapsed: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

  // Notifications
  notifications: [
    { id: 1, text: 'V2 analysis complete: Narcotics case #4421', time: '2m ago', read: false },
    { id: 2, text: 'New criminal network node detected', time: '15m ago', read: false },
    { id: 3, text: 'Data adapter synced: 1,240 records ingested', time: '1h ago', read: true },
  ],
  markAllRead: () =>
    set((s) => ({ notifications: s.notifications.map((n) => ({ ...n, read: true })) })),
  addNotification: (n) =>
    set((s) => ({ notifications: [n, ...s.notifications] })),

  // Active agents
  activeAgents: ['PlanningAgent', 'SQLToolAgent', 'GraphAgent'],

  // Theme
  theme: localStorage.getItem('vigilx-theme') || 'dark',
  setTheme: (theme) => {
    localStorage.setItem('vigilx-theme', theme)
    document.documentElement.setAttribute('data-theme', theme)
    set({ theme })
  },
  toggleTheme: () => {
    const next = useAppStore.getState().theme === 'dark' ? 'light' : 'dark'
    localStorage.setItem('vigilx-theme', next)
    document.documentElement.setAttribute('data-theme', next)
    set({ theme: next })
  },
}))

export default useAppStore

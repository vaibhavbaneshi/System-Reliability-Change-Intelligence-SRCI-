import { useState } from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'
import Sidebar from '@/layout/Sidebar'
import Header from '@/layout/Header'

interface AppShellProps {
  children: React.ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [desktopCollapsed, setDesktopCollapsed] = useState(false)

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Mobile overlay drawer */}
      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close navigation menu"
        />
      )}

      {/* Sidebar — drawer on mobile, fixed on desktop */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col bg-card border-r border-border transition-transform duration-300 lg:static lg:translate-x-0',
          desktopCollapsed ? 'lg:w-20' : 'lg:w-64',
          'w-64',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex items-center justify-end p-2 lg:hidden">
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-lg hover:bg-muted text-muted-foreground"
            aria-label="Close sidebar"
          >
            <X size={18} />
          </button>
        </div>
        <Sidebar isOpen={!desktopCollapsed} onNavigate={() => setSidebarOpen(false)} />
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        <Header
          onMenuClick={() => setSidebarOpen(true)}
          onToggleCollapse={() => setDesktopCollapsed((v) => !v)}
          desktopCollapsed={desktopCollapsed}
        />
        <main className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-hide">
          {children}
        </main>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { ChevronLeft } from 'lucide-react'
import Sidebar from './Sidebar'
import Header from './Header'
import { cn } from '../utils/cn'

interface AppShellProps {
  children: React.ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar with smooth animation */}
      <div 
        className={cn(
          'transition-all duration-300 bg-card border-r border-border flex flex-col overflow-hidden',
          sidebarOpen ? 'w-64' : 'w-20'
        )}
      >
        <Sidebar isOpen={sidebarOpen} />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page Content with smooth scrolling */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden scrollbar-hide">
          {children}
        </main>
      </div>

      {/* Sidebar Toggle Button with smooth positioning */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className={cn(
          'absolute z-20 top-1/2 -translate-y-1/2 transition-all duration-300',
          sidebarOpen ? 'left-64' : 'left-20',
          'p-1 hover:bg-muted rounded-md text-muted-foreground hover:text-foreground'
        )}
        aria-label="Toggle sidebar"
      >
        <ChevronLeft 
          size={16} 
          className={cn(
            'transition-transform duration-300',
            !sidebarOpen && 'rotate-180'
          )} 
        />
      </button>
    </div>
  )
}

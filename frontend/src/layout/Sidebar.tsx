import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  AlertTriangle,
  Zap,
  Network,
  GitBranch,
  Cpu,
  BarChart3,
  Book,
  Settings,
  Radio,
  Box,
  Brain,
} from 'lucide-react'
import { cn } from '../utils/cn'

interface SidebarProps {
  isOpen: boolean
}

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard, href: '/' },
  { label: 'Incidents', icon: AlertTriangle, href: '/incidents' },
  { label: 'Weak RCA Queue', icon: Zap, href: '/weak-rca-queue' },
  { label: 'Service Dependencies', icon: Network, href: '/service-dependencies' },
  { label: 'Services', icon: Box, href: '/services' },
  { label: 'Changes', icon: GitBranch, href: '/changes' },
  { label: 'Autonomous Actions', icon: Cpu, href: '/autonomous-actions' },
  { label: 'Decision Trace', icon: Brain, href: '/analytics' },
  { label: 'Analytics', icon: BarChart3, href: '/analytics' },
  { label: 'Knowledge Base', icon: Book, href: '/knowledge-base' },
  { label: 'Settings', icon: Settings, href: '/settings' },
]

export default function Sidebar({ isOpen }: SidebarProps) {
  const location = useLocation()

  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="p-4 border-b border-border flex items-center justify-center">
        <div className={cn(
          'flex items-center gap-2 font-bold text-primary',
          !isOpen && 'justify-center'
        )}>
          <Radio size={24} className="shrink-0" />
          {isOpen && <span className="text-lg">SRCI</span>}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors duration-200',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-card hover:text-foreground'
              )}
              title={!isOpen ? item.label : undefined}
            >
              <Icon size={20} className="shrink-0" />
              {isOpen && <span className="text-sm font-medium truncate">{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className={cn(
        'p-4 border-t border-border text-xs text-muted-foreground',
        !isOpen && 'text-center'
      )}>
        {isOpen && <p>v1.0.0</p>}
      </div>
    </div>
  )
}

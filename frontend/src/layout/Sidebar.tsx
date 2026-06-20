import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  AlertTriangle,
  Zap,
  Network,
  GitBranch,
  BarChart3,
  Settings,
  Radio,
  Box,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  isOpen: boolean
  onNavigate?: () => void
}

const sections = [
  {
    title: 'Incident intelligence',
    items: [
      { label: 'Dashboard', icon: LayoutDashboard, href: '/' },
      { label: 'Incidents', icon: AlertTriangle, href: '/incidents' },
      { label: 'Weak RCA Queue', icon: Zap, href: '/weak-rca-queue' },
    ],
  },
  {
    title: 'Infrastructure',
    items: [
      { label: 'Services', icon: Box, href: '/services' },
      { label: 'Service Dependencies', icon: Network, href: '/service-dependencies' },
      { label: 'Changes', icon: GitBranch, href: '/changes' },
    ],
  },
  {
    title: 'Insights',
    items: [{ label: 'Analytics', icon: BarChart3, href: '/analytics' }],
  },
  {
    title: 'Administration',
    items: [{ label: 'Settings', icon: Settings, href: '/settings' }],
  },
]

function isRouteActive(pathname: string, href: string): boolean {
  if (href === '/') return pathname === '/'
  return pathname === href || pathname.startsWith(`${href}/`)
}

export default function Sidebar({ isOpen, onNavigate }: SidebarProps) {
  const location = useLocation()

  return (
    <div className="flex flex-col h-full bg-card/65 backdrop-blur-md">
      <div className="p-4 border-b border-border flex items-center justify-center">
        <div
          className={cn(
            'flex items-center gap-2 font-bold text-primary transition-all duration-300',
            !isOpen && 'justify-center',
          )}
        >
          <Radio size={24} className="shrink-0 text-primary" aria-hidden="true" />
          {isOpen && (
            <span className="text-lg tracking-wider font-extrabold bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
              SRCI
            </span>
          )}
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-6" aria-label="Main navigation">
        {sections.map((section) => (
          <div key={section.title} className="space-y-1.5">
            {isOpen && (
              <h4 className="px-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest opacity-80">
                {section.title}
              </h4>
            )}
            <div className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon
                const active = isRouteActive(location.pathname, item.href)
                return (
                  <Link
                    key={item.href}
                    to={item.href}
                    onClick={onNavigate}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 group relative',
                      active
                        ? 'bg-primary text-primary-foreground shadow-[0_0_12px_rgba(59,130,246,0.3)]'
                        : 'text-muted-foreground hover:bg-card hover:text-foreground',
                    )}
                    title={!isOpen ? item.label : undefined}
                    aria-current={active ? 'page' : undefined}
                  >
                    <Icon size={18} className="shrink-0" aria-hidden="true" />
                    {isOpen && <span className="text-xs font-semibold truncate">{item.label}</span>}
                    {!isOpen && (
                      <span className="absolute left-full ml-2 px-2 py-1 text-xs bg-card text-foreground border border-border rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
                        {item.label}
                      </span>
                    )}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      <div
        className={cn(
          'p-4 border-t border-border text-[10px] text-muted-foreground/80',
          !isOpen && 'text-center',
        )}
      >
        {isOpen ? 'Phase 16 · Incident intelligence' : 'P16'}
      </div>
    </div>
  )
}

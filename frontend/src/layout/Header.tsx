import { type FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, Settings, Menu, PanelLeftClose, PanelLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface HeaderProps {
  onMenuClick?: () => void
  onToggleCollapse?: () => void
  desktopCollapsed?: boolean
}

export default function Header({ onMenuClick, onToggleCollapse, desktopCollapsed }: HeaderProps) {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e: FormEvent) => {
    e.preventDefault()
    const q = searchQuery.trim()
    if (q) {
      navigate(`/incidents?q=${encodeURIComponent(q)}`)
    } else {
      navigate('/incidents')
    }
  }

  return (
    <header className="h-16 border-b border-border bg-card px-4 lg:px-6 flex items-center justify-between gap-4 shrink-0">
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
        >
          <Menu size={20} />
        </Button>
        {onToggleCollapse && (
          <Button
            variant="ghost"
            size="icon"
            className="hidden lg:inline-flex"
            onClick={onToggleCollapse}
            aria-label={desktopCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {desktopCollapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
          </Button>
        )}
      </div>

      <form onSubmit={handleSearch} className="flex-1 max-w-md">
        <div className="relative">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            aria-hidden="true"
          />
          <input
            type="search"
            placeholder="Search incidents…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            aria-label="Search incidents"
          />
        </div>
      </form>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" asChild aria-label="Settings">
          <Link to="/settings">
            <Settings size={20} />
          </Link>
        </Button>
      </div>
    </header>
  )
}

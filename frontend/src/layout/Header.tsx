import { Search, Bell, Settings } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <header className="h-16 border-b border-border bg-card px-6 py-4 flex items-center justify-between gap-4">
      {/* Search Bar */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search incidents, services, changes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
          />
        </div>
      </div>

      {/* Environment Selector */}
      <div className="flex items-center gap-2">
        <label className="text-sm text-muted-foreground">Environment:</label>
        <select className="px-3 py-2 bg-background border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent cursor-pointer">
          <option>Production</option>
          <option>Staging</option>
          <option>Development</option>
        </select>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-4">
        {/* Alerts Badge */}
        <button className="relative p-2 hover:bg-muted rounded-lg transition-colors text-muted-foreground hover:text-foreground">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full"></span>
        </button>

        {/* Settings */}
        <button className="p-2 hover:bg-muted rounded-lg transition-colors text-muted-foreground hover:text-foreground">
          <Settings size={20} />
        </button>
      </div>
    </header>
  )
}

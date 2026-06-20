import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpDown, Search } from 'lucide-react'
import { SeverityBadge } from '../components'
import { getAllIncidents } from '../data/mockData'
import { cn } from '../utils/cn'

type SortField = 'severity' | 'rcaConfidence' | 'duration' | 'blastRadius'
type SortOrder = 'asc' | 'desc'

export default function IncidentsList() {
  const incidents = getAllIncidents()
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState<SortField>('rcaConfidence')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'resolved'>('all')

  // Filter and sort incidents
  const filteredIncidents = incidents
    .filter(i => {
      const matchesSearch = i.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        i.service.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = filterStatus === 'all' || i.status === (filterStatus === 'resolved' ? 'resolved' : 'investigating')
      return matchesSearch && matchesStatus
    })
    .sort((a, b) => {
      let aVal = a[sortField]
      let bVal = b[sortField]
      if (sortField === 'severity') {
        const severityOrder = { critical: 3, warning: 2, info: 1 }
        aVal = severityOrder[a.severity as keyof typeof severityOrder]
        bVal = severityOrder[b.severity as keyof typeof severityOrder]
      }
      const compared = (aVal as number) - (bVal as number)
      return sortOrder === 'desc' ? -compared : compared
    })

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  return (
    <div className="p-8 max-w-7xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Incidents</h1>
        <p className="text-muted-foreground">Real-time incident tracking with AI-powered root cause analysis</p>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search incidents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          {(['all', 'active', 'resolved'] as const).map(status => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={cn(
                'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                filterStatus === status
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-card border border-border text-muted-foreground hover:text-foreground'
              )}
            >
              {status === 'all' ? 'All' : status === 'active' ? 'Active' : 'Resolved'}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-4 p-4 bg-background/50 border-b border-border font-medium text-sm text-muted-foreground">
          <div className="col-span-1 flex items-center gap-1 cursor-pointer hover:text-foreground" onClick={() => handleSort('severity')}>
            Severity <ArrowUpDown size={14} />
          </div>
          <div className="col-span-3">Title</div>
          <div className="col-span-1">Service</div>
          <div className="col-span-1">Status</div>
          <div className="col-span-1 flex items-center gap-1 cursor-pointer hover:text-foreground" onClick={() => handleSort('blastRadius')}>
            Blast <ArrowUpDown size={14} />
          </div>
          <div className="col-span-2 flex items-center gap-1 cursor-pointer hover:text-foreground" onClick={() => handleSort('rcaConfidence')}>
            RCA Confidence <ArrowUpDown size={14} />
          </div>
          <div className="col-span-2 flex items-center gap-1 cursor-pointer hover:text-foreground" onClick={() => handleSort('duration')}>
            Duration <ArrowUpDown size={14} />
          </div>
          <div className="col-span-1">Owner</div>
        </div>

        {/* Table Rows */}
        <div className="divide-y divide-border">
          {filteredIncidents.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              No incidents found matching your criteria.
            </div>
          ) : (
            filteredIncidents.map((incident, idx) => (
              <Link
                key={incident.id}
                to={`/incidents/${incident.id}`}
                className={cn(
                  'grid grid-cols-12 gap-4 p-4 hover:bg-background/50 transition-colors group',
                  idx % 2 === 0 && 'bg-background/20'
                )}
              >
                {/* Severity */}
                <div className="col-span-1 flex items-center">
                  <SeverityBadge severity={incident.severity} size="sm" animated={incident.status !== 'resolved'} />
                </div>

                {/* Title */}
                <div className="col-span-3">
                  <p className="font-medium text-foreground group-hover:text-primary transition-colors truncate">
                    {incident.title}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {incident.createdAt.toLocaleTimeString()}
                  </p>
                </div>

                {/* Service */}
                <div className="col-span-1">
                  <p className="text-sm text-muted-foreground">{incident.service}</p>
                </div>

                {/* Status */}
                <div className="col-span-1">
                  <div className={cn(
                    'w-2 h-2 rounded-full',
                    incident.status === 'resolved' ? 'bg-green-500' :
                    incident.status === 'investigating' ? 'bg-yellow-500' : 'bg-red-500'
                  )} />
                </div>

                {/* Blast Radius */}
                <div className="col-span-1">
                  <p className="text-sm font-semibold text-foreground">{incident.blastRadius}%</p>
                </div>

                {/* RCA Confidence */}
                <div className="col-span-2">
                  <div className="w-full h-1.5 bg-background rounded-full overflow-hidden border border-border">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-green-400"
                      style={{ width: `${incident.rcaConfidence}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{incident.rcaConfidence}%</p>
                </div>

                {/* Duration */}
                <div className="col-span-2">
                  <p className="text-sm font-semibold text-foreground">{incident.duration}m</p>
                </div>

                {/* Owner */}
                <div className="col-span-1">
                  <p className="text-sm text-muted-foreground truncate">{incident.owner}</p>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">Showing {filteredIncidents.length} of {incidents.length} incidents</p>
      </div>
    </div>
  )
}

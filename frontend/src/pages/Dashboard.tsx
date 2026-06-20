import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { ConfidenceBadge } from '../components'
import { mockIncidents, getCriticalIncidents } from '../data/mockData'

export default function Dashboard() {
  const criticalIncidents = getCriticalIncidents()
  const allIncidents = mockIncidents
  const activeIncidents = allIncidents.filter(i => i.status !== 'resolved')

  return (
    <div className="p-8 space-y-8 max-w-7xl">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Operations Center</h1>
        <p className="text-muted-foreground">Real-time incident monitoring and AI-driven root cause analysis</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
          <div className="text-muted-foreground text-sm font-medium mb-2">Critical Incidents</div>
          <div className="text-4xl font-bold text-destructive">{criticalIncidents.length}</div>
          <div className="text-xs text-muted-foreground mt-4">Last 24 hours</div>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
          <div className="text-muted-foreground text-sm font-medium mb-2">Active Incidents</div>
          <div className="text-4xl font-bold text-yellow-400">{activeIncidents.length}</div>
          <div className="text-xs text-muted-foreground mt-4">Investigating</div>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
          <div className="text-muted-foreground text-sm font-medium mb-2">Avg RCA Confidence</div>
          <div className="text-4xl font-bold text-green-400">
            {Math.round(allIncidents.reduce((sum, i) => sum + i.rcaConfidence, 0) / allIncidents.length)}%
          </div>
          <div className="text-xs text-muted-foreground mt-4">Last 7 days</div>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors">
          <div className="text-muted-foreground text-sm font-medium mb-2">Autonomous Actions</div>
          <div className="text-4xl font-bold text-blue-400">3</div>
          <div className="text-xs text-muted-foreground mt-4">Pending review</div>
        </div>
      </div>

      {/* Recent Critical Incidents */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">Recent Critical Incidents</h2>
          <Link to="/incidents" className="text-primary hover:text-primary/80 text-sm font-medium flex items-center gap-1">
            View all <ArrowUpRight size={16} />
          </Link>
        </div>

        <div className="space-y-3">
          {criticalIncidents.slice(0, 3).map(incident => (
            <Link
              key={incident.id}
              to={`/incidents/${incident.id}`}
              className="block bg-card border border-border rounded-lg p-4 hover:border-primary hover:bg-card/80 transition-all group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                      {incident.title}
                    </h3>
                  </div>
                  <p className="text-sm text-muted-foreground">{incident.service} • {incident.duration}m ago</p>
                </div>
                <div className="text-right space-y-2">
                  <ConfidenceBadge confidence={incident.rcaConfidence} size="sm" showPercentage={false} variant="linear" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="font-semibold text-foreground mb-4">Services Health Overview</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Healthy Services</span>
              <span className="text-lg font-bold text-green-400">4</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Degraded Services</span>
              <span className="text-lg font-bold text-yellow-400">2</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Down Services</span>
              <span className="text-lg font-bold text-red-400">0</span>
            </div>
          </div>
          <Link to="/services" className="text-primary text-sm mt-4 block hover:text-primary/80">
            View all services →
          </Link>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="font-semibold text-foreground mb-4">Pending Actions</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">RCA Reviews</span>
              <span className="text-lg font-bold text-blue-400">2</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Autonomous Actions</span>
              <span className="text-lg font-bold text-blue-400">3</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Investigations</span>
              <span className="text-lg font-bold text-blue-400">1</span>
            </div>
          </div>
          <Link to="/weak-rca-queue" className="text-primary text-sm mt-4 block hover:text-primary/80">
            Review RCA queue →
          </Link>
        </div>
      </div>
    </div>
  )
}

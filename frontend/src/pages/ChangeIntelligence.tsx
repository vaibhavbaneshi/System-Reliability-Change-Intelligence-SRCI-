import { TrendingUp } from 'lucide-react'
import { mockChanges } from '../data/mockData'

export default function ChangeIntelligence() {
  return (
    <div className="p-8 max-w-7xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Change Intelligence</h1>
        <p className="text-muted-foreground">Deployment tracking and incident correlation analysis</p>
      </div>

      <div className="space-y-4">
        {mockChanges.map(change => (
          <div key={change.id} className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-all">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h3 className="font-semibold text-foreground mb-1">{change.title}</h3>
                <p className="text-sm text-muted-foreground mb-3">Service: {change.service} • Author: {change.author}</p>
                <div className="text-xs text-muted-foreground">
                  {change.timestamp.toLocaleString()}
                </div>
              </div>
              <div className="flex items-center gap-8">
                <div className="text-right">
                  <p className="text-xs text-muted-foreground mb-1">Risk Score</p>
                  <p className={`text-lg font-bold ${change.riskScore > 60 ? 'text-orange-400' : change.riskScore > 40 ? 'text-yellow-400' : 'text-green-400'}`}>
                    {change.riskScore}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground mb-1">Correlated Incidents</p>
                  <p className={`text-lg font-bold flex items-center gap-1 ${change.correlatedIncidents > 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {change.correlatedIncidents}
                    {change.correlatedIncidents > 0 && <TrendingUp size={16} />}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

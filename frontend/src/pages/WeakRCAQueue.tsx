import { AlertTriangle, TrendingDown } from 'lucide-react'
import ConfidenceBadge from '../components/ConfidenceBadge'

const weakRCAs = [
  {
    id: 'rca-001',
    title: 'API Gateway Rate Limiting Issue',
    confidence: 52,
    trend: 'down',
    missingEvidence: ['Network trace data', 'Client IP logs', 'Rate limiter state'],
    priority: 'high',
    reviewer: 'Unassigned',
    incident: 'INC-002',
  },
  {
    id: 'rca-002',
    title: 'Database Connection Pool Exhaustion',
    confidence: 58,
    trend: 'stable',
    missingEvidence: ['Application traces', 'Connection pool metrics'],
    priority: 'medium',
    reviewer: 'Sarah Chen',
    incident: 'INC-001',
  },
  {
    id: 'rca-003',
    title: 'Cache Invalidation Delay',
    confidence: 42,
    trend: 'down',
    missingEvidence: ['Cache hit rates', 'TTL configuration logs', 'Cache server metrics'],
    priority: 'high',
    reviewer: 'Unassigned',
    incident: 'INC-003',
  },
]

export default function WeakRCAQueue() {
  return (
    <div className="p-8 max-w-7xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Weak RCA Review Queue</h1>
        <p className="text-muted-foreground">Low-confidence root cause analyses requiring manual review and evidence gathering</p>
      </div>

      <div className="space-y-4">
        {weakRCAs.map(rca => (
          <div
            key={rca.id}
            className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 hover:shadow-lg transition-all"
          >
            <div className="flex items-start justify-between gap-4 mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <AlertTriangle size={20} className="text-yellow-400" />
                  <h3 className="text-lg font-semibold text-foreground">{rca.title}</h3>
                  {rca.priority === 'high' && (
                    <span className="px-2 py-1 text-xs font-bold bg-red-500/20 text-red-400 rounded">HIGH PRIORITY</span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">Incident: {rca.incident}</p>
              </div>
              <div className="flex-shrink-0">
                <ConfidenceBadge confidence={rca.confidence} size="md" variant="circular" />
              </div>
            </div>

            {/* Confidence Trend */}
            <div className="flex items-center gap-2 mb-4 text-sm">
              <TrendingDown size={14} className={rca.trend === 'down' ? 'text-red-400' : 'text-green-400'} />
              <span className={rca.trend === 'down' ? 'text-red-400' : 'text-green-400'}>
                Confidence {rca.trend === 'down' ? 'declining' : 'stable'}
              </span>
            </div>

            {/* Missing Evidence */}
            <div className="mb-4 p-4 bg-background/50 rounded-lg border border-border">
              <p className="text-xs font-semibold text-muted-foreground mb-2 uppercase">Missing Evidence to Strengthen Analysis</p>
              <div className="flex flex-wrap gap-2">
                {rca.missingEvidence.map((evidence, idx) => (
                  <span key={idx} className="px-2 py-1 bg-muted/30 border border-muted rounded text-xs text-foreground">
                    {evidence}
                  </span>
                ))}
              </div>
            </div>

            {/* Reviewer Assignment */}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Reviewer Assignment</p>
                <p className={`font-medium ${rca.reviewer === 'Unassigned' ? 'text-orange-400' : 'text-foreground'}`}>
                  {rca.reviewer}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button className="px-4 py-2 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg hover:bg-blue-500/30 transition-colors text-sm font-medium">
                  Gather More Evidence
                </button>
                <button className="px-4 py-2 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg hover:bg-green-500/30 transition-colors text-sm font-medium">
                  Approve RCA
                </button>
                <button className="px-4 py-2 bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded-lg hover:bg-orange-500/30 transition-colors text-sm font-medium">
                  Request Investigation
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

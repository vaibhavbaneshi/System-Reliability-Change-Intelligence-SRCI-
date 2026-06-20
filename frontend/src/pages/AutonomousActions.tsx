import { CheckCircle, Clock, RotateCcw, Zap } from 'lucide-react'
import ConfidenceBadge from '../components/ConfidenceBadge'
import { mockAutonomousActions } from '../data/mockData'

const statusConfig = {
  pending: { bg: 'bg-yellow-500/20', border: 'border-yellow-500/50', text: 'text-yellow-400', icon: Clock },
  approved: { bg: 'bg-blue-500/20', border: 'border-blue-500/50', text: 'text-blue-400', icon: Zap },
  executed: { bg: 'bg-green-500/20', border: 'border-green-500/50', text: 'text-green-400', icon: CheckCircle },
  rolled_back: { bg: 'bg-orange-500/20', border: 'border-orange-500/50', text: 'text-orange-400', icon: RotateCcw },
}

export default function AutonomousActions() {
  return (
    <div className="p-8 max-w-7xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Autonomous Remediation Actions</h1>
        <p className="text-muted-foreground">AI-powered automated remediation with human oversight</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-card border border-border rounded-lg p-6">
          <p className="text-xs text-muted-foreground mb-2">Total Executed</p>
          <p className="text-3xl font-bold text-green-400">24</p>
          <p className="text-xs text-muted-foreground mt-2">94% success rate</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-6">
          <p className="text-xs text-muted-foreground mb-2">Pending Approval</p>
          <p className="text-3xl font-bold text-yellow-400">3</p>
          <p className="text-xs text-muted-foreground mt-2">avg wait: 8 minutes</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-6">
          <p className="text-xs text-muted-foreground mb-2">Rolled Back</p>
          <p className="text-3xl font-bold text-orange-400">1</p>
          <p className="text-xs text-muted-foreground mt-2">last 7 days</p>
        </div>
      </div>

      <div className="space-y-4">
        {mockAutonomousActions.map(action => {
          const config = statusConfig[action.status as keyof typeof statusConfig]
          const StatusIcon = config.icon

          return (
            <div
              key={action.id}
              className={`bg-card border-2 rounded-lg p-6 ${config.border}`}
            >
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <StatusIcon size={20} className={config.text} />
                    <h3 className="text-lg font-semibold text-foreground">{action.title}</h3>
                    <span className={`px-2 py-1 text-xs font-bold rounded ${config.bg} ${config.text}`}>
                      {action.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">Service: {action.service}</p>
                </div>
                <div className="flex-shrink-0">
                  <ConfidenceBadge confidence={action.confidence} size="md" variant="circular" />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4 p-4 bg-background/50 rounded-lg border border-border">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Success Rate</p>
                  <p className="text-lg font-bold text-green-400">{action.successRate}%</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Executed At</p>
                  <p className="text-sm font-medium text-foreground">{action.timestamp.toLocaleTimeString()}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Rollback</p>
                  <p className="text-sm font-medium text-foreground">Available</p>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2">
                {action.status === 'pending' && (
                  <>
                    <button className="px-4 py-2 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-colors text-sm font-medium">
                      Reject
                    </button>
                    <button className="px-4 py-2 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg hover:bg-green-500/30 transition-colors text-sm font-medium">
                      Approve & Execute
                    </button>
                  </>
                )}
                {action.status === 'executed' && (
                  <button className="px-4 py-2 bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded-lg hover:bg-orange-500/30 transition-colors text-sm font-medium">
                    Rollback
                  </button>
                )}
                <button className="px-4 py-2 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg hover:bg-blue-500/30 transition-colors text-sm font-medium">
                  View Details
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

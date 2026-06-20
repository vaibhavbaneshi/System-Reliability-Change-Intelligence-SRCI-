import { AlertCircle, TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '../utils/cn'

interface ServiceHealthCardProps {
  name: string
  health: number
  status: 'healthy' | 'degraded' | 'down'
  incidentCount: number
  trend?: 'up' | 'down' | 'stable'
  blastRadius: number
  onClick?: () => void
}

const statusConfig = {
  healthy: {
    bg: 'bg-green-500/20',
    border: 'border-green-500/50',
    dot: 'bg-green-500',
    text: 'text-green-400',
  },
  degraded: {
    bg: 'bg-yellow-500/20',
    border: 'border-yellow-500/50',
    dot: 'bg-yellow-500',
    text: 'text-yellow-400',
  },
  down: {
    bg: 'bg-red-500/20',
    border: 'border-red-500/50',
    dot: 'bg-red-500 animate-pulse',
    text: 'text-red-400',
  },
}

export default function ServiceHealthCard({
  name,
  health,
  status,
  incidentCount,
  trend,
  blastRadius,
  onClick,
}: ServiceHealthCardProps) {
  const config = statusConfig[status]
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : null

  return (
    <div
      onClick={onClick}
      className={cn(
        'bg-card border rounded-lg p-4 hover:border-primary hover:shadow-lg transition-all cursor-pointer group',
        config.border
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3 flex-1">
          <div className={cn('w-3 h-3 rounded-full', config.dot)}></div>
          <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors truncate">
            {name}
          </h3>
        </div>
        {TrendIcon && (
          <TrendIcon size={16} className={trend === 'up' ? 'text-red-400' : 'text-green-400'} />
        )}
      </div>

      {/* Health Score */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Health Score</span>
          <span className={cn('font-bold', config.text)}>{health}%</span>
        </div>
        <div className="w-full h-2 bg-background rounded-full overflow-hidden border border-border">
          <div
            className={cn('h-full transition-all duration-300', config.bg)}
            style={{ width: `${health}%` }}
          />
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-border">
        <div>
          <div className="text-xs text-muted-foreground mb-1">Incidents (7d)</div>
          <div className="text-lg font-bold text-foreground flex items-center gap-1">
            {incidentCount}
            {incidentCount > 0 && <AlertCircle size={14} className="text-destructive" />}
          </div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground mb-1">Blast Radius</div>
          <div className="text-lg font-bold text-foreground">{blastRadius}%</div>
        </div>
      </div>
    </div>
  )
}

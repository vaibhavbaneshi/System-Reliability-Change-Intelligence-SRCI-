import { AlertTriangle, GitBranch, TrendingUp, Code } from 'lucide-react'
import { cn } from '../utils/cn'
import type { TimelineEvent as TimelineEventType } from '../data/mockData'

interface TimelineEventProps {
  event: TimelineEventType
  isLast?: boolean
}

const typeConfig = {
  alert: {
    icon: AlertTriangle,
    color: 'text-red-400',
    bgColor: 'bg-red-500/20',
    borderColor: 'border-red-500/30',
  },
  deploy: {
    icon: GitBranch,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
    borderColor: 'border-blue-500/30',
  },
  metric: {
    icon: TrendingUp,
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-500/20',
    borderColor: 'border-yellow-500/30',
  },
  error: {
    icon: Code,
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/20',
    borderColor: 'border-orange-500/30',
  },
}

export default function TimelineEvent({
  event,
  isLast,
}: TimelineEventProps) {
  const config = typeConfig[event.type]
  const Icon = config.icon

  const timeAgo = () => {
    const now = new Date()
    const diff = now.getTime() - event.timestamp.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)

    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${Math.floor(hours / 24)}d ago`
  }

  return (
    <div className="relative">
      {/* Connector Line */}
      {!isLast && (
        <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-gradient-to-b from-border to-border/30" />
      )}

      {/* Event Node */}
      <div className="flex gap-6 pb-8">
        {/* Icon */}
        <div className="relative flex-shrink-0">
          <div className={cn(
            'w-12 h-12 rounded-lg border-2 flex items-center justify-center',
            config.bgColor,
            config.borderColor
          )}>
            <Icon size={20} className={config.color} />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 pt-1">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h4 className="font-semibold text-foreground">{event.title}</h4>
              <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
            </div>
            <span className="text-xs text-muted-foreground font-medium flex-shrink-0 whitespace-nowrap">
              {timeAgo()}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

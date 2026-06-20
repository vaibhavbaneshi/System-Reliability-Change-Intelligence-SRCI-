import { cn } from '../utils/cn'

interface ConfidenceBadgeProps {
  confidence: number
  size?: 'sm' | 'md' | 'lg'
  showPercentage?: boolean
  variant?: 'circular' | 'linear'
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 80) return 'text-green-400'
  if (confidence >= 60) return 'text-yellow-400'
  return 'text-orange-400'
}

function getConfidenceGradient(confidence: number): string {
  if (confidence >= 80) return 'from-green-400 to-green-600'
  if (confidence >= 60) return 'from-yellow-400 to-yellow-600'
  return 'from-orange-400 to-orange-600'
}

function getConfidenceBg(confidence: number): string {
  if (confidence >= 80) return 'bg-green-500/20'
  if (confidence >= 60) return 'bg-yellow-500/20'
  return 'bg-orange-500/20'
}

export default function ConfidenceBadge({
  confidence,
  size = 'md',
  showPercentage = true,
  variant = 'circular',
}: ConfidenceBadgeProps) {
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-14 h-14',
    lg: 'w-20 h-20',
  }

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-lg',
  }

  if (variant === 'linear') {
    return (
      <div className="w-full">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground">Confidence</span>
          <span className={cn('font-bold text-lg', getConfidenceColor(confidence))}>
            {confidence}%
          </span>
        </div>
        <div className="w-full h-2 bg-background rounded-full overflow-hidden border border-border">
          <div
            className={cn(
              'h-full transition-all duration-500 rounded-full',
              `bg-gradient-to-r ${getConfidenceGradient(confidence)}`
            )}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={cn(
        'relative flex items-center justify-center font-bold rounded-full border-2',
        sizeClasses[size],
        getConfidenceBg(confidence),
        `border-${confidence >= 80 ? 'green' : confidence >= 60 ? 'yellow' : 'orange'}-500`
      )}>
        <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-muted opacity-20"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            strokeWidth="3"
            strokeDasharray={`${confidence * 2.827} 282.7`}
            className={cn('text-foreground transition-all duration-500', getConfidenceColor(confidence))}
            stroke="currentColor"
            style={{
              filter: 'drop-shadow(0 0 8px currentColor)',
            }}
          />
        </svg>
        <span className={cn('relative z-10 font-bold', textSizes[size], getConfidenceColor(confidence))}>
          {confidence}%
        </span>
      </div>
      {showPercentage && (
        <span className="text-xs text-muted-foreground font-medium">Confidence</span>
      )}
    </div>
  )
}

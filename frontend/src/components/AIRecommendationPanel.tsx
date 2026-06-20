import { Lightbulb, CheckCircle, AlertCircle } from 'lucide-react'
import ConfidenceBadge from './ConfidenceBadge'

interface AIRecommendationPanelProps {
  title: string
  description: string
  reasoning: string[]
  confidence: number
  action?: {
    label: string
    onClick: () => void
  }
  type?: 'success' | 'warning' | 'info'
}

const typeConfig = {
  success: {
    icon: CheckCircle,
    bg: 'bg-green-500/20',
    border: 'border-green-500/50',
    headingColor: 'text-green-400',
  },
  warning: {
    icon: AlertCircle,
    bg: 'bg-yellow-500/20',
    border: 'border-yellow-500/50',
    headingColor: 'text-yellow-400',
  },
  info: {
    icon: Lightbulb,
    bg: 'bg-blue-500/20',
    border: 'border-blue-500/50',
    headingColor: 'text-blue-400',
  },
}

export default function AIRecommendationPanel({
  title,
  description,
  reasoning,
  confidence,
  action,
  type = 'info',
}: AIRecommendationPanelProps) {
  const config = typeConfig[type]
  const Icon = config.icon

  return (
    <div className={`border-2 ${config.border} ${config.bg} rounded-lg p-6 space-y-4`}>
      {/* Header */}
      <div className="flex items-start gap-4">
        <Icon size={24} className={config.headingColor} />
        <div className="flex-1">
          <h3 className={`text-lg font-bold ${config.headingColor}`}>{title}</h3>
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        </div>
        <div className="flex-shrink-0">
          <ConfidenceBadge confidence={confidence} size="md" variant="circular" showPercentage={true} />
        </div>
      </div>

      {/* Reasoning */}
      <div className="space-y-2 pl-10">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Reasoning</p>
        <ul className="space-y-1">
          {reasoning.map((point, idx) => (
            <li key={idx} className="text-sm text-foreground flex items-start gap-2">
              <span className="text-primary mt-1">→</span>
              {point}
            </li>
          ))}
        </ul>
      </div>

      {/* Action */}
      {action && (
        <div className="pt-2 border-t border-current border-opacity-20 pl-10">
          <button
            onClick={action.onClick}
            className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
              type === 'success'
                ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30 border border-green-500/50'
                : type === 'warning'
                ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 border border-yellow-500/50'
                : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border border-blue-500/50'
            }`}
          >
            {action.label}
          </button>
        </div>
      )}
    </div>
  )
}

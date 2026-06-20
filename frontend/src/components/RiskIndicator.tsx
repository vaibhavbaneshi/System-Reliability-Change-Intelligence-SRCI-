import { AlertTriangle, AlertCircle, Zap } from 'lucide-react'
import { cn } from '../utils/cn'

interface RiskIndicatorProps {
  level: 'low' | 'medium' | 'high'
  label?: string
  showLabel?: boolean
}

const riskConfig = {
  low: {
    bg: 'bg-green-500/20',
    border: 'border-green-500/50',
    text: 'text-green-400',
    icon: AlertCircle,
    label: 'Low Risk',
  },
  medium: {
    bg: 'bg-yellow-500/20',
    border: 'border-yellow-500/50',
    text: 'text-yellow-400',
    icon: AlertTriangle,
    label: 'Medium Risk',
  },
  high: {
    bg: 'bg-red-500/20',
    border: 'border-red-500/50',
    text: 'text-red-400',
    icon: Zap,
    label: 'High Risk',
  },
}

export default function RiskIndicator({
  level,
  label,
  showLabel = true,
}: RiskIndicatorProps) {
  const config = riskConfig[level]
  const Icon = config.icon

  return (
    <div className={cn(
      'inline-flex items-center gap-2 px-3 py-2 rounded-lg border font-medium text-sm',
      config.bg,
      config.border,
      config.text
    )}>
      <Icon size={16} className="shrink-0" />
      {showLabel && <span>{label || config.label}</span>}
    </div>
  )
}

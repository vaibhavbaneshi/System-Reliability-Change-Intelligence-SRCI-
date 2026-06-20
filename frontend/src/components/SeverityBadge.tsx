import { AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react'
import { cn } from '../utils/cn'

interface SeverityBadgeProps {
  severity: 'critical' | 'warning' | 'info' | 'success'
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

const severityConfig = {
  critical: {
    bg: 'bg-red-500/20',
    text: 'text-red-400',
    border: 'border-red-500/30',
    icon: AlertTriangle,
    label: 'Critical',
  },
  warning: {
    bg: 'bg-orange-500/20',
    text: 'text-orange-400',
    border: 'border-orange-500/30',
    icon: AlertCircle,
    label: 'Warning',
  },
  info: {
    bg: 'bg-blue-500/20',
    text: 'text-blue-400',
    border: 'border-blue-500/30',
    icon: Info,
    label: 'Info',
  },
  success: {
    bg: 'bg-green-500/20',
    text: 'text-green-400',
    border: 'border-green-500/30',
    icon: CheckCircle,
    label: 'Success',
  },
}

export default function SeverityBadge({ severity, size = 'md', animated }: SeverityBadgeProps) {
  const config = severityConfig[severity]
  const Icon = config.icon

  const sizeClasses = {
    sm: 'px-2 py-1 gap-1',
    md: 'px-3 py-2 gap-1.5',
    lg: 'px-4 py-3 gap-2',
  }

  const iconSizes = {
    sm: 16,
    md: 18,
    lg: 20,
  }

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full border font-medium',
        config.bg,
        config.text,
        config.border,
        sizeClasses[size],
        textSizes[size],
        animated && 'animate-pulse-soft'
      )}
    >
      <Icon size={iconSizes[size]} className="shrink-0" />
      <span className="font-semibold">{config.label}</span>
    </div>
  )
}

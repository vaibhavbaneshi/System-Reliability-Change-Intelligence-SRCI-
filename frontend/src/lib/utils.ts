import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatHybridScore(score: number | null | undefined): string {
  if (score == null) return '—'
  return score.toFixed(3)
}

export function formatPercentFromHybrid(score: number | null | undefined): string {
  if (score == null) return '—'
  return `${Math.round(score * 100)}%`
}

export function bandColor(band: string | null | undefined): string {
  switch (band) {
    case 'high':
      return 'text-green-400 border-green-500/40 bg-green-500/10'
    case 'medium':
      return 'text-yellow-400 border-yellow-500/40 bg-yellow-500/10'
    case 'low':
      return 'text-orange-400 border-orange-500/40 bg-orange-500/10'
    default:
      return 'text-muted-foreground border-border bg-card'
  }
}

export function severityColor(severity: string): string {
  const s = severity.toLowerCase()
  if (s === 'critical' || s === 'high') return 'text-red-400 bg-red-500/10 border-red-500/30'
  if (s === 'warning' || s === 'medium') return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
  return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
}

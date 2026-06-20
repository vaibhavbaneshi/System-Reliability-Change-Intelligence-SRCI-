import { cn, formatHybridScore, bandColor } from '@/lib/utils'
import type { ConfidenceBand } from '@/api/types'

interface ConfidenceBandBadgeProps {
  hybridScore: number | null | undefined
  confidenceBand: ConfidenceBand | null | undefined
  showScore?: boolean
  className?: string
}

export default function ConfidenceBandBadge({
  hybridScore,
  confidenceBand,
  showScore = true,
  className,
}: ConfidenceBandBadgeProps) {
  const band = confidenceBand ?? 'unknown'
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize',
        bandColor(band),
        className,
      )}
      title={`Hybrid score: ${formatHybridScore(hybridScore)}`}
    >
      {showScore && hybridScore != null && (
        <span className="font-mono">{formatHybridScore(hybridScore)}</span>
      )}
      <span>{band}</span>
    </span>
  )
}

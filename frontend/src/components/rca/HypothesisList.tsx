import { Link } from 'react-router-dom'
import type { Prediction } from '@/api/types'
import ConfidenceBandBadge from '@/components/rca/ConfidenceBandBadge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatHybridScore } from '@/lib/utils'

interface HypothesisListProps {
  predictions: Prediction[]
}

export default function HypothesisList({ predictions }: HypothesisListProps) {
  if (predictions.length === 0) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-sm text-muted-foreground">
          No hypotheses ranked yet. Run RCA to analyze candidate changes.
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Ranked hypotheses</CardTitle>
        <p className="text-sm text-muted-foreground">
          Changes ordered by hybrid score (rule + ML fusion, 0–1 scale).
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {predictions.map((prediction, index) => (
          <div
            key={prediction.change_id}
            className="rounded-lg border border-border bg-background/50 p-4 space-y-3"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-muted-foreground">#{index + 1}</span>
                  <Link
                    to={`/changes/${prediction.change_id}/impact`}
                    className="text-sm font-semibold text-primary hover:underline truncate"
                  >
                    {prediction.change_description ?? prediction.change_id}
                  </Link>
                </div>
                <p className="text-xs font-mono text-muted-foreground">{prediction.change_id}</p>
                {prediction.change_created_at && (
                  <p className="text-xs text-muted-foreground">
                    Deployed {new Date(prediction.change_created_at).toLocaleString()}
                  </p>
                )}
              </div>
              <ConfidenceBandBadge
                hybridScore={prediction.hybrid_score}
                confidenceBand={prediction.confidence_band}
              />
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="rounded-md border border-border px-2 py-1.5">
                <span className="text-muted-foreground block">Hybrid</span>
                <span className="font-mono font-semibold">{formatHybridScore(prediction.hybrid_score)}</span>
              </div>
              <div className="rounded-md border border-border px-2 py-1.5">
                <span className="text-muted-foreground block">Rule</span>
                <span className="font-mono font-semibold">{formatHybridScore(prediction.rule_confidence)}</span>
              </div>
              <div className="rounded-md border border-border px-2 py-1.5">
                <span className="text-muted-foreground block">ML</span>
                <span className="font-mono font-semibold">{formatHybridScore(prediction.ml_probability)}</span>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

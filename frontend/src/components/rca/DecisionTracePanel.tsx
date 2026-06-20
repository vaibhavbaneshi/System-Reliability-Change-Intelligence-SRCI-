import { useState } from 'react'
import type { DecisionTrace, Prediction } from '@/api/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatHybridScore } from '@/lib/utils'

interface DecisionTracePanelProps {
  predictions: Prediction[]
}

function TraceSection({ title, data }: { title: string; data: Record<string, unknown> }) {
  const entries = Object.entries(data ?? {})
  if (entries.length === 0) return null

  return (
    <div className="space-y-2">
      <h4 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">{title}</h4>
      <div className="rounded-lg border border-border bg-background/50 overflow-hidden">
        <table className="w-full text-xs">
          <tbody>
            {entries.map(([key, value]) => (
              <tr key={key} className="border-b border-border last:border-0">
                <td className="px-3 py-2 font-mono text-muted-foreground w-1/3 align-top">{key}</td>
                <td className="px-3 py-2 text-foreground align-top">
                  {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function SingleTrace({ trace, label }: { trace: DecisionTrace; label: string }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-sm font-semibold text-foreground">{label}</span>
        {trace.final_score != null && (
          <Badge variant="secondary">Final score: {formatHybridScore(trace.final_score)}</Badge>
        )}
      </div>
      <TraceSection title="Weights" data={trace.weights as Record<string, unknown>} />
      <TraceSection title="Components" data={trace.components as Record<string, unknown>} />
      <TraceSection title="Feature snapshot" data={trace.feature_snapshot as Record<string, unknown>} />
    </div>
  )
}

export default function DecisionTracePanel({ predictions }: DecisionTracePanelProps) {
  const [selectedIndex, setSelectedIndex] = useState(0)

  if (predictions.length === 0) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-sm text-muted-foreground">
          No decision trace available. Run RCA to generate predictions.
        </CardContent>
      </Card>
    )
  }

  const selected = predictions[selectedIndex]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Decision trace</CardTitle>
        <p className="text-sm text-muted-foreground">
          Scoring breakdown for ranked change hypotheses.
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {predictions.length > 1 && (
          <div className="flex flex-wrap gap-2">
            {predictions.map((p, idx) => (
              <button
                key={p.change_id}
                type="button"
                onClick={() => setSelectedIndex(idx)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                  idx === selectedIndex
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'bg-background border-border text-muted-foreground hover:text-foreground'
                }`}
                aria-pressed={idx === selectedIndex}
              >
                #{idx + 1} {p.change_id.slice(0, 8)}…
              </button>
            ))}
          </div>
        )}
        <SingleTrace
          trace={selected.decision_trace}
          label={selected.change_description ?? selected.change_id}
        />
      </CardContent>
    </Card>
  )
}

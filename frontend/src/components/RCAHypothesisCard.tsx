import { Check, X, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import ConfidenceBadge from './ConfidenceBadge'
import RiskIndicator from './RiskIndicator'
import { cn } from '../utils/cn'
import type { Hypothesis } from '../data/mockData'

interface RCAHypothesisCardProps {
  hypothesis: Hypothesis
  onAccept?: () => void
  onReject?: () => void
  onInvestigate?: () => void
}

const statusConfig = {
  proposed: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', label: 'Proposed' },
  'in-progress': { bg: 'bg-purple-500/10', border: 'border-purple-500/30', label: 'Investigating' },
  validated: { bg: 'bg-green-500/10', border: 'border-green-500/30', label: 'Validated' },
  rejected: { bg: 'bg-red-500/10', border: 'border-red-500/30', label: 'Rejected' },
}

export default function RCAHypothesisCard({
  hypothesis,
  onAccept,
  onReject,
  onInvestigate,
}: RCAHypothesisCardProps) {
  const [expanded, setExpanded] = useState(false)
  const config = statusConfig[hypothesis.status]

  return (
    <div className={cn(
      'bg-card border rounded-lg p-5 space-y-4 hover:shadow-lg transition-all',
      config.border
    )}>
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-foreground">{hypothesis.title}</h3>
            <div className={cn('px-2 py-1 rounded text-xs font-medium', config.bg, config.border, 'border')}>
              {config.label}
            </div>
          </div>
          <p className="text-sm text-muted-foreground line-clamp-2">
            Based on observed patterns and correlated events
          </p>
        </div>
        <div className="flex-shrink-0">
          <ConfidenceBadge confidence={hypothesis.confidence} size="md" showPercentage={true} variant="circular" />
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-4">
        <div>
          <span className="text-xs text-muted-foreground block mb-1">Supporting Evidence</span>
          <span className="text-lg font-bold text-green-400">{hypothesis.supportingEvidence.length}</span>
        </div>
        <div>
          <span className="text-xs text-muted-foreground block mb-1">Contradicting Evidence</span>
          <span className="text-lg font-bold text-orange-400">{hypothesis.contradictingEvidence.length}</span>
        </div>
        <div>
          <span className="text-xs text-muted-foreground block mb-1">Risk Level</span>
          <RiskIndicator level={hypothesis.riskLevel} showLabel={false} />
        </div>
      </div>

      {/* Affected Services */}
      <div>
        <span className="text-xs font-medium text-muted-foreground mb-2 block">Affected Services</span>
        <div className="flex flex-wrap gap-1">
          {hypothesis.affectedServices.map(service => (
            <span
              key={service}
              className="px-2 py-1 text-xs bg-background border border-border rounded text-foreground"
            >
              {service}
            </span>
          ))}
        </div>
      </div>

      {/* Evidence Details (Expandable) */}
      {expanded && (
        <div className="space-y-3 pt-3 border-t border-border animate-slide-in-up">
          <div>
            <h4 className="text-sm font-medium text-green-400 mb-2">Supporting Evidence:</h4>
            <ul className="space-y-1">
              {hypothesis.supportingEvidence.map((ev, idx) => (
                <li key={idx} className="text-sm text-foreground flex items-start gap-2">
                  <Check size={14} className="text-green-400 flex-shrink-0 mt-0.5" />
                  {ev}
                </li>
              ))}
            </ul>
          </div>
          {hypothesis.contradictingEvidence.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-orange-400 mb-2">Contradicting Evidence:</h4>
              <ul className="space-y-1">
                {hypothesis.contradictingEvidence.map((ev, idx) => (
                  <li key={idx} className="text-sm text-foreground flex items-start gap-2">
                    <X size={14} className="text-orange-400 flex-shrink-0 mt-0.5" />
                    {ev}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-3 border-t border-border">
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-primary hover:text-primary/80 font-medium flex items-center gap-1 transition-colors"
        >
          {expanded ? 'Hide' : 'Show'} Details
          <ChevronDown size={14} className={cn('transition-transform', expanded && 'rotate-180')} />
        </button>
        <div className="flex items-center gap-2">
          {hypothesis.status !== 'rejected' && (
            <button
              onClick={onReject}
              className="px-3 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 border border-destructive/30 rounded transition-colors"
            >
              Reject
            </button>
          )}
          {hypothesis.status !== 'validated' && (
            <button
              onClick={onInvestigate}
              className="px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary/10 border border-primary/30 rounded transition-colors"
            >
              Investigate
            </button>
          )}
          {hypothesis.status !== 'validated' && (
            <button
              onClick={onAccept}
              className="px-3 py-1.5 text-xs font-medium text-green-400 hover:bg-green-500/10 border border-green-500/30 rounded transition-colors"
            >
              Accept
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

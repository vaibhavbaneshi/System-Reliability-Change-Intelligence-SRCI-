import { ChevronRight } from 'lucide-react'
import ConfidenceBadge from './ConfidenceBadge'
import { cn } from '../utils/cn'
import type { DecisionTraceStep } from '../data/mockData'

interface DecisionTraceNodeProps {
  step: DecisionTraceStep
  isLast?: boolean
  expanded?: boolean
  onExpand?: () => void
}

const stageColors = {
  Observation: 'from-blue-600 to-blue-400',
  Analysis: 'from-purple-600 to-purple-400',
  Correlation: 'from-indigo-600 to-indigo-400',
  Hypothesis: 'from-pink-600 to-pink-400',
  Confidence: 'from-green-600 to-green-400',
  Recommendation: 'from-orange-600 to-orange-400',
}

export default function DecisionTraceNode({
  step,
  isLast,
  expanded,
  onExpand,
}: DecisionTraceNodeProps) {
  const color = (stageColors[step.stage as keyof typeof stageColors] || 'from-gray-600 to-gray-400') as string

  return (
    <div className="relative">
      {/* Connection Line */}
      {!isLast && (
        <div className="absolute left-1/2 top-24 w-1 h-12 bg-gradient-to-b from-border to-transparent transform -translate-x-1/2" />
      )}

      {/* Node */}
      <div
        onClick={onExpand}
        className={cn(
          'relative bg-card border-2 rounded-xl p-5 cursor-pointer group transition-all hover:shadow-xl',
          expanded ? 'border-primary ring-1 ring-primary/20' : 'border-border hover:border-primary/50'
        )}
      >
        {/* Stage Badge */}
        <div className={cn(
          'inline-block px-3 py-1 rounded-full text-xs font-bold text-white mb-3 bg-gradient-to-r',
          color
        )}>
          {step.stage}
        </div>

        {/* Content */}
        <div className="mb-4">
          <h3 className="font-semibold text-foreground mb-2">{step.input}</h3>
          {expanded && (
            <p className="text-sm text-muted-foreground animate-slide-in-up">
              {step.reasoning}
            </p>
          )}
        </div>

        {/* Confidence and Alternatives */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1">
            <ConfidenceBadge
              confidence={step.confidence}
              size="sm"
              showPercentage={true}
              variant="linear"
            />
          </div>
          <ChevronRight
            size={18}
            className={cn(
              'text-muted-foreground group-hover:text-primary transition-all',
              expanded && 'rotate-90'
            )}
          />
        </div>

        {/* Alternatives (Expanded) */}
        {expanded && step.alternatives.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border animate-slide-in-up">
            <p className="text-xs font-medium text-muted-foreground mb-2">Alternative Hypotheses:</p>
            <ul className="space-y-1">
              {step.alternatives.map((alt, idx) => (
                <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  {alt}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

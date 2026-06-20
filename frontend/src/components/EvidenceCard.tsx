import { ChevronDown, Copy } from 'lucide-react'
import { useState } from 'react'
import { cn } from '../utils/cn'
import type { Evidence } from '../data/mockData'

interface EvidenceCardProps {
  evidence: Evidence
}

const typeConfig = {
  log: { label: 'Log', color: 'text-orange-400', bg: 'bg-orange-500/20' },
  metric: { label: 'Metric', color: 'text-blue-400', bg: 'bg-blue-500/20' },
  alert: { label: 'Alert', color: 'text-red-400', bg: 'bg-red-500/20' },
  change: { label: 'Change', color: 'text-purple-400', bg: 'bg-purple-500/20' },
  trace: { label: 'Trace', color: 'text-green-400', bg: 'bg-green-500/20' },
}

const strengthConfig = {
  weak: { label: 'Weak', color: 'text-muted-foreground' },
  moderate: { label: 'Moderate', color: 'text-yellow-400' },
  strong: { label: 'Strong', color: 'text-green-400' },
}

export default function EvidenceCard({ evidence }: EvidenceCardProps) {
  const [expanded, setExpanded] = useState(false)
  const typeInfo = typeConfig[evidence.type]
  const strengthInfo = strengthConfig[evidence.strength]

  return (
    <div className="bg-card border border-border rounded-lg p-4 hover:border-primary hover:shadow-lg transition-all">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className={cn('px-2 py-1 rounded text-xs font-bold', typeInfo.bg, typeInfo.color)}>
              {typeInfo.label}
            </span>
            <span className={cn('px-2 py-1 rounded text-xs font-medium bg-muted/30 border border-muted', strengthInfo.color)}>
              {strengthInfo.label}
            </span>
          </div>
          <h4 className="font-semibold text-foreground">{evidence.title}</h4>
          <p className="text-xs text-muted-foreground mt-1">
            Relevance: <span className="font-bold text-primary">{evidence.relevance}%</span>
          </p>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronDown size={16} className={cn('transition-transform', expanded && 'rotate-180')} />
        </button>
      </div>

      {/* Content (Expanded) */}
      {expanded && (
        <div className="pt-3 border-t border-border animate-slide-in-up">
          <div className="bg-background rounded p-3 font-mono text-xs text-muted-foreground mb-3 max-h-32 overflow-y-auto">
            <code>{evidence.content}</code>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">
              {new Date(evidence.timestamp).toLocaleString()}
            </span>
            <button className="flex items-center gap-1 text-primary hover:text-primary/80 transition-colors">
              <Copy size={12} />
              Copy
            </button>
          </div>
        </div>
      )}

      {/* Preview */}
      {!expanded && (
        <p className="text-sm text-muted-foreground line-clamp-2">
          {evidence.content}
        </p>
      )}
    </div>
  )
}

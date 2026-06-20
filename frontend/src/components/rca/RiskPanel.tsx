import type { ExplanationResponse } from '@/api/types'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Flag, ShieldAlert } from 'lucide-react'

interface RiskPanelProps {
  escalation: ExplanationResponse['escalation']
  quality: ExplanationResponse['quality']
  contextFlags: ExplanationResponse['context_flags']
}

export default function RiskPanel({ escalation, quality, contextFlags }: RiskPanelProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <ShieldAlert size={16} className="text-orange-400" />
            Escalation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Badge variant={escalation.should_escalate ? 'destructive' : 'success'}>
            {escalation.should_escalate ? 'Escalate' : 'No escalation'}
          </Badge>
          {escalation.escalation_level && (
            <p className="text-xs text-muted-foreground capitalize">
              Level: {escalation.escalation_level}
            </p>
          )}
          {escalation.reasons.length > 0 && (
            <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
              {escalation.reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <AlertTriangle size={16} className="text-yellow-400" />
            Quality
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold font-mono">{quality.quality_score.toFixed(2)}</span>
            <Badge variant="secondary" className="capitalize">
              {quality.quality_band}
            </Badge>
          </div>
          {quality.factors.length > 0 && (
            <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
              {quality.factors.map((factor) => (
                <li key={factor}>{factor}</li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Flag size={16} className="text-blue-400" />
            Context flags
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Badge variant={contextFlags.weak_signal ? 'warning' : 'secondary'}>
            Weak signal: {contextFlags.weak_signal ? 'yes' : 'no'}
          </Badge>
          <Badge variant={contextFlags.close_competition ? 'warning' : 'secondary'}>
            Close competition: {contextFlags.close_competition ? 'yes' : 'no'}
          </Badge>
        </CardContent>
      </Card>
    </div>
  )
}

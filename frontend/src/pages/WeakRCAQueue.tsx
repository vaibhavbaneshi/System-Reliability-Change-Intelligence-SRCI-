import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { incidentsApi } from '@/api/incidents'
import QueryWrapper from '@/components/common/QueryWrapper'
import ConfidenceBandBadge from '@/components/rca/ConfidenceBandBadge'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { severityColor } from '@/lib/utils'

export default function WeakRCAQueue() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['weak-rca'],
    queryFn: () => incidentsApi.weakRca(),
  })

  const incidents = data?.incidents ?? []

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Weak RCA queue</h1>
        <p className="text-muted-foreground">
          Incidents with weak signals, close competition, or low-confidence RCA requiring analyst review.
        </p>
      </div>

      <QueryWrapper
        isLoading={isLoading}
        isError={isError}
        error={error as Error}
        onRetry={refetch}
        isEmpty={incidents.length === 0}
        emptyTitle="Queue is empty"
        emptyDescription="No incidents currently flagged for weak RCA review."
      >
        <div className="space-y-3">
          {incidents.map((incident) => (
            <Link key={incident.id} to={`/incidents/${incident.id}`}>
              <Card className="hover:border-primary/50 transition-colors">
                <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="min-w-0 space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${severityColor(incident.severity)}`}>
                        {incident.severity}
                      </span>
                      {incident.auto_rca_should_escalate && <Badge variant="destructive">Escalate</Badge>}
                    </div>
                    <h3 className="font-semibold text-foreground">{incident.title}</h3>
                    <p className="text-xs font-mono text-muted-foreground">{incident.id}</p>
                    {incident.auto_rca_quality_band && (
                      <p className="text-xs text-muted-foreground">
                        Quality: {incident.auto_rca_quality_band}
                        {incident.auto_rca_quality_score != null &&
                          ` (${incident.auto_rca_quality_score.toFixed(2)})`}
                      </p>
                    )}
                  </div>
                  <ConfidenceBandBadge
                    hybridScore={incident.auto_rca_hybrid_score}
                    confidenceBand={incident.auto_rca_confidence_band}
                  />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </QueryWrapper>
    </div>
  )
}

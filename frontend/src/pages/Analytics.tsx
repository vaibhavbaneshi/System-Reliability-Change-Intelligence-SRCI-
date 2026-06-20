import { useQuery } from '@tanstack/react-query'
import { incidentsApi } from '@/api/incidents'
import { autonomyApi } from '@/api/services'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatPercentFromHybrid } from '@/lib/utils'

export default function Analytics() {
  const incidentsQuery = useQuery({
    queryKey: ['incidents'],
    queryFn: () => incidentsApi.list(),
  })

  const autonomyQuery = useQuery({
    queryKey: ['autonomy-status'],
    queryFn: () => autonomyApi.status(),
  })

  const incidents = incidentsQuery.data?.incidents ?? []
  const processed = incidents.filter((i) => i.auto_rca_processed).length
  const escalated = incidents.filter((i) => i.auto_rca_should_escalate).length
  const withScores = incidents.filter((i) => i.auto_rca_hybrid_score != null)
  const avgHybrid =
    withScores.length > 0
      ? withScores.reduce((sum, i) => sum + (i.auto_rca_hybrid_score ?? 0), 0) / withScores.length
      : null

  const bandCounts: Record<string, number> = incidents.reduce(
    (acc, i) => {
      const band = i.auto_rca_confidence_band ?? 'unknown'
      acc[band] = (acc[band] ?? 0) + 1
      return acc
    },
    {} as Record<string, number>,
  )

  const autonomy = autonomyQuery.data

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Analytics</h1>
        <p className="text-muted-foreground">
          Incident intelligence metrics and autonomy pipeline status — no synthetic charts, real API data only.
        </p>
      </div>

      <QueryWrapper
        isLoading={incidentsQuery.isLoading || autonomyQuery.isLoading}
        isError={incidentsQuery.isError || autonomyQuery.isError}
        error={(incidentsQuery.error ?? autonomyQuery.error) as Error}
        onRetry={() => {
          incidentsQuery.refetch()
          autonomyQuery.refetch()
        }}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total incidents" value={String(incidents.length)} />
          <StatCard label="RCA processed" value={String(processed)} />
          <StatCard label="Escalation flagged" value={String(escalated)} />
          <StatCard
            label="Avg hybrid score"
            value={avgHybrid != null ? formatPercentFromHybrid(avgHybrid) : '—'}
            hint="Across incidents with scores (0–1 scale)"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Confidence band distribution</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(bandCounts).length === 0 ? (
                <p className="text-sm text-muted-foreground">No band data yet.</p>
              ) : (
                Object.entries(bandCounts).map(([band, count]) => (
                  <div key={band} className="flex items-center justify-between text-sm">
                    <span className="capitalize text-muted-foreground">{band}</span>
                    <div className="flex items-center gap-2">
                      <div className="h-2 rounded-full bg-primary/30 w-32 overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full"
                          style={{ width: `${incidents.length ? (count / incidents.length) * 100 : 0}%` }}
                        />
                      </div>
                      <span className="font-mono w-8 text-right">{count}</span>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Autonomy pipeline</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {autonomy ? (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Monitor running</span>
                    <Badge variant={autonomy.running ? 'success' : 'secondary'}>
                      {autonomy.running ? 'Active' : 'Stopped'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Unprocessed incidents</span>
                    <span className="font-mono">{String(autonomy.unprocessed_incidents ?? 0)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Active workers</span>
                    <span className="font-mono">{String(autonomy.active_workers ?? 0)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Poll interval</span>
                    <span className="font-mono">{String(autonomy.poll_interval_sec ?? '—')}s</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Env enabled</span>
                    <Badge variant={autonomy.autonomy_enabled_env ? 'success' : 'secondary'}>
                      {autonomy.autonomy_enabled_env ? 'Yes' : 'No'}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground pt-2 border-t border-border">
                    Per-incident evaluation (precision@k, MRR) is available via POST /incidents/:id/evaluate
                    when ground-truth labels exist.
                  </p>
                </>
              ) : (
                <p className="text-muted-foreground">Autonomy status unavailable.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </QueryWrapper>
    </div>
  )
}

function StatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Card>
      <CardContent className="p-6">
        <p className="text-sm text-muted-foreground mb-1">{label}</p>
        <p className="text-3xl font-bold text-foreground">{value}</p>
        {hint && <p className="text-xs text-muted-foreground mt-2">{hint}</p>}
      </CardContent>
    </Card>
  )
}

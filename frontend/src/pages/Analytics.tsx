import { useQuery } from '@tanstack/react-query'
import { incidentsApi } from '@/api/incidents'
import { changesApi, autonomyApi } from '@/api/services'
import { gitApi } from '@/api/git'
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

  const changesQuery = useQuery({
    queryKey: ['changes'],
    queryFn: () => changesApi.list(),
  })

  const gitEventsQuery = useQuery({
    queryKey: ['git-events'],
    queryFn: () => gitApi.events(),
  })

  const gitPrsQuery = useQuery({
    queryKey: ['git-pull-requests'],
    queryFn: () => gitApi.pullRequests(),
  })

  const workspaceQuery = useQuery({
    queryKey: ['git-workspace'],
    queryFn: () => gitApi.workspace(),
  })

  const incidents = incidentsQuery.data?.incidents ?? []
  const changes = changesQuery.data ?? []
  const gitChanges = changes.filter((c) => c.source?.startsWith('github'))
  const gitEvents = gitEventsQuery.data?.events ?? []
  const gitPrs = gitPrsQuery.data?.pull_requests ?? []
  const workspace = workspaceQuery.data

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

  const prRiskCounts = gitPrs.reduce(
    (acc, pr) => {
      const band = pr.risk_band ?? 'unknown'
      acc[band] = (acc[band] ?? 0) + 1
      return acc
    },
    {} as Record<string, number>,
  )

  const autonomy = autonomyQuery.data
  const hasGit = (workspace?.git_connections ?? 0) > 0

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Analytics</h1>
        <p className="text-muted-foreground">
          Incident intelligence, Git change tracking, and autonomy pipeline status — real API data only.
        </p>
      </div>

      <QueryWrapper
        isLoading={
          incidentsQuery.isLoading ||
          autonomyQuery.isLoading ||
          changesQuery.isLoading ||
          gitEventsQuery.isLoading
        }
        isError={
          incidentsQuery.isError ||
          autonomyQuery.isError ||
          changesQuery.isError ||
          gitEventsQuery.isError
        }
        error={
          (incidentsQuery.error ??
            autonomyQuery.error ??
            changesQuery.error ??
            gitEventsQuery.error) as Error
        }
        onRetry={() => {
          incidentsQuery.refetch()
          autonomyQuery.refetch()
          changesQuery.refetch()
          gitEventsQuery.refetch()
          gitPrsQuery.refetch()
          workspaceQuery.refetch()
        }}
      >
        {hasGit && (
          <>
            <h2 className="text-lg font-semibold text-foreground">Git & change intelligence</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Services (from repo)" value={String(workspace?.services ?? 0)} />
              <StatCard label="Git-tracked changes" value={String(gitChanges.length)} />
              <StatCard label="Git events" value={String(gitEvents.length)} />
              <StatCard label="Open PR checks" value={String(gitPrs.filter((p) => p.state === 'open').length)} />
            </div>

            {gitPrs.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">PR risk distribution</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {Object.entries(prRiskCounts).map(([band, count]) => (
                    <div key={band} className="flex items-center justify-between text-sm">
                      <span className="capitalize text-muted-foreground">{band}</span>
                      <span className="font-mono">{count}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </>
        )}

        <h2 className="text-lg font-semibold text-foreground pt-2">Incident intelligence</h2>
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

        {!hasGit && (
          <p className="text-sm text-muted-foreground">
            Connect a GitHub repo under Integrations to see change and PR risk metrics here.
          </p>
        )}

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
                    Incidents are ingested from monitoring systems, not Git. Per-incident evaluation is available
                    via POST /incidents/:id/evaluate when ground-truth labels exist.
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

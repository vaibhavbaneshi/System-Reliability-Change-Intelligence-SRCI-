import type { ComponentType } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowUpRight, AlertTriangle, GitBranch, Box, Zap } from 'lucide-react'
import { incidentsApi } from '@/api/incidents'
import { servicesApi, changesApi } from '@/api/services'
import QueryWrapper from '@/components/common/QueryWrapper'
import ConfidenceBandBadge from '@/components/rca/ConfidenceBandBadge'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { severityColor } from '@/lib/utils'

export default function Dashboard() {
  const incidentsQuery = useQuery({
    queryKey: ['incidents'],
    queryFn: () => incidentsApi.list(),
  })

  const weakRcaQuery = useQuery({
    queryKey: ['weak-rca'],
    queryFn: () => incidentsApi.weakRca(),
  })

  const servicesQuery = useQuery({
    queryKey: ['services'],
    queryFn: () => servicesApi.list(),
  })

  const changesQuery = useQuery({
    queryKey: ['changes'],
    queryFn: () => changesApi.list(),
  })

  const isLoading =
    incidentsQuery.isLoading ||
    weakRcaQuery.isLoading ||
    servicesQuery.isLoading ||
    changesQuery.isLoading

  const isError =
    incidentsQuery.isError ||
    weakRcaQuery.isError ||
    servicesQuery.isError ||
    changesQuery.isError

  const error =
    (incidentsQuery.error as Error) ||
    (weakRcaQuery.error as Error) ||
    (servicesQuery.error as Error) ||
    (changesQuery.error as Error)

  const incidents = incidentsQuery.data?.incidents ?? []
  const weakCount = weakRcaQuery.data?.incidents.length ?? 0
  const serviceCount = servicesQuery.data?.length ?? 0
  const changeCount = changesQuery.data?.length ?? 0
  const processedCount = incidents.filter((i) => i.auto_rca_processed).length
  const escalateCount = incidents.filter((i) => i.auto_rca_should_escalate).length
  const recent = [...incidents]
    .sort((a, b) => {
      const aTime = a.started_at ? new Date(a.started_at).getTime() : 0
      const bTime = b.started_at ? new Date(b.started_at).getTime() : 0
      return bTime - aTime
    })
    .slice(0, 5)

  return (
    <div className="p-6 lg:p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Incident intelligence</h1>
        <p className="text-muted-foreground">
          Overview of incidents, changes, and RCA coverage across your services.
        </p>
      </div>

      <QueryWrapper
        isLoading={isLoading}
        isError={isError}
        error={error}
        onRetry={() => {
          incidentsQuery.refetch()
          weakRcaQuery.refetch()
          servicesQuery.refetch()
          changesQuery.refetch()
        }}
        skeleton={
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-28 rounded-xl" />
            ))}
          </div>
        }
      >
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard icon={AlertTriangle} label="Incidents" value={incidents.length} hint={`${processedCount} RCA processed`} />
          <MetricCard icon={Zap} label="Weak RCA queue" value={weakCount} hint="Needs analyst review" accent="text-yellow-400" />
          <MetricCard icon={Box} label="Services" value={serviceCount} hint="Registered services" />
          <MetricCard icon={GitBranch} label="Changes" value={changeCount} hint={`${escalateCount} flagged for escalation`} />
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-foreground">Recent incidents</h2>
            <Link to="/incidents" className="text-primary hover:text-primary/80 text-sm font-medium flex items-center gap-1">
              View all <ArrowUpRight size={16} />
            </Link>
          </div>

          {recent.length === 0 ? (
            <Card>
              <CardContent className="py-10 text-center text-sm text-muted-foreground">
                No incidents recorded yet.
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {recent.map((incident) => (
                <Link
                  key={incident.id}
                  to={`/incidents/${incident.id}`}
                  className="block bg-card border border-border rounded-lg p-4 hover:border-primary/50 transition-all group"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${severityColor(incident.severity)}`}>
                          {incident.severity}
                        </span>
                        {incident.auto_rca_should_escalate && (
                          <Badge variant="destructive">Escalate</Badge>
                        )}
                        {incident.auto_rca_in_progress && (
                          <Badge variant="warning">RCA running</Badge>
                        )}
                      </div>
                      <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                        {incident.title}
                      </h3>
                      <p className="text-xs text-muted-foreground font-mono">{incident.id}</p>
                    </div>
                    <ConfidenceBandBadge
                      hybridScore={incident.auto_rca_hybrid_score}
                      confidenceBand={incident.auto_rca_confidence_band}
                    />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {weakCount > 0 && (
          <Card className="border-yellow-500/30 bg-yellow-500/5">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Zap size={18} className="text-yellow-400" />
                Weak RCA signals need attention
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                {weakCount} incident{weakCount !== 1 ? 's' : ''} with low-confidence or ambiguous RCA results.
              </p>
              <Link to="/weak-rca-queue">
                <Badge variant="warning" className="cursor-pointer hover:opacity-80">
                  Open weak RCA queue →
                </Badge>
              </Link>
            </CardContent>
          </Card>
        )}
      </QueryWrapper>
    </div>
  )
}

function MetricCard({
  icon: Icon,
  label,
  value,
  hint,
  accent,
}: {
  icon: ComponentType<{ size?: number; className?: string }>
  label: string
  value: number
  hint: string
  accent?: string
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center gap-2 text-muted-foreground text-sm mb-2">
          <Icon size={16} />
          {label}
        </div>
        <div className={`text-4xl font-bold ${accent ?? 'text-foreground'}`}>{value}</div>
        <p className="text-xs text-muted-foreground mt-2">{hint}</p>
      </CardContent>
    </Card>
  )
}

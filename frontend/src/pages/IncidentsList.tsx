import { useMemo } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { incidentsApi } from '@/api/incidents'
import QueryWrapper from '@/components/common/QueryWrapper'
import ConfidenceBandBadge from '@/components/rca/ConfidenceBandBadge'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { severityColor } from '@/lib/utils'

export default function IncidentsList() {
  const [searchParams] = useSearchParams()
  const q = searchParams.get('q')?.toLowerCase() ?? ''

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => incidentsApi.list(),
  })

  const incidents = useMemo(() => {
    const list = data?.incidents ?? []
    if (!q) return list
    return list.filter(
      (i) =>
        i.title.toLowerCase().includes(q) ||
        i.id.toLowerCase().includes(q) ||
        i.severity.toLowerCase().includes(q),
    )
  }, [data, q])

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Incidents</h1>
        <p className="text-muted-foreground">
          Incident intelligence with hybrid RCA scores and escalation signals.
        </p>
      </div>

      {q && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Search size={14} />
          Showing results for &quot;{searchParams.get('q')}&quot;
        </div>
      )}

      <QueryWrapper
        isLoading={isLoading}
        isError={isError}
        error={error as Error}
        onRetry={refetch}
        isEmpty={incidents.length === 0}
        emptyTitle="No incidents found"
        emptyDescription={q ? 'Try a different search term.' : 'Incidents will appear here when ingested.'}
      >
        {/* Mobile card layout */}
        <div className="space-y-3 lg:hidden">
          {incidents.map((incident) => (
            <Link key={incident.id} to={`/incidents/${incident.id}`}>
              <Card className="hover:border-primary/50 transition-colors">
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="font-semibold text-foreground truncate">{incident.title}</p>
                      <p className="text-xs font-mono text-muted-foreground">{incident.id}</p>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full border capitalize shrink-0 ${severityColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <ConfidenceBandBadge
                      hybridScore={incident.auto_rca_hybrid_score}
                      confidenceBand={incident.auto_rca_confidence_band}
                    />
                    {incident.auto_rca_should_escalate && <Badge variant="destructive">Escalate</Badge>}
                    {incident.auto_rca_in_progress && <Badge variant="warning">RCA running</Badge>}
                  </div>
                  {incident.started_at && (
                    <p className="text-xs text-muted-foreground">
                      Started {new Date(incident.started_at).toLocaleString()}
                    </p>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {/* Desktop table */}
        <div className="hidden lg:block rounded-xl border border-border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-card border-b border-border">
              <tr>
                <th className="text-left px-4 py-3 font-semibold text-muted-foreground">Incident</th>
                <th className="text-left px-4 py-3 font-semibold text-muted-foreground">Severity</th>
                <th className="text-left px-4 py-3 font-semibold text-muted-foreground">RCA score</th>
                <th className="text-left px-4 py-3 font-semibold text-muted-foreground">Band</th>
                <th className="text-left px-4 py-3 font-semibold text-muted-foreground">Status</th>
                <th className="text-left px-4 py-3 font-semibold text-muted-foreground">Started</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.id} className="border-b border-border last:border-0 hover:bg-card/50">
                  <td className="px-4 py-3">
                    <Link to={`/incidents/${incident.id}`} className="font-medium text-primary hover:underline">
                      {incident.title}
                    </Link>
                    <p className="text-xs font-mono text-muted-foreground">{incident.id}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${severityColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono">
                    {incident.auto_rca_hybrid_score != null
                      ? incident.auto_rca_hybrid_score.toFixed(3)
                      : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <ConfidenceBandBadge
                      hybridScore={incident.auto_rca_hybrid_score}
                      confidenceBand={incident.auto_rca_confidence_band}
                      showScore={false}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {incident.auto_rca_should_escalate && <Badge variant="destructive">Escalate</Badge>}
                      {incident.auto_rca_in_progress && <Badge variant="warning">Running</Badge>}
                      {incident.auto_rca_processed && !incident.auto_rca_in_progress && (
                        <Badge variant="success">Processed</Badge>
                      )}
                      {!incident.auto_rca_processed && !incident.auto_rca_in_progress && (
                        <Badge variant="secondary">Pending</Badge>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground text-xs">
                    {incident.started_at ? new Date(incident.started_at).toLocaleString() : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </QueryWrapper>
    </div>
  )
}

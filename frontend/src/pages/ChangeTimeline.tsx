import { useMemo } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { incidentsApi } from '@/api/incidents'
import { changesApi } from '@/api/services'
import Breadcrumbs from '@/components/layout/Breadcrumbs'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function ChangeTimeline() {
  const { id = '' } = useParams()

  const incidentQuery = useQuery({
    queryKey: ['incident', id],
    queryFn: () => incidentsApi.get(id),
    enabled: !!id,
  })

  const changesQuery = useQuery({
    queryKey: ['changes'],
    queryFn: () => changesApi.list(),
  })

  const incident = incidentQuery.data
  const incidentStart = incident?.started_at ? new Date(incident.started_at) : null

  const priorChanges = useMemo(() => {
    if (!incidentStart) return []
    return (changesQuery.data ?? [])
      .filter((c) => new Date(c.created_at) < incidentStart)
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  }, [changesQuery.data, incidentStart])

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Incidents', href: '/incidents' },
          { label: incident?.title ?? id, href: `/incidents/${id}` },
          { label: 'Change timeline' },
        ]}
      />

      <div>
        <h1 className="text-2xl font-bold text-foreground mb-2">Change timeline</h1>
        <p className="text-muted-foreground text-sm">
          Changes deployed before incident start
          {incidentStart ? ` (${incidentStart.toLocaleString()})` : ''}.
        </p>
      </div>

      <QueryWrapper
        isLoading={incidentQuery.isLoading || changesQuery.isLoading}
        isError={incidentQuery.isError || changesQuery.isError}
        error={(incidentQuery.error ?? changesQuery.error) as Error}
        onRetry={() => {
          incidentQuery.refetch()
          changesQuery.refetch()
        }}
        isEmpty={priorChanges.length === 0}
        emptyTitle="No prior changes"
        emptyDescription={
          incidentStart
            ? 'No changes were recorded before this incident started.'
            : 'Incident start time is not set.'
        }
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {priorChanges.length} change{priorChanges.length !== 1 ? 's' : ''} before incident
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {priorChanges.map((change) => {
              const changeTime = new Date(change.created_at)
              const minutesBefore = incidentStart
                ? Math.round((incidentStart.getTime() - changeTime.getTime()) / 60000)
                : null

              return (
                <div
                  key={change.id}
                  className="relative pl-6 border-l-2 border-border pb-4 last:pb-0"
                >
                  <div className="absolute -left-[5px] top-1 w-2 h-2 rounded-full bg-primary" />
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs text-muted-foreground">
                        {changeTime.toLocaleString()}
                      </span>
                      {minutesBefore != null && (
                        <Badge variant="secondary">{minutesBefore}m before incident</Badge>
                      )}
                      <Badge variant="outline">{change.change_type}</Badge>
                    </div>
                    <p className="font-medium text-foreground">{change.description}</p>
                    <p className="text-xs font-mono text-muted-foreground">{change.git_ref}</p>
                    <Link
                      to={`/changes/${change.id}/impact`}
                      className="text-xs text-primary hover:underline"
                    >
                      View impact →
                    </Link>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>
      </QueryWrapper>
    </div>
  )
}

import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { changesApi } from '@/api/services'
import Breadcrumbs from '@/components/layout/Breadcrumbs'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const impactVariant = (level: string) => {
  const l = level.toLowerCase()
  if (l === 'critical' || l === 'high') return 'destructive' as const
  if (l === 'medium') return 'warning' as const
  return 'secondary' as const
}

export default function ChangeImpactPage() {
  const { id = '' } = useParams()

  const changeQuery = useQuery({
    queryKey: ['change', id],
    queryFn: () => changesApi.get(id),
    enabled: !!id,
  })

  const impactQuery = useQuery({
    queryKey: ['change-impact', id],
    queryFn: () => changesApi.impact(id),
    enabled: !!id,
  })

  const change = changeQuery.data
  const impacts = impactQuery.data ?? []

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Changes', href: '/changes' },
          { label: change?.description ?? id },
        ]}
      />

      <QueryWrapper
        isLoading={changeQuery.isLoading}
        isError={changeQuery.isError}
        error={changeQuery.error as Error}
        onRetry={() => changeQuery.refetch()}
      >
        {change && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{change.description}</CardTitle>
              <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
                <Badge variant="secondary">{change.change_type}</Badge>
                <span className="font-mono text-xs">{change.git_ref}</span>
                <span className="text-xs">{new Date(change.created_at).toLocaleString()}</span>
              </div>
            </CardHeader>
          </Card>
        )}
      </QueryWrapper>

      <QueryWrapper
        isLoading={impactQuery.isLoading}
        isError={impactQuery.isError}
        error={impactQuery.error as Error}
        onRetry={() => impactQuery.refetch()}
        isEmpty={impacts.length === 0}
        emptyTitle="No blast radius data"
        emptyDescription="Impact analysis has not been computed for this change."
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Blast radius</CardTitle>
            <p className="text-sm text-muted-foreground">
              Services affected by this change, ranked by impact level.
            </p>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {impacts.map((item, idx) => (
                <li
                  key={`${item.service}-${idx}`}
                  className="flex items-center justify-between rounded-lg border border-border bg-background/50 px-4 py-3"
                >
                  <Link to="/services" className="font-medium text-primary hover:underline">
                    {item.service}
                  </Link>
                  <Badge variant={impactVariant(item.impact_level)} className="capitalize">
                    {item.impact_level}
                  </Badge>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </QueryWrapper>
    </div>
  )
}

import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowUpRight } from 'lucide-react'
import { changesApi } from '@/api/services'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

export default function ChangeIntelligence() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['changes'],
    queryFn: () => changesApi.list(),
  })

  const changes = data ?? []

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Change intelligence</h1>
        <p className="text-muted-foreground">
          Track deployments and configuration changes linked to incident analysis.
        </p>
      </div>

      <QueryWrapper
        isLoading={isLoading}
        isError={isError}
        error={error as Error}
        onRetry={refetch}
        isEmpty={changes.length === 0}
        emptyTitle="No changes recorded"
        emptyDescription="Changes will appear here when ingested from your change pipeline."
      >
        <div className="space-y-3">
          {changes.map((change) => (
            <Card key={change.id} className="hover:border-primary/30 transition-colors">
              <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="min-w-0 space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="secondary">{change.change_type}</Badge>
                    {change.source && change.source !== 'manual' && (
                      <Badge variant="outline" className="capitalize">
                        {change.source.replace('github_', 'git ')}
                      </Badge>
                    )}
                    {change.pr_number != null && (
                      <Badge variant="outline">PR #{change.pr_number}</Badge>
                    )}
                    <span className="text-xs font-mono text-muted-foreground">{change.id}</span>
                  </div>
                  <p className="font-medium text-foreground">{change.description}</p>
                  <p className="text-xs text-muted-foreground font-mono">{change.git_ref}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(change.created_at).toLocaleString()}
                  </p>
                </div>
                <Link
                  to={`/changes/${change.id}/impact`}
                  className="inline-flex items-center gap-1 text-sm text-primary hover:underline shrink-0"
                >
                  View blast radius <ArrowUpRight size={14} />
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </QueryWrapper>
    </div>
  )
}

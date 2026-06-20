import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ExternalLink, GitPullRequest } from 'lucide-react'
import { gitApi } from '@/api/git'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const recVariant = (rec: string | null) => {
  if (rec === 'review_required') return 'destructive' as const
  if (rec === 'caution') return 'warning' as const
  return 'success' as const
}

export default function PullRequests() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['git-pull-requests'],
    queryFn: () => gitApi.pullRequests(),
    refetchInterval: 60000,
  })

  const prs = data?.pull_requests ?? []

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Pull request checks</h1>
        <p className="text-muted-foreground">
          Pre-merge blast radius and risk scores for open PRs from connected repositories.
        </p>
      </div>

      <QueryWrapper
        isLoading={isLoading}
        isError={isError}
        error={error as Error}
        onRetry={refetch}
        isEmpty={prs.length === 0}
        emptyTitle="No PR checks yet"
        emptyDescription="Connect a repo in Integrations and sync, or open a PR to trigger checks."
      >
        <div className="space-y-3">
          {prs.map((pr) => (
            <Card key={pr.id}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-start justify-between gap-4">
                  <span className="flex items-center gap-2">
                    <GitPullRequest size={18} />
                    #{pr.pr_number} {pr.title}
                  </span>
                  {pr.html_url && (
                    <a
                      href={pr.html_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-primary shrink-0"
                      aria-label="Open on GitHub"
                    >
                      <ExternalLink size={16} />
                    </a>
                  )}
                </CardTitle>
                <p className="text-xs text-muted-foreground font-mono">{pr.repo}</p>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  <Badge variant={recVariant(pr.merge_recommendation)}>
                    {pr.merge_recommendation?.replace('_', ' ') ?? 'pending'}
                  </Badge>
                  {pr.risk_band && (
                    <Badge variant="outline" className="capitalize">
                      Risk: {pr.risk_band}
                    </Badge>
                  )}
                  {pr.services_touched.map((s) => (
                    <Badge key={s} variant="secondary">
                      {s}
                    </Badge>
                  ))}
                </div>
                {pr.change_id && (
                  <Link
                    to={`/changes/${pr.change_id}/impact`}
                    className="text-sm text-primary hover:underline"
                  >
                    View blast radius →
                  </Link>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </QueryWrapper>
    </div>
  )
}

import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowDown, ArrowUp, AlertTriangle } from 'lucide-react'
import { changesApi } from '@/api/services'
import Breadcrumbs from '@/components/layout/Breadcrumbs'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { GraphNode } from '@/api/types'

const impactVariant = (level: string) => {
  const l = level.toLowerCase()
  if (l === 'critical' || l === 'high') return 'destructive' as const
  if (l === 'medium') return 'warning' as const
  return 'secondary' as const
}

const riskVariant = (band: string) => {
  const b = band.toLowerCase()
  if (b === 'high') return 'destructive' as const
  if (b === 'medium') return 'warning' as const
  return 'secondary' as const
}

function NodeList({ title, icon, nodes }: { title: string; icon: React.ReactNode; nodes: GraphNode[] }) {
  if (nodes.length === 0) return null
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          {icon}
          {title}
          <Badge variant="secondary">{nodes.length}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {nodes.map((node) => (
            <li
              key={`${node.direction}-${node.service_id}`}
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-lg border border-border bg-background/50 px-4 py-3"
            >
              <div>
                <span className="font-medium">{node.service_name}</span>
                <div className="text-xs text-muted-foreground mt-0.5">
                  depth {node.depth}
                  {node.dependency_type && ` · ${node.dependency_type}`}
                  {` · ${Math.round(node.propagation_probability * 100)}% spread`}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="capitalize text-xs">
                  {node.criticality}
                </Badge>
                <Badge variant={impactVariant(node.impact_level)} className="capitalize">
                  {node.impact_level}
                </Badge>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

export default function ChangeImpactPage() {
  const { id = '' } = useParams()

  const changeQuery = useQuery({
    queryKey: ['change', id],
    queryFn: () => changesApi.get(id),
    enabled: !!id,
  })

  const blastQuery = useQuery({
    queryKey: ['blast-radius', id],
    queryFn: () => changesApi.blastRadius(id),
    enabled: !!id,
  })

  const change = changeQuery.data
  const blast = blastQuery.data

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
        isLoading={blastQuery.isLoading}
        isError={blastQuery.isError}
        error={blastQuery.error as Error}
        onRetry={() => blastQuery.refetch()}
      >
        {blast && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <p className="text-xs text-muted-foreground">Blast score</p>
                  <p className="text-2xl font-bold font-mono">
                    {Math.round(blast.blast_radius.score * 100)}%
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-xs text-muted-foreground">Total affected</p>
                  <p className="text-2xl font-bold font-mono">{blast.blast_radius.total_services}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-xs text-muted-foreground">Max depth</p>
                  <p className="text-2xl font-bold font-mono">{blast.blast_radius.max_depth}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <AlertTriangle size={12} /> Risk band
                  </p>
                  <Badge variant={riskVariant(blast.risk_panel.risk_band)} className="mt-1 capitalize text-sm">
                    {blast.risk_panel.risk_band}
                  </Badge>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Failure spread model</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground block text-xs">Expected affected</span>
                  <span className="font-mono text-lg">{blast.failure_spread.expected_affected_count}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block text-xs">High risk</span>
                  <span className="font-mono text-lg text-destructive">{blast.failure_spread.high_risk_count}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block text-xs">Medium risk</span>
                  <span className="font-mono text-lg">{blast.failure_spread.medium_risk_count}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block text-xs">Low risk</span>
                  <span className="font-mono text-lg">{blast.failure_spread.low_risk_count}</span>
                </div>
              </CardContent>
            </Card>

            {blast.risk_panel.factors.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Risk factors</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm space-y-1 font-mono text-muted-foreground">
                    {blast.risk_panel.factors.map((f) => (
                      <li key={f}>{f}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            <NodeList
              title="Origin services"
              icon={<span className="w-2 h-2 rounded-full bg-primary" />}
              nodes={blast.origin_services.map((o) => ({
                service_id: o.id,
                service_name: o.name,
                criticality: o.criticality,
                depth: 0,
                direction: 'origin' as const,
                dependency_type: null,
                edge_weight: 1,
                propagation_probability: 1,
                impact_level: 'high',
                risk_contribution: 1,
                origin_service_id: o.id,
              }))}
            />

            <NodeList title="Downstream impact" icon={<ArrowDown size={16} />} nodes={blast.downstream} />
            <NodeList title="Upstream dependencies" icon={<ArrowUp size={16} />} nodes={blast.upstream} />
          </div>
        )}
      </QueryWrapper>

      {!blastQuery.isLoading && !blast && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground text-sm">
            No blast radius computed yet.{' '}
            <Link to="/changes" className="text-primary hover:underline">
              Ingest a change
            </Link>{' '}
            or run POST /changes/{id}/propagate.
          </CardContent>
        </Card>
      )}
    </div>
  )
}

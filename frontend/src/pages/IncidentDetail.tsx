import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Loader2, Play, Clock, Server } from 'lucide-react'
import { incidentsApi } from '@/api/incidents'
import { rcaApi } from '@/api/rca'
import Breadcrumbs from '@/components/layout/Breadcrumbs'
import QueryWrapper from '@/components/common/QueryWrapper'
import ConfidenceBandBadge from '@/components/rca/ConfidenceBandBadge'
import ExplanationPanel from '@/components/rca/ExplanationPanel'
import HypothesisList from '@/components/rca/HypothesisList'
import DecisionTracePanel from '@/components/rca/DecisionTracePanel'
import FeedbackPanel from '@/components/rca/FeedbackPanel'
import RiskPanel from '@/components/rca/RiskPanel'
import RcaChatPanel from '@/components/chat/RcaChatPanel'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { severityColor } from '@/lib/utils'

export default function IncidentDetail() {
  const { id = '' } = useParams()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('summary')

  const incidentQuery = useQuery({
    queryKey: ['incident', id],
    queryFn: () => incidentsApi.get(id),
    enabled: !!id,
  })

  const explanationQuery = useQuery({
    queryKey: ['explanation', id],
    queryFn: () => rcaApi.explain(id),
    enabled: !!id,
    retry: false,
  })

  const evidenceQuery = useQuery({
    queryKey: ['evidence', id],
    queryFn: () => rcaApi.evidence(id),
    enabled: !!id && activeTab === 'evidence',
  })

  const runRcaMutation = useMutation({
    mutationFn: () => rcaApi.run(id),
    onSuccess: (data) => {
      toast.success('RCA completed')
      queryClient.setQueryData(['explanation', id], data)
      queryClient.invalidateQueries({ queryKey: ['incident', id] })
    },
    onError: (err: Error) => {
      toast.error(err.message || 'RCA run failed')
    },
  })

  const incident = incidentQuery.data
  const explanation = explanationQuery.data
  const predictions = explanation?.predictions ?? []

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <Breadcrumbs
        items={[
          { label: 'Incidents', href: '/incidents' },
          { label: incident?.title ?? id },
        ]}
      />

      <QueryWrapper
        isLoading={incidentQuery.isLoading}
        isError={incidentQuery.isError}
        error={incidentQuery.error as Error}
        onRetry={() => incidentQuery.refetch()}
      >
        {incident && (
          <>
            <Card>
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                  <div className="space-y-2 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-mono bg-background px-2 py-1 rounded border border-border">
                        {incident.id}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${severityColor(incident.severity)}`}>
                        {incident.severity}
                      </span>
                      {incident.auto_rca_should_escalate && <Badge variant="destructive">Escalate</Badge>}
                      {incident.auto_rca_in_progress && <Badge variant="warning">RCA in progress</Badge>}
                    </div>
                    <h1 className="text-2xl font-bold text-foreground">{incident.title}</h1>
                    <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
                      {incident.started_at && (
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          Started {new Date(incident.started_at).toLocaleString()}
                        </span>
                      )}
                      {incident.affected_services.length > 0 && (
                        <span className="flex items-center gap-1">
                          <Server size={12} />
                          {incident.affected_services.map((s) => s.name).join(', ')}
                        </span>
                      )}
                    </div>
                    <Link
                      to={`/incidents/${id}/timeline`}
                      className="text-xs text-primary hover:underline inline-block"
                    >
                      View change timeline →
                    </Link>
                  </div>

                  <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 shrink-0">
                    <ConfidenceBandBadge
                      hybridScore={incident.auto_rca_hybrid_score ?? explanation?.rca_summary?.hybrid_score}
                      confidenceBand={incident.auto_rca_confidence_band ?? explanation?.rca_summary?.confidence_band}
                    />
                    <Button
                      onClick={() => runRcaMutation.mutate()}
                      disabled={runRcaMutation.isPending || incident.auto_rca_in_progress}
                      aria-label="Run RCA analysis"
                    >
                      {runRcaMutation.isPending || incident.auto_rca_in_progress ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <Play size={16} />
                      )}
                      {runRcaMutation.isPending || incident.auto_rca_in_progress ? 'Running RCA…' : 'Run RCA'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList aria-label="Incident workspace sections">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="hypotheses">Hypotheses</TabsTrigger>
                <TabsTrigger value="evidence">Evidence</TabsTrigger>
                <TabsTrigger value="trace">Decision Trace</TabsTrigger>
                <TabsTrigger value="feedback">Feedback</TabsTrigger>
                <TabsTrigger value="chat">Chat</TabsTrigger>
              </TabsList>

              <TabsContent value="summary">
                {explanationQuery.isLoading && !explanation ? (
                  <Card>
                    <CardContent className="py-10 text-center text-sm text-muted-foreground">
                      Loading RCA summary…
                    </CardContent>
                  </Card>
                ) : explanation ? (
                  <div className="space-y-6">
                    <ExplanationPanel
                      explanation={explanation.explanation}
                      explanationSource={explanation.explanation_source}
                    />
                    <RiskPanel
                      escalation={explanation.escalation}
                      quality={explanation.quality}
                      contextFlags={explanation.context_flags}
                    />
                  </div>
                ) : (
                  <Card>
                    <CardContent className="py-10 text-center space-y-4">
                      <p className="text-sm text-muted-foreground">
                        No RCA explanation yet. Run RCA to generate analysis.
                      </p>
                      <Button onClick={() => runRcaMutation.mutate()} disabled={runRcaMutation.isPending}>
                        <Play size={16} />
                        Run RCA
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="hypotheses">
                <HypothesisList predictions={predictions} />
              </TabsContent>

              <TabsContent value="evidence">
                <QueryWrapper
                  isLoading={evidenceQuery.isLoading}
                  isError={evidenceQuery.isError}
                  error={evidenceQuery.error as Error}
                  onRetry={() => evidenceQuery.refetch()}
                  isEmpty={(evidenceQuery.data?.evidence.length ?? 0) === 0}
                  emptyTitle="No evidence linked"
                  emptyDescription="Evidence records will appear when linked to this incident."
                >
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Evidence</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {evidenceQuery.data?.evidence.map((item) => (
                        <div
                          key={item.id}
                          className="rounded-lg border border-border bg-background/50 p-4 text-sm"
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="secondary">{item.source_type}</Badge>
                            <span className="text-xs text-muted-foreground font-mono">{item.id}</span>
                          </div>
                          <p className="text-foreground font-mono text-xs break-all">{item.reference}</p>
                          {item.created_at && (
                            <p className="text-xs text-muted-foreground mt-2">
                              {new Date(item.created_at).toLocaleString()}
                            </p>
                          )}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </QueryWrapper>
              </TabsContent>

              <TabsContent value="trace">
                <DecisionTracePanel predictions={predictions} />
              </TabsContent>

              <TabsContent value="feedback">
                <FeedbackPanel incidentId={id} predictions={predictions} />
              </TabsContent>

              <TabsContent value="chat">
                <RcaChatPanel incidentId={id} />
              </TabsContent>
            </Tabs>
          </>
        )}
      </QueryWrapper>
    </div>
  )
}

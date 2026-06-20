import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Zap } from 'lucide-react'
import {
  SeverityBadge,
  ConfidenceBadge,
  RCAHypothesisCard,
  TimelineEvent,
  InvestigationProgress,
  DecisionTraceNode,
  EvidenceCard,
  AIRecommendationPanel,
} from '../components'
import { getIncidentById } from '../data/mockData'

type TabType = 'summary' | 'timeline' | 'hypotheses' | 'evidence' | 'decision-trace' | 'feedback'

export default function IncidentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const incident = getIncidentById(id || '')
  const [activeTab, setActiveTab] = useState<TabType>('summary')
  const [expandedTrace, setExpandedTrace] = useState<string | null>(null)

  if (!incident) {
    return (
      <div className="p-8">
        <button
          onClick={() => navigate('/incidents')}
          className="flex items-center gap-2 text-primary hover:text-primary/80 mb-4"
        >
          <ArrowLeft size={18} />
          Back to Incidents
        </button>
        <p className="text-muted-foreground">Incident not found</p>
      </div>
    )
  }

  const tabs = [
    { id: 'summary', label: 'Summary' },
    { id: 'timeline', label: 'Timeline' },
    { id: 'hypotheses', label: 'Hypotheses' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'decision-trace', label: 'Decision Trace' },
    { id: 'feedback', label: 'Feedback' },
  ] as const

  return (
    <div className="p-8 max-w-7xl space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate('/incidents')}
        className="flex items-center gap-2 text-primary hover:text-primary/80 transition-colors"
      >
        <ArrowLeft size={18} />
        Back to Incidents
      </button>

      {/* Command Center Header */}
      <div className="bg-gradient-to-r from-card to-card/80 border border-border rounded-lg p-8 space-y-6">
        {/* Title and Badge */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className={`w-4 h-4 rounded-full ${incident.status === 'resolved' ? 'bg-green-500' : incident.status === 'investigating' ? 'bg-yellow-500' : 'bg-red-500'} ${incident.status !== 'resolved' && 'animate-pulse'}`}></div>
              <h1 className="text-3xl font-bold text-foreground">{incident.title}</h1>
            </div>
            <p className="text-muted-foreground">ID: {incident.id}</p>
          </div>
          <SeverityBadge severity={incident.severity} size="lg" animated={incident.status !== 'resolved'} />
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-5 gap-4 pt-4 border-t border-border">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Status</p>
            <p className="font-semibold text-foreground capitalize">{incident.status}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Service</p>
            <p className="font-semibold text-foreground">{incident.service}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Duration</p>
            <p className="font-semibold text-foreground">{incident.duration}m</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Blast Radius</p>
            <p className="font-semibold text-orange-400">{incident.blastRadius}%</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Owner</p>
            <p className="font-semibold text-foreground">{incident.owner}</p>
          </div>
        </div>

        {/* RCA Confidence & Action */}
        <div className="flex items-center justify-between pt-4 border-t border-border">
          <div className="flex-1">
            <ConfidenceBadge confidence={incident.rcaConfidence} size="lg" variant="linear" showPercentage={true} />
          </div>
          <button className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium">
            <Zap size={18} />
            Run RCA Analysis
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border flex gap-8 overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 font-medium transition-colors border-b-2 whitespace-nowrap ${
              activeTab === tab.id
                ? 'text-primary border-primary'
                : 'text-muted-foreground hover:text-foreground border-transparent'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Summary Tab */}
        {activeTab === 'summary' && (
          <div className="space-y-6">
            {/* AI Recommendation */}
            <AIRecommendationPanel
              title="Recommended Root Cause"
              description="Based on analysis of supporting evidence and system correlations"
              reasoning={[
                'Memory usage increased 81% in 30 minutes',
                'Connection pool exhaustion correlates with memory spike',
                'Payment processing queue shows retention pattern',
                'Recent deploy to payment-service may have introduced leak',
              ]}
              confidence={incident.rcaConfidence}
              type="info"
              action={{
                label: 'Approve & Proceed',
                onClick: () => console.log('Approved'),
              }}
            />

            {/* Investigation Progress */}
            <div className="bg-card border border-border rounded-lg p-6">
              <InvestigationProgress
                progress={72}
                currentStep="Analyzing connection pool metrics and memory traces"
                milestones={[
                  { id: '1', name: 'Data collection', completed: true },
                  { id: '2', name: 'Pattern identification', completed: true },
                  { id: '3', name: 'Correlation analysis', completed: true },
                  { id: '4', name: 'Hypothesis validation', completed: false },
                  { id: '5', name: 'RCA finalization', completed: false },
                ]}
                estimatedTimeRemaining={12}
              />
            </div>

            {/* Impact Assessment */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-card border border-border rounded-lg p-6">
                <p className="text-xs text-muted-foreground mb-2">Affected Services</p>
                <p className="text-3xl font-bold text-blue-400">3</p>
                <p className="text-xs text-muted-foreground mt-2">payment-service, order-service, billing-service</p>
              </div>
              <div className="bg-card border border-border rounded-lg p-6">
                <p className="text-xs text-muted-foreground mb-2">User Impact</p>
                <p className="text-3xl font-bold text-red-400">~5.2k</p>
                <p className="text-xs text-muted-foreground mt-2">users unable to complete transactions</p>
              </div>
              <div className="bg-card border border-border rounded-lg p-6">
                <p className="text-xs text-muted-foreground mb-2">Revenue Impact</p>
                <p className="text-3xl font-bold text-destructive">$240k</p>
                <p className="text-xs text-muted-foreground mt-2">estimated during incident window</p>
              </div>
            </div>
          </div>
        )}

        {/* Timeline Tab */}
        {activeTab === 'timeline' && (
          <div className="bg-card border border-border rounded-lg p-8">
            <div className="space-y-4">
              {incident.timeline.map((event, idx) => (
                <TimelineEvent
                  key={event.id}
                  event={event}
                  isLast={idx === incident.timeline.length - 1}
                />
              ))}
            </div>
          </div>
        )}

        {/* Hypotheses Tab */}
        {activeTab === 'hypotheses' && (
          <div className="space-y-4">
            {incident.hypotheses.map(hypothesis => (
              <RCAHypothesisCard
                key={hypothesis.id}
                hypothesis={hypothesis}
                onAccept={() => console.log('Accepted', hypothesis.id)}
                onReject={() => console.log('Rejected', hypothesis.id)}
                onInvestigate={() => console.log('Investigate', hypothesis.id)}
              />
            ))}
          </div>
        )}

        {/* Evidence Tab */}
        {activeTab === 'evidence' && (
          <div className="space-y-4">
            {incident.evidence.map(ev => (
              <EvidenceCard key={ev.id} evidence={ev} />
            ))}
          </div>
        )}

        {/* Decision Trace Tab */}
        {activeTab === 'decision-trace' && (
          <div className="bg-card border border-border rounded-lg p-8 space-y-6">
            <p className="text-muted-foreground text-sm">
              Follow the AI's reasoning process from initial observations through final recommendations.
            </p>
            <div className="space-y-8">
              {incident.decisionTrace.map((step, idx) => (
                <DecisionTraceNode
                  key={step.id}
                  step={step}
                  isLast={idx === incident.decisionTrace.length - 1}
                  expanded={expandedTrace === step.id}
                  onExpand={() => setExpandedTrace(expandedTrace === step.id ? null : step.id)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <div className="bg-card border border-border rounded-lg p-6 text-center py-12">
            <p className="text-muted-foreground mb-4">Provide feedback on this RCA to improve future analysis</p>
            <div className="flex items-center justify-center gap-4">
              <button className="px-6 py-2 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg hover:bg-green-500/30 transition-colors font-medium">
                Accurate
              </button>
              <button className="px-6 py-2 bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 rounded-lg hover:bg-yellow-500/30 transition-colors font-medium">
                Partially Accurate
              </button>
              <button className="px-6 py-2 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-colors font-medium">
                Inaccurate
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

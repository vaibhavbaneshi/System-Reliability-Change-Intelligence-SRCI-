export type ConfidenceBand = 'high' | 'medium' | 'low' | 'unknown'

export interface IncidentSummary {
  id: string
  title: string
  severity: string
  started_at: string | null
  auto_rca_processed: boolean
  auto_rca_processed_at: string | null
  auto_rca_attempts: number
  auto_rca_in_progress: boolean
  auto_rca_hybrid_score: number | null
  auto_rca_confidence_band: ConfidenceBand | null
  auto_rca_should_escalate: boolean | null
  auto_rca_quality_score: number | null
  auto_rca_quality_band: string | null
}

export interface IncidentDetail extends IncidentSummary {
  affected_services: { id: string; name: string; criticality: string }[]
}

export interface DecisionTrace {
  weights: Record<string, unknown>
  components: Record<string, unknown>
  feature_snapshot: Record<string, unknown>
  final_score?: number
}

export interface Prediction {
  change_id: string
  change_description?: string
  change_created_at?: string
  rule_confidence: number
  ml_probability: number
  hybrid_score: number
  confidence_band: ConfidenceBand
  decision_trace: DecisionTrace
}

export interface ExplanationResponse {
  incident_id: string
  explanation: string
  explanation_source: 'llm' | 'template'
  confidence: number | null
  rca_summary: {
    top_change_id?: string
    top_change_description?: string
    hybrid_score?: number
    confidence_band?: ConfidenceBand
    rule_confidence?: number
    ml_probability?: number
    graph_distance?: number
  } | null
  debug_trace: Record<string, unknown>
  predictions: Prediction[]
  context_flags: { weak_signal: boolean; close_competition: boolean }
  escalation: {
    should_escalate: boolean
    escalation_level: string
    reasons: string[]
  }
  quality: {
    quality_score: number
    quality_band: string
    factors: string[]
  }
}

export interface RunRcaResponse extends ExplanationResponse {
  status: string
  steps_completed: string[]
}

export interface FeedbackEntry {
  feedback_id: string
  change_id: string | null
  verdict: 'confirmed' | 'rejected' | 'corrected'
  comment: string | null
  created_at: string | null
}

export interface Service {
  id: string
  name: string
  owner_team: string | null
  criticality: string
  created_at: string
}

export interface DependencyEdge {
  id: string
  source_id: string
  target_id: string
  source: string
  target: string
  dependency_type: string
}

export interface Change {
  id: string
  change_type: string
  description: string
  git_ref: string
  created_at: string
  source?: string
  commit_sha?: string | null
  pr_number?: number | null
}

export interface GitConnection {
  id: string
  provider: string
  owner: string
  repo: string
  full_name: string
  default_branch: string
  token_masked: string
  auto_sync: boolean
  ingest_services_from_repo: boolean
  last_sync_at: string | null
  last_sync_status: string | null
  last_sync_message: string | null
  created_at: string
  webhook_url: string
}

export interface GitConnectResponse {
  connection: GitConnection
  webhook_secret: string
  webhook_setup: {
    url: string
    secret: string
    events: string[]
    instructions: string
  }
  services_ingested: { ingested?: number } | null
  initial_sync: Record<string, unknown>
}

export interface PullRequestCheck {
  id: string
  connection_id: string
  pr_number: number
  title: string
  head_sha: string
  base_branch: string
  state: string
  risk_band: string | null
  risk_score: number | null
  merge_recommendation: string | null
  services_touched: string[]
  change_id: string | null
  html_url: string | null
  updated_at: string
  repo: string
}

export interface GitEvent {
  id: string
  event_type: string
  git_ref: string | null
  pr_number: number | null
  commit_message: string | null
  author: string | null
  services_touched: string[]
  change_id: string | null
  created_at: string
  repo: string
}

export interface GraphNode {
  service_id: string
  service_name: string
  criticality: string
  depth: number
  direction: 'upstream' | 'downstream' | 'origin'
  dependency_type: string | null
  edge_weight: number
  propagation_probability: number
  impact_level: string
  risk_contribution: number
}

export interface BlastRadiusResponse {
  change_id: string
  origin_services: { id: string; name: string; criticality: string }[]
  blast_radius: {
    total_services: number
    downstream_count: number
    upstream_count: number
    score: number
    max_depth: number
  }
  downstream: GraphNode[]
  upstream: GraphNode[]
  failure_spread: {
    model: string
    expected_affected_count: number
    high_risk_count: number
    medium_risk_count: number
    low_risk_count: number
  }
  risk_panel: {
    overall_risk_score: number
    risk_band: string
    factors: string[]
  }
}

export interface ChangeImpactResponse {
  change_id: string
  impacts: { service: string; impact_level: string; criticality?: string }[]
  blast_radius_summary: BlastRadiusResponse['blast_radius'] | null
  risk_panel: BlastRadiusResponse['risk_panel'] | null
}

export interface FailureRiskResponse {
  service_id: string
  service_name: string
  criticality: string
  downstream: GraphNode[]
  upstream: GraphNode[]
  failure_spread: BlastRadiusResponse['failure_spread']
  risk_panel: BlastRadiusResponse['risk_panel']
  blast_radius_pct: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  source?: string
  citations?: { type: string; [key: string]: unknown }[]
}

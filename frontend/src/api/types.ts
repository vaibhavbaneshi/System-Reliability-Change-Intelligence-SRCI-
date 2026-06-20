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
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  source?: string
  citations?: { type: string; [key: string]: unknown }[]
}

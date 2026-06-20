import { api } from './client'
import type { ExplanationResponse, RunRcaResponse } from './types'

export const rcaApi = {
  explain: (id: string) => api.get<ExplanationResponse>(`/incidents/${id}/explanation`),
  run: (id: string) => api.post<RunRcaResponse>(`/incidents/${id}/run-rca`),
  predict: (id: string) => api.post<{ predictions: RunRcaResponse['predictions'] }>(`/incidents/${id}/predict`),
  reasoning: (id: string) => api.get<{ reasoning: Record<string, unknown> }>(`/incidents/${id}/reasoning`),
  evidence: (id: string) =>
    api.get<{ evidence: { id: string; source_type: string; reference: string; created_at: string }[] }>(
      `/incidents/${id}/evidence`,
    ),
  chat: (id: string, message: string) =>
    api.post<{ answer: string; source: string; citations: unknown[] }>(`/incidents/${id}/chat`, { message }),
  chatSuggestions: (id: string) => api.get<{ suggestions: string[] }>(`/incidents/${id}/chat/suggestions`),
  evaluate: (id: string) =>
    api.post<{
      incident_id: string
      metrics: Record<string, number | boolean>
      ground_truth: { change_id: string; label: number }[]
      predictions: {
        change_id: string
        hybrid_score: number
        confidence_band: string | null
        is_positive: boolean
      }[]
    }>(`/incidents/${id}/evaluate`),
}

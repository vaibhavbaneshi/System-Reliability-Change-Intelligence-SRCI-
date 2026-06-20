import { api } from './client'
import type {
  BlastRadiusResponse,
  Change,
  ChangeImpactResponse,
  DependencyEdge,
  FailureRiskResponse,
  Service,
} from './types'

export const servicesApi = {
  list: () => api.get<Service[]>('/services'),
  dependencies: () => api.get<DependencyEdge[]>('/dependencies'),
  failureRisk: (id: string) => api.get<FailureRiskResponse>(`/services/${id}/failure-risk`),
}

export const changesApi = {
  list: () => api.get<Change[]>('/changes'),
  get: (id: string) => api.get<Change & { error?: string }>(`/changes/${id}`),
  impact: (id: string) => api.get<ChangeImpactResponse>(`/changes/${id}/impact`),
  blastRadius: (id: string) => api.get<BlastRadiusResponse>(`/changes/${id}/blast-radius`),
}

export const autonomyApi = {
  status: () => api.get<Record<string, unknown>>('/autonomy/status'),
}

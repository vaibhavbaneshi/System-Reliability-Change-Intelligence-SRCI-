import { api } from './client'
import type { Change, DependencyEdge, Service } from './types'

export const servicesApi = {
  list: () => api.get<Service[]>('/services'),
  dependencies: () => api.get<DependencyEdge[]>('/dependencies'),
}

export const changesApi = {
  list: () => api.get<Change[]>('/changes'),
  get: (id: string) => api.get<Change & { error?: string }>(`/changes/${id}`),
  impact: (id: string) => api.get<{ service: string; impact_level: string }[]>(`/changes/${id}/impact`),
}

export const autonomyApi = {
  status: () => api.get<Record<string, unknown>>('/autonomy/status'),
}

import { api } from './client'
import type { IncidentDetail, IncidentSummary } from './types'

export const incidentsApi = {
  list: () => api.get<{ incidents: IncidentSummary[] }>('/incidents'),
  weakRca: () => api.get<{ incidents: IncidentSummary[] }>('/incidents/weak-rca'),
  get: (id: string) => api.get<IncidentDetail>(`/incidents/${id}`),
}

import { api } from './client'
import type { FeedbackEntry } from './types'

export const feedbackApi = {
  list: (incidentId: string) =>
    api.get<{ feedback: FeedbackEntry[] }>(`/incidents/${incidentId}/feedback`),
  submit: (
    incidentId: string,
    body: { verdict: 'confirmed' | 'rejected' | 'corrected'; change_id?: string; comment?: string },
  ) => api.post(`/incidents/${incidentId}/feedback`, body),
}

import { api } from './client'
import type { GitConnection, GitConnectResponse, GitEvent, PullRequestCheck } from './types'

export const gitApi = {
  connect: (body: {
    owner: string
    repo: string
    access_token: string
    default_branch?: string
    ingest_services_from_repo?: boolean
  }) => api.post<GitConnectResponse>('/git/connect', body),

  connections: () => api.get<{ connections: GitConnection[] }>('/git/connections'),

  disconnect: (id: string) => api.delete<{ deleted: boolean }>(`/git/connections/${id}`),

  sync: (id: string) => api.post<Record<string, unknown>>(`/git/connections/${id}/sync`),

  pullRequests: () => api.get<{ pull_requests: PullRequestCheck[] }>('/git/pull-requests'),

  events: () => api.get<{ events: GitEvent[] }>('/git/events'),
}

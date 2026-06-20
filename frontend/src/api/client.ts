export function getApiKey(): string | null {
  return localStorage.getItem('srci_api_key')
}

export function setApiKey(key: string): void {
  localStorage.setItem('srci_api_key', key)
}

export function clearApiKey(): void {
  localStorage.removeItem('srci_api_key')
}

function authHeaders(): Record<string, string> {
  const key = getApiKey()
  if (!key) return {}
  return { Authorization: `Bearer ${key}` }
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(init?.headers || {}),
    },
    ...init,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || JSON.stringify(body)
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail)
  }
  return res.json() as Promise<T>
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(path),
  post: <T>(path: string, body?: unknown) =>
    apiFetch<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => apiFetch<T>(path, { method: 'DELETE' }),
}

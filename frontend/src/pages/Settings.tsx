import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Play, Square, RefreshCw, Shield, Key } from 'lucide-react'
import { autonomyApi } from '@/api/services'
import { api, getApiKey, setApiKey, clearApiKey } from '@/api/client'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

type AuthMe = {
  tenant_id: string
  role: string
  email: string | null
  auth_enabled: string
}

type LlmUsage = {
  budget_tokens: number
  used_tokens: number
  remaining_tokens: number
  utilization_pct: number
}

export default function Settings() {
  const [apiKeyInput, setApiKeyInput] = useState(getApiKey() || '')
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['autonomy-status'],
    queryFn: () => autonomyApi.status(),
    refetchInterval: 15000,
  })

  const authQuery = useQuery({
    queryKey: ['auth-me'],
    queryFn: () => api.get<AuthMe>('/auth/me'),
  })

  const llmQuery = useQuery({
    queryKey: ['llm-usage'],
    queryFn: () => api.get<LlmUsage>('/enterprise/llm-usage'),
  })

  const saveApiKey = () => {
    if (apiKeyInput.trim()) setApiKey(apiKeyInput.trim())
    else clearApiKey()
    authQuery.refetch()
  }

  return (
    <div className="p-6 lg:p-8 max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Authentication, cost controls, and autonomy pipeline status.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Key size={16} /> API authentication
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            When <code className="font-mono text-xs">SRCI_AUTH_ENABLED=true</code>, set your API key
            (demo: <code className="font-mono text-xs">srci_demo_key</code>).
          </p>
          <div className="flex gap-2">
            <input
              type="password"
              placeholder="Bearer API key"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              aria-label="API key"
              className="flex h-9 w-full rounded-md border border-border bg-background px-3 py-1 text-sm"
            />
            <Button onClick={saveApiKey}>Save</Button>
          </div>
          {authQuery.data && (
            <div className="text-sm space-y-1 pt-2 border-t border-border">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tenant</span>
                <span className="font-mono text-xs">{authQuery.data.tenant_id.slice(0, 8)}…</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Role</span>
                <Badge variant="secondary">{authQuery.data.role}</Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <QueryWrapper isLoading={llmQuery.isLoading} isError={llmQuery.isError} error={llmQuery.error as Error}>
        {llmQuery.data && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Shield size={16} /> LLM token budget
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground block text-xs">Used / Budget</span>
                  <span className="font-mono">
                    {llmQuery.data.used_tokens.toLocaleString()} /{' '}
                    {llmQuery.data.budget_tokens.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground block text-xs">Utilization</span>
                  <span className="font-mono">{llmQuery.data.utilization_pct}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </QueryWrapper>

      <QueryWrapper
        isLoading={isLoading}
        isError={isError}
        error={error as Error}
        onRetry={refetch}
      >
        {data && (
          <div className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-base">Autonomy monitor</CardTitle>
                <Button variant="ghost" size="icon" onClick={() => refetch()} aria-label="Refresh status">
                  <RefreshCw size={16} className={isFetching ? 'animate-spin' : ''} />
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <Badge variant={data.running ? 'success' : 'secondary'}>
                    {data.running ? 'Running' : 'Stopped'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Environment flag</span>
                  <Badge variant={data.autonomy_enabled_env ? 'success' : 'secondary'}>
                    {data.autonomy_enabled_env ? 'AUTONOMY_ENABLED' : 'Disabled'}
                  </Badge>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground block text-xs">Unprocessed</span>
                    <span className="font-mono text-lg">{String(data.unprocessed_incidents ?? 0)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block text-xs">Active workers</span>
                    <span className="font-mono text-lg">{String(data.active_workers ?? 0)}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block text-xs">Poll interval</span>
                    <span className="font-mono text-lg">{String(data.poll_interval_sec ?? '—')}s</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block text-xs">Batch limit</span>
                    <span className="font-mono text-lg">{String(data.poll_batch_limit ?? '—')}</span>
                  </div>
                </div>

                {data.last_result != null && (
                  <div className="rounded-lg border border-border bg-background/50 p-3">
                    <p className="text-xs font-semibold text-muted-foreground mb-2">Last poll result</p>
                    <pre className="text-[10px] font-mono text-muted-foreground overflow-x-auto">
                      {JSON.stringify(data.last_result, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Control endpoints</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Start and stop the autonomy monitor via the API. These controls are read-only in the UI.
                </p>
                <div className="flex flex-wrap gap-3">
                  <Button variant="outline" asChild>
                    <Link to="/analytics">
                      <Play size={16} />
                      POST /autonomy/start
                    </Link>
                  </Button>
                  <Button variant="outline" asChild>
                    <Link to="/analytics">
                      <Square size={16} />
                      POST /autonomy/stop
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </QueryWrapper>
    </div>
  )
}

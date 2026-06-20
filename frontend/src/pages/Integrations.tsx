import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { GitBranch, Link2, RefreshCw, Trash2, Copy, Check } from 'lucide-react'
import { toast } from 'sonner'
import { gitApi } from '@/api/git'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function Integrations() {
  const qc = useQueryClient()
  const [owner, setOwner] = useState('')
  const [repo, setRepo] = useState('')
  const [token, setToken] = useState('')
  const [branch, setBranch] = useState('main')
  const [webhookInfo, setWebhookInfo] = useState<{ url: string; secret: string } | null>(null)
  const [copied, setCopied] = useState<string | null>(null)

  const connectionsQuery = useQuery({
    queryKey: ['git-connections'],
    queryFn: () => gitApi.connections(),
  })

  const eventsQuery = useQuery({
    queryKey: ['git-events'],
    queryFn: () => gitApi.events(),
    refetchInterval: 30000,
  })

  const connectMutation = useMutation({
    mutationFn: () =>
      gitApi.connect({
        owner: owner.trim(),
        repo: repo.trim(),
        access_token: token.trim(),
        default_branch: branch.trim() || 'main',
        ingest_services_from_repo: true,
      }),
    onSuccess: (data) => {
      toast.success(`Connected ${data.connection.full_name}`)
      setWebhookInfo({ url: data.webhook_setup.url, secret: data.webhook_setup.secret })
      setToken('')
      qc.invalidateQueries({ queryKey: ['git-connections'] })
      qc.invalidateQueries({ queryKey: ['git-events'] })
      qc.invalidateQueries({ queryKey: ['changes'] })
      qc.invalidateQueries({ queryKey: ['git-pull-requests'] })
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const syncMutation = useMutation({
    mutationFn: (id: string) => gitApi.sync(id),
    onSuccess: () => {
      toast.success('Sync complete')
      qc.invalidateQueries({ queryKey: ['git-connections'] })
      qc.invalidateQueries({ queryKey: ['git-events'] })
      qc.invalidateQueries({ queryKey: ['changes'] })
      qc.invalidateQueries({ queryKey: ['git-pull-requests'] })
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const disconnectMutation = useMutation({
    mutationFn: (id: string) => gitApi.disconnect(id),
    onSuccess: () => {
      toast.success('Disconnected')
      qc.invalidateQueries({ queryKey: ['git-connections'] })
    },
  })

  const copy = (text: string, key: string) => {
    navigator.clipboard.writeText(text)
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  const connections = connectionsQuery.data?.connections ?? []
  const events = eventsQuery.data?.events ?? []

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Git integration</h1>
        <p className="text-muted-foreground">
          Connect a GitHub repository. SRCI auto-tracks commits and runs pre-merge risk checks on open PRs.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Link2 size={16} /> Connect GitHub
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Create a{' '}
            <a
              href="https://github.com/settings/tokens"
              target="_blank"
              rel="noreferrer"
              className="text-primary hover:underline"
            >
              Personal Access Token
            </a>{' '}
            with <code className="text-xs">repo</code> scope.
          </p>
          <div className="grid sm:grid-cols-2 gap-3">
            <input
              className="h-9 rounded-md border border-border bg-background px-3 text-sm"
              placeholder="Owner (org or user)"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
            />
            <input
              className="h-9 rounded-md border border-border bg-background px-3 text-sm"
              placeholder="Repository name"
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
            />
            <input
              className="h-9 rounded-md border border-border bg-background px-3 text-sm sm:col-span-2"
              type="password"
              placeholder="GitHub token (ghp_...)"
              value={token}
              onChange={(e) => setToken(e.target.value)}
            />
            <input
              className="h-9 rounded-md border border-border bg-background px-3 text-sm"
              placeholder="Default branch"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
            />
          </div>
          <Button
            onClick={() => connectMutation.mutate()}
            disabled={!owner || !repo || !token || connectMutation.isPending}
          >
            {connectMutation.isPending ? 'Connecting…' : 'Connect & sync'}
          </Button>
        </CardContent>
      </Card>

      {webhookInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Webhook setup (for live updates)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="text-muted-foreground">
              Add this webhook in GitHub → repo Settings → Webhooks. Select <strong>push</strong> and{' '}
              <strong>pull request</strong> events.
            </p>
            <div className="flex items-center gap-2">
              <code className="flex-1 text-xs bg-muted p-2 rounded overflow-x-auto">{webhookInfo.url}</code>
              <Button variant="outline" size="icon" onClick={() => copy(webhookInfo.url, 'url')}>
                {copied === 'url' ? <Check size={14} /> : <Copy size={14} />}
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <code className="flex-1 text-xs bg-muted p-2 rounded overflow-x-auto">{webhookInfo.secret}</code>
              <Button variant="outline" size="icon" onClick={() => copy(webhookInfo.secret, 'secret')}>
                {copied === 'secret' ? <Check size={14} /> : <Copy size={14} />}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <QueryWrapper
        isLoading={connectionsQuery.isLoading}
        isError={connectionsQuery.isError}
        error={connectionsQuery.error as Error}
        onRetry={() => connectionsQuery.refetch()}
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Connected repositories</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {connections.length === 0 ? (
              <p className="text-sm text-muted-foreground">No repositories connected yet.</p>
            ) : (
              connections.map((c) => (
                <div
                  key={c.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border border-border rounded-lg p-4"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <GitBranch size={16} className="text-primary" />
                      <span className="font-medium">{c.full_name}</span>
                      <Badge variant="outline">{c.default_branch}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Token {c.token_masked}
                      {c.last_sync_at && ` · Last sync ${new Date(c.last_sync_at).toLocaleString()}`}
                    </p>
                    {c.last_sync_message && (
                      <p className="text-xs text-muted-foreground">{c.last_sync_message}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => syncMutation.mutate(c.id)}
                      disabled={syncMutation.isPending}
                    >
                      <RefreshCw size={14} className={syncMutation.isPending ? 'animate-spin' : ''} />
                      Sync
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => disconnectMutation.mutate(c.id)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </QueryWrapper>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Recent Git activity</CardTitle>
        </CardHeader>
        <CardContent>
          {events.length === 0 ? (
            <p className="text-sm text-muted-foreground">Commits and PRs will appear here after sync or webhook events.</p>
          ) : (
            <ul className="space-y-2">
              {events.slice(0, 15).map((ev) => (
                <li key={ev.id} className="text-sm border border-border rounded-lg p-3">
                  <div className="flex flex-wrap gap-2 items-center">
                    <Badge variant="secondary">{ev.event_type}</Badge>
                    <span className="text-muted-foreground">{ev.repo}</span>
                    {ev.pr_number != null && <span className="font-mono text-xs">PR #{ev.pr_number}</span>}
                  </div>
                  <p className="mt-1">{ev.commit_message || ev.git_ref?.slice(0, 8)}</p>
                  {ev.services_touched.length > 0 && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Services: {ev.services_touched.join(', ')}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

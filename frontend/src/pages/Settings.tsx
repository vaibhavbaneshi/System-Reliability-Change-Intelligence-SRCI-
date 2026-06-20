import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Play, Square, RefreshCw } from 'lucide-react'
import { autonomyApi } from '@/api/services'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function Settings() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['autonomy-status'],
    queryFn: () => autonomyApi.status(),
    refetchInterval: 15000,
  })

  return (
    <div className="p-6 lg:p-8 max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Autonomy pipeline configuration and operational status.
        </p>
      </div>

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
                <p className="text-xs text-muted-foreground">
                  Use curl or your API client: <code className="font-mono">curl -X POST /autonomy/start</code>
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </QueryWrapper>
    </div>
  )
}

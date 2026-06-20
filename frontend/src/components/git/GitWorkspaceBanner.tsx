import { useQuery } from '@tanstack/react-query'
import { GitBranch, Info } from 'lucide-react'
import { gitApi } from '@/api/git'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

export default function GitWorkspaceBanner() {
  const { data } = useQuery({
    queryKey: ['git-workspace'],
    queryFn: () => gitApi.workspace(),
  })

  const conn = data?.connection
  if (!conn) {
    return (
      <Card className="border-border">
        <CardContent className="pt-6 flex gap-3 text-sm text-muted-foreground">
          <Info size={18} className="shrink-0 mt-0.5" />
          <p>
            No Git repo connected. Services shown here come from the local demo seed. Connect your repo under{' '}
            <strong className="text-foreground">Integrations</strong> to import{' '}
            <code className="text-xs">service.yaml</code> definitions from GitHub.
          </p>
        </CardContent>
      </Card>
    )
  }

  const gitCount = data?.git_services ?? 0
  const paths = conn.service_yaml_paths ?? []

  return (
    <Card className="border-primary/25 bg-primary/5">
      <CardContent className="pt-6 space-y-3 text-sm">
        <div className="flex flex-wrap items-center gap-2">
          <GitBranch size={16} className="text-primary" />
          <span className="font-medium text-foreground">{conn.full_name}</span>
          <Badge variant="outline">{conn.default_branch}</Badge>
          <Badge variant="success">{gitCount} service(s) from Git</Badge>
          {conn.last_sync_at && (
            <span className="text-xs text-muted-foreground">
              Last sync {new Date(conn.last_sync_at).toLocaleString()}
            </span>
          )}
        </div>
        {paths.length > 0 && (
          <ul className="text-xs font-mono text-muted-foreground space-y-1 pl-5 list-disc">
            {paths.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        )}
        <p className="text-muted-foreground">
          This repository defines the same sample services as the SRCI demo (<code className="text-xs">auth-service</code>,{' '}
          <code className="text-xs">billing-service</code>, <code className="text-xs">notification-service</code>), so
          names and the graph look identical to demo data — that is expected. Edit a{' '}
          <code className="text-xs">service.yaml</code> in GitHub and click <strong className="text-foreground">Sync</strong>{' '}
          on Integrations to see updates here.
        </p>
      </CardContent>
    </Card>
  )
}

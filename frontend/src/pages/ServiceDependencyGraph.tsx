import { useQuery } from '@tanstack/react-query'
import { servicesApi } from '@/api/services'
import DependencyGraph from '@/components/graph/DependencyGraph'
import GitWorkspaceBanner from '@/components/git/GitWorkspaceBanner'

export default function ServiceDependencyGraph() {
  const servicesQuery = useQuery({
    queryKey: ['services'],
    queryFn: () => servicesApi.list(),
  })

  const depsQuery = useQuery({
    queryKey: ['dependencies'],
    queryFn: () => servicesApi.dependencies(),
  })

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Service dependencies</h1>
        <p className="text-muted-foreground">
          Interactive graph of service relationships and dependency types.
        </p>
      </div>

      <GitWorkspaceBanner />

      <DependencyGraph
        services={servicesQuery.data}
        dependencies={depsQuery.data}
        isLoading={servicesQuery.isLoading || depsQuery.isLoading}
        isError={servicesQuery.isError || depsQuery.isError}
        error={(servicesQuery.error ?? depsQuery.error) as Error}
        onRetry={() => {
          servicesQuery.refetch()
          depsQuery.refetch()
        }}
      />
    </div>
  )
}

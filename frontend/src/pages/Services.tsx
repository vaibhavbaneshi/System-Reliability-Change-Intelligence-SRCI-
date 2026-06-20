import { useQuery } from '@tanstack/react-query'
import { servicesApi } from '@/api/services'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

const criticalityVariant = (c: string) => {
  const l = c.toLowerCase()
  if (l === 'critical') return 'destructive' as const
  if (l === 'high') return 'warning' as const
  return 'secondary' as const
}

export default function Services() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['services'],
    queryFn: () => servicesApi.list(),
  })

  const services = data ?? []

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Services</h1>
        <p className="text-muted-foreground">
          Registered services and their criticality for incident correlation.
        </p>
      </div>

      <QueryWrapper
        isLoading={isLoading}
        isError={isError}
        error={error as Error}
        onRetry={refetch}
        isEmpty={services.length === 0}
        emptyTitle="No services registered"
        emptyDescription="Services will appear here once ingested."
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((service) => (
            <Card key={service.id}>
              <CardContent className="p-4 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-foreground">{service.name}</h3>
                  <Badge variant={criticalityVariant(service.criticality)} className="capitalize shrink-0">
                    {service.criticality}
                  </Badge>
                </div>
                <p className="text-xs font-mono text-muted-foreground">{service.id}</p>
                {service.owner_team && (
                  <p className="text-xs text-muted-foreground">Team: {service.owner_team}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Added {new Date(service.created_at).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </QueryWrapper>
    </div>
  )
}

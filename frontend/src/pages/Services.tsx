import { ServiceHealthCard } from '../components'
import { mockServices } from '../data/mockData'

export default function Services() {
  return (
    <div className="p-8 max-w-7xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Services</h1>
        <p className="text-muted-foreground">Real-time service health monitoring and dependency tracking</p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {mockServices.map(service => (
          <ServiceHealthCard
            key={service.id}
            name={service.name}
            health={service.health}
            status={service.status}
            incidentCount={service.incidentCount7d}
            blastRadius={service.blastRadius}
            trend={service.health < 80 ? 'down' : 'up'}
            onClick={() => console.log('Clicked:', service.name)}
          />
        ))}
      </div>
    </div>
  )
}

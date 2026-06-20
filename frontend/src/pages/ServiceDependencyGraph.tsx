export default function ServiceDependencyGraph() {
  return (
    <div className="p-8 max-w-7xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Service Dependency Graph</h1>
        <p className="text-muted-foreground">Visual service dependency map with blast radius impact analysis</p>
      </div>

      <div className="bg-card border border-border rounded-lg p-8 min-h-96 flex items-center justify-center">
        <div className="text-center space-y-4">
          <svg width="200" height="160" className="mx-auto opacity-40" viewBox="0 0 200 160">
            <circle cx="40" cy="40" r="20" fill="none" stroke="currentColor" strokeWidth="2" className="text-primary" />
            <circle cx="100" cy="40" r="20" fill="none" stroke="currentColor" strokeWidth="2" className="text-primary" />
            <circle cx="160" cy="40" r="20" fill="none" stroke="currentColor" strokeWidth="2" className="text-primary" />
            <circle cx="70" cy="100" r="20" fill="none" stroke="currentColor" strokeWidth="2" className="text-primary" />
            <circle cx="130" cy="100" r="20" fill="none" stroke="currentColor" strokeWidth="2" className="text-primary" />

            {/* Lines */}
            <line x1="60" y1="40" x2="80" y2="40" stroke="currentColor" strokeWidth="1" className="text-border" />
            <line x1="120" y1="40" x2="140" y2="40" stroke="currentColor" strokeWidth="1" className="text-border" />
            <line x1="40" y1="60" x2="70" y2="80" stroke="currentColor" strokeWidth="1" className="text-border" />
            <line x1="100" y1="60" x2="70" y2="80" stroke="currentColor" strokeWidth="1" className="text-border" />
            <line x1="100" y1="60" x2="130" y2="80" stroke="currentColor" strokeWidth="1" className="text-border" />
            <line x1="160" y1="60" x2="130" y2="80" stroke="currentColor" strokeWidth="1" className="text-border" />
          </svg>
          <h3 className="font-semibold text-foreground">Service Dependency Graph</h3>
          <p className="text-sm text-muted-foreground">
            Placeholder for React Flow integration. Shows service dependencies, health status, and blast radius impact.
          </p>
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium">
            Load Graph
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="w-3 h-3 rounded-full bg-green-500 mb-2"></div>
          <p className="text-sm font-medium text-foreground">Healthy</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="w-3 h-3 rounded-full bg-yellow-500 mb-2"></div>
          <p className="text-sm font-medium text-foreground">Degraded</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="w-3 h-3 rounded-full bg-red-500 mb-2"></div>
          <p className="text-sm font-medium text-foreground">Down</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <p className="text-sm font-medium text-foreground">→ Dependency</p>
        </div>
      </div>
    </div>
  )
}

import { useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { DependencyEdge, Service } from '@/api/types'
import QueryWrapper from '@/components/common/QueryWrapper'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface DependencyGraphProps {
  services: Service[] | undefined
  dependencies: DependencyEdge[] | undefined
  isLoading: boolean
  isError: boolean
  error?: Error | null
  onRetry?: () => void
}

const criticalityColor: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#3b82f6',
}

export default function DependencyGraph({
  services,
  dependencies,
  isLoading,
  isError,
  error,
  onRetry,
}: DependencyGraphProps) {
  const { nodes, edges } = useMemo(() => {
    if (!services?.length) return { nodes: [] as Node[], edges: [] as Edge[] }

    const serviceNodes: Node[] = services.map((service, index) => {
      const col = index % 4
      const row = Math.floor(index / 4)
      return {
        id: service.id,
        data: { label: service.name },
        position: { x: col * 220, y: row * 120 },
        style: {
          background: '#1e293b',
          color: '#e2e8f0',
          border: `2px solid ${criticalityColor[service.criticality] ?? '#64748b'}`,
          borderRadius: 8,
          padding: 10,
          fontSize: 12,
          minWidth: 140,
        },
      }
    })

    const flowEdges: Edge[] = (dependencies ?? []).map((dep) => ({
      id: dep.id,
      source: dep.source_id,
      target: dep.target_id,
      label: dep.dependency_type,
      animated: dep.dependency_type === 'critical',
      style: { stroke: '#64748b' },
      labelStyle: { fill: '#94a3b8', fontSize: 10 },
    }))

    return { nodes: serviceNodes, edges: flowEdges }
  }, [services, dependencies])

  return (
    <QueryWrapper
      isLoading={isLoading}
      isError={isError}
      error={error}
      onRetry={onRetry}
      isEmpty={!isLoading && !isError && nodes.length === 0}
      emptyTitle="No services to graph"
      emptyDescription="Register services to visualize dependency relationships."
      skeleton={
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-[480px] w-full" />
          </CardContent>
        </Card>
      }
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Service dependency graph</CardTitle>
          <p className="text-sm text-muted-foreground">
            Pan and zoom to explore upstream and downstream dependencies.
          </p>
        </CardHeader>
        <CardContent>
          <div className="h-[480px] rounded-lg border border-border overflow-hidden bg-background">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              fitView
              minZoom={0.3}
              maxZoom={1.5}
              proOptions={{ hideAttribution: true }}
            >
              <Background color="#334155" gap={16} />
              <Controls />
              <MiniMap
                nodeColor="#1e293b"
                maskColor="rgba(0,0,0,0.6)"
                style={{ background: '#0f172a' }}
              />
            </ReactFlow>
          </div>
        </CardContent>
      </Card>
    </QueryWrapper>
  )
}

export interface Incident {
  id: string
  title: string
  severity: 'critical' | 'warning' | 'info'
  status: 'active' | 'investigating' | 'resolved'
  service: string
  blastRadius: number
  rcaConfidence: number
  createdAt: Date
  duration: number
  owner: string
  timeline: TimelineEvent[]
  hypotheses: Hypothesis[]
  evidence: Evidence[]
  decisionTrace: DecisionTraceStep[]
}

export interface TimelineEvent {
  id: string
  timestamp: Date
  type: 'alert' | 'deploy' | 'metric' | 'error'
  title: string
  description: string
}

export interface Hypothesis {
  id: string
  title: string
  confidence: number
  supportingEvidence: string[]
  contradictingEvidence: string[]
  riskLevel: 'low' | 'medium' | 'high'
  affectedServices: string[]
  status: 'proposed' | 'in-progress' | 'validated' | 'rejected'
}

export interface Evidence {
  id: string
  type: 'log' | 'metric' | 'alert' | 'change' | 'trace'
  title: string
  strength: 'weak' | 'moderate' | 'strong'
  relevance: number
  content: string
  timestamp: Date
}

export interface DecisionTraceStep {
  id: string
  stage: string
  input: string
  reasoning: string
  confidence: number
  alternatives: string[]
}

export interface Service {
  id: string
  name: string
  health: number
  incidentCount7d: number
  blastRadius: number
  owner: string
  status: 'healthy' | 'degraded' | 'down'
}

export interface Change {
  id: string
  title: string
  service: string
  riskScore: number
  correlatedIncidents: number
  author: string
  timestamp: Date
}

export interface AutonomousAction {
  id: string
  title: string
  service: string
  confidence: number
  status: 'pending' | 'approved' | 'executed' | 'rolled_back'
  successRate: number
  timestamp: Date
}

// Mock Incidents
export const mockIncidents: Incident[] = [
  {
    id: 'INC-001',
    title: 'Payment Service Database Connection Timeout',
    severity: 'critical',
    status: 'investigating',
    service: 'payment-service',
    blastRadius: 85,
    rcaConfidence: 78,
    createdAt: new Date(Date.now() - 45 * 60000),
    duration: 45,
    owner: 'Sarah Chen',
    timeline: [
      {
        id: 'evt-1',
        timestamp: new Date(Date.now() - 45 * 60000),
        type: 'alert',
        title: 'High Error Rate Detected',
        description: 'Payment service error rate exceeded 15% threshold',
      },
      {
        id: 'evt-2',
        timestamp: new Date(Date.now() - 40 * 60000),
        type: 'metric',
        title: 'Database Connection Pool Exhausted',
        description: 'Connection pool hit 100% utilization',
      },
      {
        id: 'evt-3',
        timestamp: new Date(Date.now() - 35 * 60000),
        type: 'deploy',
        title: 'Connection Pool Size Increased',
        description: 'Scaled pool from 50 to 100 connections',
      },
    ],
    hypotheses: [
      {
        id: 'hyp-1',
        title: 'Memory Leak in Payment Processing Queue',
        confidence: 82,
        supportingEvidence: ['Memory usage spike', 'Queue depth increase', 'Timeout correlation'],
        contradictingEvidence: ['Recent deploy was stable'],
        riskLevel: 'high',
        affectedServices: ['payment-service', 'order-service'],
        status: 'in-progress',
      },
      {
        id: 'hyp-2',
        title: 'External Database Provider Degradation',
        confidence: 45,
        supportingEvidence: ['Latency spike in queries'],
        contradictingEvidence: ['Other services performing normally'],
        riskLevel: 'medium',
        affectedServices: ['payment-service'],
        status: 'proposed',
      },
    ],
    evidence: [
      {
        id: 'ev-1',
        type: 'metric',
        title: 'Memory Usage Trend',
        strength: 'strong',
        relevance: 95,
        content: 'Memory usage increased from 2.1GB to 3.8GB over 30 minutes',
        timestamp: new Date(Date.now() - 30 * 60000),
      },
      {
        id: 'ev-2',
        type: 'log',
        title: 'Connection Pool Errors',
        strength: 'strong',
        relevance: 92,
        content: 'Unable to acquire connection: pool exhausted',
        timestamp: new Date(Date.now() - 25 * 60000),
      },
    ],
    decisionTrace: [
      {
        id: 'dt-1',
        stage: 'Observation',
        input: 'High error rate alert triggered',
        reasoning: 'Error rate spike indicates service distress',
        confidence: 98,
        alternatives: [],
      },
      {
        id: 'dt-2',
        stage: 'Analysis',
        input: 'Database connection timeout errors',
        reasoning: 'Connection pool exhaustion limits throughput',
        confidence: 94,
        alternatives: ['Application-level timeout'],
      },
      {
        id: 'dt-3',
        stage: 'Correlation',
        input: 'Memory leak pattern + connection pool size',
        reasoning: 'Leaked connections prevent new acquisitions',
        confidence: 87,
        alternatives: ['External provider issue'],
      },
      {
        id: 'dt-4',
        stage: 'Hypothesis',
        input: 'Memory trend + queue metrics',
        reasoning: 'Payment processing queue has memory leak',
        confidence: 82,
        alternatives: ['Provider issue', 'Network problem'],
      },
    ],
  },
  {
    id: 'INC-002',
    title: 'API Gateway Rate Limiting Not Applied',
    severity: 'warning',
    status: 'resolved',
    service: 'api-gateway',
    blastRadius: 42,
    rcaConfidence: 91,
    createdAt: new Date(Date.now() - 2 * 60 * 60000),
    duration: 18,
    owner: 'Mike Rodriguez',
    timeline: [],
    hypotheses: [],
    evidence: [],
    decisionTrace: [],
  },
  {
    id: 'INC-003',
    title: 'Cache Invalidation Delay',
    severity: 'info',
    status: 'resolved',
    service: 'cache-layer',
    blastRadius: 28,
    rcaConfidence: 87,
    createdAt: new Date(Date.now() - 4 * 60 * 60000),
    duration: 12,
    owner: 'Emily Watson',
    timeline: [],
    hypotheses: [],
    evidence: [],
    decisionTrace: [],
  },
]

// Mock Services
export const mockServices: Service[] = [
  { id: 'svc-1', name: 'Payment Service', health: 78, incidentCount7d: 3, blastRadius: 85, owner: 'Finance Team', status: 'degraded' },
  { id: 'svc-2', name: 'User Service', health: 95, incidentCount7d: 1, blastRadius: 60, owner: 'Identity Team', status: 'healthy' },
  { id: 'svc-3', name: 'API Gateway', health: 88, incidentCount7d: 2, blastRadius: 100, owner: 'Platform Team', status: 'healthy' },
  { id: 'svc-4', name: 'Cache Layer', health: 91, incidentCount7d: 1, blastRadius: 45, owner: 'Infrastructure', status: 'healthy' },
  { id: 'svc-5', name: 'Order Service', health: 84, incidentCount7d: 2, blastRadius: 65, owner: 'Commerce Team', status: 'degraded' },
  { id: 'svc-6', name: 'Search Service', health: 97, incidentCount7d: 0, blastRadius: 30, owner: 'Search Team', status: 'healthy' },
]

// Mock Changes
export const mockChanges: Change[] = [
  { id: 'chg-1', title: 'Deployed payment-service v2.1.0', service: 'payment-service', riskScore: 68, correlatedIncidents: 2, author: 'alice@company.com', timestamp: new Date(Date.now() - 90 * 60000) },
  { id: 'chg-2', title: 'Updated cache TTL configuration', service: 'cache-layer', riskScore: 42, correlatedIncidents: 0, author: 'bob@company.com', timestamp: new Date(Date.now() - 3 * 60 * 60000) },
  { id: 'chg-3', title: 'Scaled API gateway instances', service: 'api-gateway', riskScore: 55, correlatedIncidents: 1, author: 'charlie@company.com', timestamp: new Date(Date.now() - 5 * 60 * 60000) },
]

// Mock Autonomous Actions
export const mockAutonomousActions: AutonomousAction[] = [
  { id: 'act-1', title: 'Auto-scale payment service', service: 'payment-service', confidence: 87, status: 'executed', successRate: 94, timestamp: new Date(Date.now() - 30 * 60000) },
  { id: 'act-2', title: 'Restart cache service', service: 'cache-layer', confidence: 72, status: 'pending', successRate: 88, timestamp: new Date(Date.now() - 15 * 60000) },
  { id: 'act-3', title: 'Rollback payment service v2.1.0', service: 'payment-service', confidence: 65, status: 'pending', successRate: 91, timestamp: new Date(Date.now() - 5 * 60000) },
]

// Get incident by ID
export function getIncidentById(id: string): Incident | undefined {
  return mockIncidents.find(inc => inc.id === id)
}

// Get all incidents
export function getAllIncidents(): Incident[] {
  return mockIncidents
}

// Get critical incidents
export function getCriticalIncidents(): Incident[] {
  return mockIncidents.filter(inc => inc.severity === 'critical')
}

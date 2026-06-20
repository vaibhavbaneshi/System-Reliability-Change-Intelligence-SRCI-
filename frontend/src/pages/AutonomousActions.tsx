import { useState } from 'react'
import { CheckCircle, Clock, RotateCcw, Zap, Terminal, ShieldCheck, RefreshCw, Activity } from 'lucide-react'
import ConfidenceBadge from '../components/ConfidenceBadge'

interface AutonomousAction {
  id: string
  title: string
  service: string
  confidence: number
  status: 'pending' | 'approved' | 'executed' | 'rolled_back'
  successRate: number
  timestamp: Date
  commands: string[]
  logs: string[]
}

const initialActions: AutonomousAction[] = [
  { 
    id: 'act-1', 
    title: 'Auto-scale payment service', 
    service: 'payment-service', 
    confidence: 87, 
    status: 'executed', 
    successRate: 94, 
    timestamp: new Date(Date.now() - 30 * 60000),
    commands: [
      '# Scaling deployment replica set to handle traffic load spikes',
      'kubectl scale deployment payment-service --replicas=6 -n prod-us-east',
      '# Waiting for rolling update rollout status validation...',
      'kubectl rollout status deployment/payment-service -n prod-us-east'
    ],
    logs: [
      'INFO: Initializing container deployment scale verification...',
      'INFO: Desired replicas: 6, Current: 3',
      'INFO: Scaling replica set to 6 instances successful.',
      'SUCCESS: Rolling rollout finished. 6 / 6 pods active and healthy.'
    ]
  },
  { 
    id: 'act-2', 
    title: 'Restart cache service', 
    service: 'cache-layer', 
    confidence: 72, 
    status: 'pending', 
    successRate: 88, 
    timestamp: new Date(Date.now() - 15 * 60000),
    commands: [
      '# Clearing corrupted connection nodes and trigger rolling restart',
      'kubectl rollout restart deployment cache-layer -n prod-infra',
      '# Verifying cache TTL key invalidations...',
      'redis-cli -h cache-layer-service.prod-infra ping'
    ],
    logs: [
      'INFO: Starting rolling container pods restart...',
      'WARN: Redis connection pool timeout detected, retrying...',
      'INFO: Successfully recycled container pods cache-layer.',
      'SUCCESS: Redis host responded with PONG. Verification passed.'
    ]
  },
  { 
    id: 'act-3', 
    title: 'Rollback payment service v2.1.0', 
    service: 'payment-service', 
    confidence: 65, 
    status: 'pending', 
    successRate: 91, 
    timestamp: new Date(Date.now() - 5 * 60000),
    commands: [
      '# Reverting payment deployment patch to stable revision tag',
      'helm rollback payment-service 14 -n prod-us-east',
      '# Testing billing service HTTP endpoints connectivity...',
      'curl -f -X GET https://api.prod.company.com/billing/healthz'
    ],
    logs: [
      'INFO: Reverting deployment helm release to revision 14...',
      'INFO: Rev 14 tag: v2.0.9 (Stable release build)',
      'SUCCESS: Rolling back release completed.',
      'SUCCESS: Billing API health test returned HTTP 200 OK.'
    ]
  },
]

const statusConfig = {
  pending: { bg: 'bg-yellow-500/20 border-yellow-500/30', text: 'text-yellow-400', icon: Clock, label: 'Pending Review' },
  approved: { bg: 'bg-blue-500/20 border-blue-500/30', text: 'text-blue-400', icon: Zap, label: 'Approved' },
  executed: { bg: 'bg-green-500/20 border-green-500/30', text: 'text-green-400', icon: CheckCircle, label: 'Executed' },
  rolled_back: { bg: 'bg-orange-500/20 border-orange-500/30', text: 'text-orange-400', icon: RotateCcw, label: 'Rolled Back' },
}

export default function AutonomousActions() {
  const [actions, setActions] = useState<AutonomousAction[]>(initialActions)
  const [activeActionId, setActiveActionId] = useState<string | null>('act-2')
  const [isDryRunning, setIsDryRunning] = useState(false)
  const [dryRunLogs, setDryRunLogs] = useState<string[]>([])
  const [toastMessage, setToastMessage] = useState<string | null>(null)

  const activeAction = actions.find(a => a.id === activeActionId)

  const showToast = (msg: string) => {
    setToastMessage(msg)
    setTimeout(() => setToastMessage(null), 3000)
  }

  // Execute Dry-Run
  const runDryRun = (action: AutonomousAction) => {
    setIsDryRunning(true)
    setDryRunLogs([])
    
    let currentLine = 0
    const interval = setInterval(() => {
      if (currentLine < action.logs.length) {
        setDryRunLogs(prev => [...prev, `[DRY-RUN] ${action.logs[currentLine]}`])
        currentLine++
      } else {
        clearInterval(interval)
        setIsDryRunning(false)
        showToast('Dry-run completed successfully! Verification checks passed.')
      }
    }, 450)
  }

  // Execute Action
  const executeAction = (actionId: string) => {
    setActions(prev => prev.map(act => {
      if (act.id === actionId) {
        return { ...act, status: 'executed' }
      }
      return act
    }))
    showToast('Remediation action approved and successfully executed on prod cluster.')
  }

  // Reject Action
  const rejectAction = (actionId: string) => {
    setActions(prev => prev.filter(a => a.id !== actionId))
    setActiveActionId(null)
    showToast('Remediation action rejected and removed from operations queue.')
  }

  // Rollback Action
  const rollbackAction = (actionId: string) => {
    setActions(prev => prev.map(act => {
      if (act.id === actionId) {
        return { ...act, status: 'rolled_back' }
      }
      return act
    }))
    showToast('Remediation action rolled back successfully. Kubernetes pods scaled down.')
  }

  // Calculate statistics
  const totalExecuted = actions.filter(a => a.status === 'executed').length + 23 // mock constant + status
  const totalPending = actions.filter(a => a.status === 'pending').length

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 animate-fade-in">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Autonomous Remediation Actions</h1>
        <p className="text-xs text-muted-foreground mt-1">
          AI-generated automated incident mitigations with safety validation scopes and human-in-the-loop approvals.
        </p>
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 bg-primary/95 text-primary-foreground px-4 py-3 rounded-xl shadow-2xl z-50 text-xs font-bold border border-blue-400 animate-slide-in-up">
          {toastMessage}
        </div>
      )}

      {/* Overview stats cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-xl p-5 hover:border-primary/45 transition-colors">
          <p className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider mb-2">Total Executed</p>
          <p className="text-3xl font-black text-green-400">{totalExecuted}</p>
          <p className="text-[10px] text-muted-foreground mt-2">94% average success rate</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-5 hover:border-primary/45 transition-colors">
          <p className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider mb-2">Pending Approval</p>
          <p className="text-3xl font-black text-yellow-400">{totalPending}</p>
          <p className="text-[10px] text-muted-foreground mt-2">Requires engineer verification</p>
        </div>
        <div className="bg-card border border-border rounded-xl p-5 hover:border-primary/45 transition-colors">
          <p className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider mb-2">Rolled Back</p>
          <p className="text-3xl font-black text-orange-400">1</p>
          <p className="text-[10px] text-muted-foreground mt-2">Last 7 days operational logs</p>
        </div>
      </div>

      {/* Split Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: Actions List (6/12 width) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between text-xs mb-1">
            <span className="font-semibold text-muted-foreground">Remediation Logs ({actions.length})</span>
            <span className="text-[10px] text-muted-foreground bg-background px-2 py-0.5 rounded border border-border">
              Cluster scope: us-east
            </span>
          </div>

          <div className="space-y-3">
            {actions.map(action => {
              const isSelected = activeActionId === action.id
              const config = statusConfig[action.status]
              const StatusIcon = config.icon

              return (
                <div
                  key={action.id}
                  onClick={() => {
                    setActiveActionId(action.id)
                    setDryRunLogs([])
                  }}
                  className={`bg-card border rounded-xl p-5 hover:border-primary/50 hover:shadow-lg transition-all cursor-pointer relative ${
                    isSelected ? 'border-primary ring-1 ring-primary/20' : 'border-border'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2.5">
                        <StatusIcon size={16} className={config.text} />
                        <h3 className="font-bold text-foreground text-sm">
                          {action.title}
                        </h3>
                      </div>
                      <p className="text-[10px] text-muted-foreground">Service: {action.service}</p>
                    </div>

                    <div className="scale-90 origin-top-right">
                      <ConfidenceBadge confidence={action.confidence} size="sm" showPercentage={true} variant="circular" />
                    </div>
                  </div>

                  <div className="flex items-center justify-between border-t border-border/40 pt-3 text-xs">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${config.bg} ${config.text}`}>
                      {config.label}
                    </span>
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <Activity size={10} className="text-green-400" />
                      Success rate: {action.successRate}%
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right Side: Detailed execution inspection (6/12 width) */}
        <div className="lg:col-span-6">
          {activeAction ? (
            <div className="bg-card border border-border rounded-xl p-5 space-y-5 shadow-xl animate-slide-in-up">
              
              {/* Header */}
              <div className="border-b border-border pb-3 flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <ShieldCheck size={16} className="text-primary" />
                    <h3 className="font-bold text-foreground text-sm leading-tight">{activeAction.title}</h3>
                  </div>
                  <p className="text-[10px] text-muted-foreground">Microservice target: {activeAction.service}</p>
                </div>
                <div className="scale-90 origin-top-right">
                  <ConfidenceBadge confidence={activeAction.confidence} size="sm" showPercentage={true} variant="circular" />
                </div>
              </div>

              {/* Code execution CLI preview */}
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-1">
                  <Terminal size={12} className="text-primary" />
                  CLI Execution Preview
                </span>
                
                <div className="bg-background/80 border border-border p-3.5 rounded-lg font-mono text-[11px] text-foreground leading-relaxed overflow-x-auto space-y-1 shadow-inner">
                  {activeAction.commands.map((cmd, idx) => (
                    <p key={idx} className={cmd.startsWith('#') ? 'text-muted-foreground' : 'text-blue-400'}>
                      {cmd}
                    </p>
                  ))}
                </div>
              </div>

              {/* Dry-run CLI window */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                    Dry-Run Sandbox Output
                  </span>
                  {activeAction.status === 'pending' && (
                    <button
                      onClick={() => runDryRun(activeAction)}
                      disabled={isDryRunning}
                      className="px-2.5 py-1 bg-muted hover:bg-muted/80 text-foreground text-[10px] font-bold rounded border border-border transition-colors flex items-center gap-1"
                    >
                      {isDryRunning ? (
                        <>
                          <RefreshCw size={10} className="animate-spin" />
                          Testing...
                        </>
                      ) : (
                        'Run Dry-Run'
                      )}
                    </button>
                  )}
                </div>

                {dryRunLogs.length > 0 ? (
                  <div className="bg-background border border-border p-3 rounded-lg font-mono text-[10px] text-muted-foreground space-y-1 h-32 overflow-y-auto leading-relaxed shadow-inner">
                    {dryRunLogs.map((log, idx) => (
                      <p key={idx} className={log.includes('SUCCESS') ? 'text-green-400' : log.includes('WARN') ? 'text-yellow-400' : 'text-muted-foreground'}>
                        {log}
                      </p>
                    ))}
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-border rounded-lg p-6 text-center text-xs text-muted-foreground flex flex-col items-center justify-center gap-1 bg-background/20">
                    <Terminal size={22} className="opacity-20 mb-1" />
                    Click Run Dry-Run to inspect script validation testing logs.
                  </div>
                )}
              </div>

              {/* Success metrics */}
              <div className="grid grid-cols-2 gap-4 text-xs bg-background/50 border border-border/40 p-3 rounded-xl">
                <div>
                  <span className="text-[10px] text-muted-foreground block mb-0.5">Success metrics (7d)</span>
                  <span className="font-bold text-green-400 flex items-center gap-1">
                    <CheckCircle size={12} />
                    {activeAction.successRate}% Success rate
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground block mb-0.5">Verification status</span>
                  <span className="font-bold text-foreground">
                    {activeAction.status === 'pending' ? 'Unverified' : 'Verified & Safe'}
                  </span>
                </div>
              </div>

              {/* Actions controls */}
              <div className="pt-4 border-t border-border">
                {activeAction.status === 'pending' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => rejectAction(activeAction.id)}
                      className="flex-1 py-2 bg-muted hover:bg-muted/80 text-foreground text-xs font-bold rounded-lg border border-border transition-colors"
                    >
                      Reject Action
                    </button>
                    <button
                      onClick={() => executeAction(activeAction.id)}
                      className="flex-1 py-2 bg-green-500 text-green-foreground text-xs font-bold rounded-lg hover:bg-green-600 transition-colors shadow-md"
                    >
                      Approve & Execute
                    </button>
                  </div>
                )}

                {activeAction.status === 'executed' && (
                  <button
                    onClick={() => rollbackAction(activeAction.id)}
                    className="w-full py-2 bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 border border-orange-500/30 rounded-lg text-xs font-bold transition-colors"
                  >
                    Rollback Execution
                  </button>
                )}

                {activeAction.status === 'rolled_back' && (
                  <div className="bg-orange-500/10 border border-orange-500/30 text-orange-400 p-2.5 rounded-lg text-xs font-semibold text-center flex items-center justify-center gap-1.5 animate-pulse">
                    <RotateCcw size={12} />
                    This action was rolled back from production.
                  </div>
                )}
              </div>

            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-xs text-muted-foreground">
              Select an action from the remediation logs list to view CLI details.
            </div>
          )}
        </div>

      </div>

    </div>
  )
}

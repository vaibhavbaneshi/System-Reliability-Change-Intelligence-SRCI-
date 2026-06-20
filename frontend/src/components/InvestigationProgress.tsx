import { Check, Clock } from 'lucide-react'
import { cn } from '../utils/cn'

interface Milestone {
  id: string
  name: string
  completed: boolean
}

interface InvestigationProgressProps {
  progress: number
  currentStep: string
  milestones: Milestone[]
  estimatedTimeRemaining?: number
}

export default function InvestigationProgress({
  progress,
  currentStep,
  milestones,
  estimatedTimeRemaining,
}: InvestigationProgressProps) {
  return (
    <div className="space-y-6">
      {/* Progress Bar */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-foreground">Investigation Progress</span>
          <span className="text-sm font-bold text-primary">{progress}%</span>
        </div>
        <div className="w-full h-3 bg-background rounded-full overflow-hidden border border-border">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500 rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Current Step */}
      <div className="p-4 bg-background border border-primary/30 rounded-lg">
        <div className="flex items-start gap-3">
          <div className="mt-0.5">
            <Clock size={16} className="text-primary animate-pulse" />
          </div>
          <div className="flex-1">
            <p className="text-xs text-muted-foreground mb-1">Currently Analyzing</p>
            <p className="font-medium text-foreground">{currentStep}</p>
          </div>
        </div>
      </div>

      {/* Milestones */}
      <div>
        <p className="text-xs text-muted-foreground font-medium mb-3">Investigation Milestones</p>
        <div className="space-y-2">
          {milestones.map((milestone) => (
            <div key={milestone.id} className="flex items-center gap-3">
              <div className={cn(
                'w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all',
                milestone.completed
                  ? 'bg-green-500/20 border-green-500/50'
                  : 'bg-background border-muted'
              )}>
                {milestone.completed && <Check size={12} className="text-green-400" />}
              </div>
              <span className={cn(
                'text-sm',
                milestone.completed ? 'text-foreground line-through opacity-60' : 'text-foreground'
              )}>
                {milestone.name}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Estimated Time */}
      {estimatedTimeRemaining && (
        <div className="p-3 bg-muted/30 border border-muted rounded-lg">
          <p className="text-xs text-muted-foreground">Estimated Time Remaining</p>
          <p className="text-sm font-bold text-foreground mt-1">{estimatedTimeRemaining} minutes</p>
        </div>
      )}
    </div>
  )
}

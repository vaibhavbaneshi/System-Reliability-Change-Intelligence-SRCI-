import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Check, X, Edit3 } from 'lucide-react'
import type { Prediction } from '@/api/types'
import { feedbackApi } from '@/api/feedback'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface FeedbackPanelProps {
  incidentId: string
  predictions: Prediction[]
}

export default function FeedbackPanel({ incidentId, predictions }: FeedbackPanelProps) {
  const queryClient = useQueryClient()
  const [selectedChangeId, setSelectedChangeId] = useState(predictions[0]?.change_id ?? '')
  const [comment, setComment] = useState('')

  const { data: feedbackData } = useQuery({
    queryKey: ['feedback', incidentId],
    queryFn: () => feedbackApi.list(incidentId),
  })

  const submitMutation = useMutation({
    mutationFn: (verdict: 'confirmed' | 'rejected' | 'corrected') =>
      feedbackApi.submit(incidentId, {
        verdict,
        change_id: selectedChangeId || undefined,
        comment: comment.trim() || undefined,
      }),
    onSuccess: (_, verdict) => {
      toast.success(`Feedback submitted: ${verdict}`)
      setComment('')
      queryClient.invalidateQueries({ queryKey: ['feedback', incidentId] })
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Failed to submit feedback')
    },
  })

  const feedback = feedbackData?.feedback ?? []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Analyst feedback</CardTitle>
        <p className="text-sm text-muted-foreground">
          Confirm, reject, or correct the RCA hypothesis to improve future predictions.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {predictions.length > 0 && (
          <div className="space-y-2">
            <label htmlFor="change-select" className="text-xs font-medium text-muted-foreground">
              Change hypothesis
            </label>
            <select
              id="change-select"
              value={selectedChangeId}
              onChange={(e) => setSelectedChangeId(e.target.value)}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {predictions.map((p) => (
                <option key={p.change_id} value={p.change_id}>
                  {p.change_description ?? p.change_id}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="space-y-2">
          <label htmlFor="feedback-comment" className="text-xs font-medium text-muted-foreground">
            Comment (optional)
          </label>
          <textarea
            id="feedback-comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            placeholder="Add context for this verdict…"
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          <Button
            onClick={() => submitMutation.mutate('confirmed')}
            disabled={submitMutation.isPending || !selectedChangeId}
            aria-label="Confirm hypothesis"
          >
            <Check size={16} />
            Confirm
          </Button>
          <Button
            variant="destructive"
            onClick={() => submitMutation.mutate('rejected')}
            disabled={submitMutation.isPending}
            aria-label="Reject hypothesis"
          >
            <X size={16} />
            Reject
          </Button>
          <Button
            variant="outline"
            onClick={() => submitMutation.mutate('corrected')}
            disabled={submitMutation.isPending || !selectedChangeId}
            aria-label="Correct hypothesis"
          >
            <Edit3 size={16} />
            Correct
          </Button>
        </div>

        {feedback.length > 0 && (
          <div className="space-y-2 pt-4 border-t border-border">
            <h4 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
              Previous feedback
            </h4>
            <ul className="space-y-2">
              {feedback.map((entry) => (
                <li
                  key={entry.feedback_id}
                  className="rounded-lg border border-border bg-background/50 px-3 py-2 text-sm"
                >
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="secondary" className="capitalize">
                      {entry.verdict}
                    </Badge>
                    {entry.change_id && (
                      <span className="font-mono text-xs text-muted-foreground">{entry.change_id}</span>
                    )}
                    {entry.created_at && (
                      <span className="text-xs text-muted-foreground ml-auto">
                        {new Date(entry.created_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                  {entry.comment && (
                    <p className="text-muted-foreground mt-1 text-xs">{entry.comment}</p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

import { AlertCircle, RefreshCw, Inbox } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'

interface QueryWrapperProps {
  isLoading: boolean
  isError: boolean
  error?: Error | null
  onRetry?: () => void
  isEmpty?: boolean
  emptyTitle?: string
  emptyDescription?: string
  emptyAction?: { label: string; onClick: () => void }
  skeleton?: React.ReactNode
  children: React.ReactNode
}

function DefaultSkeleton() {
  return (
    <div className="space-y-4" aria-busy="true" aria-label="Loading content">
      <Skeleton className="h-8 w-1/3" />
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-32 w-full" />
    </div>
  )
}

export default function QueryWrapper({
  isLoading,
  isError,
  error,
  onRetry,
  isEmpty,
  emptyTitle = 'No data yet',
  emptyDescription = 'There is nothing to display for this view.',
  emptyAction,
  skeleton,
  children,
}: QueryWrapperProps) {
  if (isLoading) {
    return skeleton ?? <DefaultSkeleton />
  }

  if (isError) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <AlertCircle className="h-10 w-10 text-destructive mb-4" aria-hidden="true" />
          <h3 className="text-lg font-semibold text-foreground mb-2">Failed to load data</h3>
          <p className="text-sm text-muted-foreground mb-6 max-w-md">
            {error?.message ?? 'An unexpected error occurred.'}
          </p>
          {onRetry && (
            <Button variant="outline" onClick={onRetry} aria-label="Retry loading data">
              <RefreshCw size={16} />
              Retry
            </Button>
          )}
        </CardContent>
      </Card>
    )
  }

  if (isEmpty) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <Inbox className="h-10 w-10 text-muted-foreground/40 mb-4" aria-hidden="true" />
          <h3 className="text-lg font-semibold text-foreground mb-2">{emptyTitle}</h3>
          <p className="text-sm text-muted-foreground mb-6 max-w-md">{emptyDescription}</p>
          {emptyAction && (
            <Button onClick={emptyAction.onClick}>{emptyAction.label}</Button>
          )}
        </CardContent>
      </Card>
    )
  }

  return <>{children}</>
}

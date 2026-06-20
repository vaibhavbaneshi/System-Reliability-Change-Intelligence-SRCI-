import { cn } from '../utils/cn'

interface SkeletonLoaderProps {
  count?: number
  height?: string
  width?: string
  className?: string
  animated?: boolean
}

export default function SkeletonLoader({
  count = 1,
  height = 'h-4',
  width = 'w-full',
  className,
  animated = true,
}: SkeletonLoaderProps) {
  const items = Array.from({ length: count })

  return (
    <>
      {items.map((_, idx) => (
        <div
          key={idx}
          className={cn(
            'bg-muted rounded-md',
            height,
            width,
            className,
            animated && 'animate-pulse-soft'
          )}
        />
      ))}
    </>
  )
}

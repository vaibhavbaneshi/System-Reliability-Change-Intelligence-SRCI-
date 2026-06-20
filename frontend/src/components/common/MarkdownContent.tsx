import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'

interface MarkdownContentProps {
  content: string
  className?: string
}

export default function MarkdownContent({ content, className }: MarkdownContentProps) {
  return (
    <div
      className={cn(
        'prose prose-invert prose-sm max-w-none',
        'prose-headings:text-foreground prose-p:text-muted-foreground prose-strong:text-foreground',
        'prose-a:text-primary prose-code:text-foreground prose-code:bg-background prose-code:px-1 prose-code:rounded',
        'prose-pre:bg-background prose-pre:border prose-pre:border-border',
        'prose-li:text-muted-foreground prose-table:text-sm',
        className,
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  )
}

import MarkdownContent from '@/components/common/MarkdownContent'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface ExplanationPanelProps {
  explanation: string
  explanationSource: 'llm' | 'template'
}

export default function ExplanationPanel({ explanation, explanationSource }: ExplanationPanelProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
        <div>
          <CardTitle className="text-base">RCA explanation</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Narrative summary of the top-ranked change hypothesis.
          </p>
        </div>
        <Badge variant={explanationSource === 'llm' ? 'default' : 'secondary'} className="shrink-0">
          {explanationSource === 'llm' ? 'LLM generated' : 'Template'}
        </Badge>
      </CardHeader>
      <CardContent>
        {explanation ? (
          <MarkdownContent content={explanation} />
        ) : (
          <p className="text-sm text-muted-foreground">No explanation available yet.</p>
        )}
      </CardContent>
    </Card>
  )
}

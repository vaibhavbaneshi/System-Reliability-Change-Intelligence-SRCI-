import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Send, MessageSquare, Sparkles } from 'lucide-react'
import type { ChatMessage } from '@/api/types'
import { rcaApi } from '@/api/rca'
import MarkdownContent from '@/components/common/MarkdownContent'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

interface RcaChatPanelProps {
  incidentId: string
}

export default function RcaChatPanel({ incidentId }: RcaChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)

  const { data: suggestionsData, isLoading: suggestionsLoading } = useQuery({
    queryKey: ['chat-suggestions', incidentId],
    queryFn: () => rcaApi.chatSuggestions(incidentId),
  })

  const suggestions = suggestionsData?.suggestions ?? []

  const sendMessage = async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || isSending) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: trimmed }])
    setIsSending(true)

    try {
      const response = await rcaApi.chat(incidentId, trimmed)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          source: response.source,
          citations: response.citations as ChatMessage['citations'],
        },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: err instanceof Error ? err.message : 'Failed to get a response.',
        },
      ])
    } finally {
      setIsSending(false)
    }
  }

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <MessageSquare size={18} />
          RCA chat
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Ask questions about this incident&apos;s root cause analysis.
        </p>
      </CardHeader>
      <CardContent className="flex flex-col flex-1 min-h-0 gap-4">
        {suggestionsLoading ? (
          <div className="flex gap-2 flex-wrap">
            <Skeleton className="h-7 w-32" />
            <Skeleton className="h-7 w-40" />
          </div>
        ) : suggestions.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {suggestions.map((question) => (
              <button
                key={question}
                type="button"
                onClick={() => sendMessage(question)}
                disabled={isSending}
                className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1 text-xs text-muted-foreground hover:text-foreground hover:border-primary/50 transition-colors disabled:opacity-50"
              >
                <Sparkles size={12} />
                {question}
              </button>
            ))}
          </div>
        ) : null}

        <div className="flex-1 overflow-y-auto space-y-4 pr-1" role="log" aria-live="polite" aria-label="Chat messages">
          {messages.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-8">
              Start a conversation or pick a suggested question above.
            </p>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`rounded-lg px-4 py-3 text-sm ${
                msg.role === 'user'
                  ? 'bg-primary/10 border border-primary/20 ml-8'
                  : 'bg-background border border-border mr-8'
              }`}
            >
              {msg.role === 'assistant' && msg.source && (
                <Badge variant="secondary" className="mb-2 text-[10px]">
                  {msg.source}
                </Badge>
              )}
              {msg.role === 'assistant' ? (
                <MarkdownContent content={msg.content} />
              ) : (
                <p className="text-foreground">{msg.content}</p>
              )}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-border space-y-1">
                  <p className="text-xs font-semibold text-muted-foreground">Citations</p>
                  {msg.citations.map((citation, cIdx) => (
                    <pre
                      key={cIdx}
                      className="text-[10px] font-mono text-muted-foreground bg-card rounded p-2 overflow-x-auto"
                    >
                      {JSON.stringify(citation, null, 2)}
                    </pre>
                  ))}
                </div>
              )}
            </div>
          ))}
          {isSending && (
            <div className="bg-background border border-border rounded-lg px-4 py-3 mr-8 text-sm text-muted-foreground">
              Thinking…
            </div>
          )}
        </div>

        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            sendMessage(input)
          }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about hypotheses, evidence, or changes…"
            disabled={isSending}
            className="flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
            aria-label="Chat message"
          />
          <Button type="submit" disabled={isSending || !input.trim()} aria-label="Send message">
            <Send size={16} />
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

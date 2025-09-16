import { useState, useRef } from "react"
import { api } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { PromptBox } from "@/components/ui/chatgpt-prompt-input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Loader2, Link as LinkIcon, FileText } from "lucide-react"

type Message = { role: "user" | "assistant"; content: string }

type Source = { pdfId: string; originalName?: string; preview: string }

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [sources, setSources] = useState<Source[] | null>(null)
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const sendMessage = async () => {
    const content = input.trim()
    if (!content || loading) return
    const next = [...messages, { role: "user", content } as Message]
    setMessages(next)
    setInput("")
    setLoading(true)
    try {
      const res = await api.rag.chat(next)
      setMessages([...next, { role: "assistant", content: res.reply } as Message])
      setSources(res.sources || null)
    } catch (e: any) {
      setMessages([...next, { role: "assistant", content: e?.message || "Something went wrong" } as Message])
      setSources(null)
    } finally {
      setLoading(false)
      queueMicrotask(() => {
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
      })
    }
  }

  // Enter-to-submit is now handled inside PromptBox

  const downloadUrl = (id: string) => `/api/pdfs/${id}/download`

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Chat With Your Files</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col h-[70vh]">
            <ScrollArea className="flex-1 border rounded-md p-4" ref={scrollRef as any}>
              <div className="space-y-4">
                {messages.length === 0 && (
                  <div className="text-sm text-muted-foreground">
                    Ask a question about your uploaded PDFs. Answers are grounded via RAG.
                  </div>
                )}
                {messages.map((m, idx) => (
                  <div key={idx} className={m.role === "user" ? "text-right" : "text-left"}>
                    <div className={
                      "inline-block px-3 py-2 rounded-md max-w-[85%] whitespace-pre-wrap " +
                      (m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted")
                    }>
                      {m.content}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Thinking...
                  </div>
                )}
                {!!sources?.length && (
                  <div className="mt-4 border-t pt-4">
                    <div className="text-sm font-medium mb-2 flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Sources
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {sources.map((s, i) => (
                        <div key={`${s.pdfId}-${i}`} className="text-sm p-3 rounded-md border bg-background">
                          <div className="flex items-center justify-between mb-2">
                            <div className="font-medium truncate" title={s.originalName || s.pdfId}>
                              [{i + 1}] {s.originalName || s.pdfId}
                            </div>
                            <a
                              href={downloadUrl(s.pdfId)}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                            >
                              <LinkIcon className="h-3 w-3" /> Download
                            </a>
                          </div>
                          <div className="text-muted-foreground line-clamp-4">{s.preview}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            <form
              className="mt-4"
              onSubmit={(e) => {
                e.preventDefault()
                sendMessage()
              }}
            >
              <PromptBox
                value={input}
                onChange={(e) => setInput((e.target as HTMLTextAreaElement).value)}
              />
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

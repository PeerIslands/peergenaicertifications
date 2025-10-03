import React, { useMemo, useState } from 'react'

type QueryResponse = {
  result: string
  sources?: { source: string; page: number | string }[]
}

export function App() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState<string>('')
  const [sources, setSources] = useState<QueryResponse['sources']>([])
  const [loading, setLoading] = useState(false)
  const apiBase = useMemo(() => (import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'), [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setAnswer('')
    setSources([])
    try {
      const res = await fetch(`${apiBase}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text)
      }
      const data: QueryResponse = await res.json()
      setAnswer(data.result)
      setSources(data.sources ?? [])
    } catch (err: any) {
      setAnswer(`Error: ${err?.message || String(err)}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: '2rem auto', fontFamily: 'Inter, system-ui, Arial' }}>
      <h1>RAG UI</h1>
      <p>Ask questions about your PDFs via the backend API.</p>
      <form onSubmit={submit} style={{ display: 'flex', gap: 8 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="What is this document about?"
          style={{ flex: 1, padding: '0.75rem', fontSize: 16 }}
        />
        <button disabled={loading} style={{ padding: '0.75rem 1rem' }}>
          {loading ? 'Searching...' : 'Ask'}
        </button>
      </form>

      <section style={{ marginTop: 24 }}>
        <h3>Response</h3>
        <div style={{ whiteSpace: 'pre-wrap', background: '#fafafa', padding: 12, border: '1px solid #eee' }}>
          {answer || 'No response yet.'}
        </div>
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>Sources</h3>
        {sources && sources.length > 0 ? (
          <ul>
            {sources.map((s, i) => (
              <li key={i}>{s.source} (page {s.page})</li>
            ))}
          </ul>
        ) : (
          <div>No source documents found.</div>
        )}
      </section>
    </div>
  )
}

export default App


import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [files, setFiles] = useState([])
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploadLoading, setUploadLoading] = useState(false)
  const [status, setStatus] = useState({ initialized: false, documents_count: 0 })
  const [error, setError] = useState('')

  // Sample questions
  const sampleQuestions = [
    "What problem were GANs trying to solve in AI",
    "How do GANs make fake images look real?",
    "What is attention, and why did it replace older sequence models?",
    "What makes Mercury models faster than older AI models?",
  ]

  useEffect(() => {
    fetchStatus()
  }, [])

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/status`)
      setStatus(response.data)
    } catch (err) {
      console.error('Error fetching status:', err)
    }
  }

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files)
    setFiles(selectedFiles)
    setError('')
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select at least one PDF file')
      return
    }

    setUploadLoading(true)
    setError('')

    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ingest`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      alert(`Success! ${response.data.files_processed} PDF(s) ingested successfully`)
      setFiles([])
      document.getElementById('fileInput').value = ''
      fetchStatus()
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading files')
    } finally {
      setUploadLoading(false)
    }
  }

  const handleQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a question')
      return
    }

    if (!status.initialized) {
      setError('Please upload and ingest PDFs first')
      return
    }

    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])

    try {
      const response = await axios.post(`${API_BASE_URL}/api/query`, {
        query: query,
        top_k: 3,
      })
      setAnswer(response.data.answer)
      setSources(response.data.sources)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error querying documents')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async () => {
    if (!window.confirm('Are you sure you want to reset the system? This will clear all ingested documents.')) {
      return
    }

    try {
      await axios.delete(`${API_BASE_URL}/api/reset`)
      alert('System reset successfully')
      setAnswer('')
      setSources([])
      setQuery('')
      fetchStatus()
    } catch (err) {
      setError('Error resetting system')
    }
  }

  const useSampleQuestion = (question) => {
    setQuery(question)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>📚 DocRAG - PDF Query System</h1>
        <p className="subtitle">Upload PDFs and ask questions using AI-powered retrieval</p>
      </header>

      <div className="container">
        {/* Status Section */}
        <div className="status-section">
          <div className="status-card">
            <div className="status-item">
              <span className="status-label">System Status:</span>
              <span className={`status-badge ${status.initialized ? 'active' : 'inactive'}`}>
                {status.initialized ? '✓ Ready' : '○ Not Initialized'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Documents Indexed:</span>
              <span className="status-value">{status.documents_count} chunks</span>
            </div>
            {status.initialized && (
              <button onClick={handleReset} className="btn-reset">
                Reset System
              </button>
            )}
          </div>
        </div>

        {/* Upload Section */}
        <section className="section">
          <h2>1. Upload PDFs</h2>
          <div className="upload-section">
            <input
              id="fileInput"
              type="file"
              accept=".pdf"
              multiple
              onChange={handleFileChange}
              className="file-input"
            />
            <div className="upload-controls">
              {files.length > 0 && (
                <div className="file-list">
                  <p className="files-selected">Selected files: {files.map(f => f.name).join(', ')}</p>
                </div>
              )}
              <button
                onClick={handleUpload}
                disabled={uploadLoading || files.length === 0}
                className="btn btn-primary"
              >
                {uploadLoading ? '⏳ Ingesting...' : '📤 Upload & Ingest PDFs'}
              </button>
            </div>
          </div>
        </section>

        {/* Query Section */}
        <section className="section">
          <h2>2. Ask Questions</h2>
          
          {/* Sample Questions */}
          <div className="sample-questions">
            <p className="label">Sample Questions:</p>
            <div className="question-buttons">
              {sampleQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => useSampleQuestion(q)}
                  className="btn-sample"
                  disabled={!status.initialized}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <div className="query-section">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your question about the uploaded documents..."
              className="query-input"
              rows="3"
              disabled={!status.initialized}
            />
            <button
              onClick={handleQuery}
              disabled={loading || !query.trim() || !status.initialized}
              className="btn btn-secondary"
            >
              {loading ? '🔄 Searching...' : '🔍 Search Documents'}
            </button>
          </div>
        </section>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {/* Results Section */}
        {answer && (
          <section className="section results-section">
            <h2>Answer</h2>
            <div className="answer-box">
              <p className="answer-text">{answer}</p>
            </div>

            {sources.length > 0 && (
              <div className="sources">
                <h3>Sources</h3>
                <ul className="sources-list">
                  {sources.map((source, idx) => (
                    <li key={idx} className="source-item">
                      📄 {source}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </div>

      <footer className="footer">
        <p>Powered by LangChain, FAISS, and Azure OpenAI</p>
      </footer>
    </div>
  )
}

export default App


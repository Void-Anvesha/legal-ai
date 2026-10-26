import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Loader2, AlertCircle, FileText, MessageSquare } from 'lucide-react'
import { getDocument, getSummary, type DocumentInfo, type SummaryResponse } from '../services/api'
import SummaryCard from '../components/SummaryCard'

export default function Summary() {
  const { documentId } = useParams<{ documentId: string }>()
  const [document, setDocument] = useState<DocumentInfo | null>(null)
  const [summary, setSummary] = useState<SummaryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (documentId) {
      loadData()
    }
  }, [documentId])

  const loadData = async () => {
    if (!documentId) return
    setLoading(true)
    try {
      const [doc, sum] = await Promise.all([
        getDocument(documentId),
        getSummary(documentId),
      ])
      setDocument(doc)
      setSummary(sum)
    } catch (err) {
      setError('Failed to load summary. Make sure the document is fully processed.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  if (error || !summary) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-700 mb-2">Unable to Generate Summary</h2>
        <p className="text-gray-500 mb-6">{error || 'No summary available.'}</p>
        <Link to="/" className="btn-primary">Go to Dashboard</Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 font-serif">Document Summary</h1>
          <p className="text-gray-500 mt-1">
            {document?.original_filename}
          </p>
        </div>
        <Link
          to={`/chat/${documentId}`}
          className="btn-secondary flex items-center gap-2 text-sm"
        >
          <MessageSquare className="w-4 h-4" />
          Chat
        </Link>
      </div>

      {/* Document Info Bar */}
      {document?.metadata && (
        <div className="flex flex-wrap gap-3 p-4 bg-gray-50 rounded-xl border border-gray-200">
          {document.metadata.case_number && (
            <div className="flex items-center gap-1 text-sm">
              <span className="text-gray-500">Case:</span>
              <span className="font-mono text-gray-800">{document.metadata.case_number}</span>
            </div>
          )}
          {document.metadata.court_name && (
            <div className="flex items-center gap-1 text-sm">
              <span className="text-gray-500">Court:</span>
              <span className="text-gray-800">{document.metadata.court_name}</span>
            </div>
          )}
          {document.metadata.crime_category && (
            <div className="flex items-center gap-1 text-sm">
              <span className="text-gray-500">Category:</span>
              <span className="badge-red">{document.metadata.crime_category}</span>
            </div>
          )}
          {document.metadata.date_of_judgment && (
            <div className="flex items-center gap-1 text-sm">
              <span className="text-gray-500">Date:</span>
              <span className="text-gray-800">{document.metadata.date_of_judgment}</span>
            </div>
          )}
        </div>
      )}

      {/* Summary Card */}
      <SummaryCard summary={summary} />

      {/* Extracted Text */}
      {document?.extracted_text && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-4 h-4 text-gray-400" />
            <h3 className="text-sm font-semibold text-gray-700">Full Extracted Text</h3>
          </div>
          <div className="max-h-[400px] overflow-y-auto scrollbar-thin bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
              {document.extracted_text}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

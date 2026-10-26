import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Upload, FileText, MessageSquare, Search, Scale, Clock, CheckCircle2,
  AlertCircle, Loader2, ArrowRight
} from 'lucide-react'
import { listDocuments, type DocumentInfo } from '../services/api'

const statusConfig: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  uploaded: { icon: Clock, color: 'text-gray-500', label: 'Uploaded' },
  extracting_text: { icon: Loader2, color: 'text-blue-500', label: 'Extracting Text' },
  ocr_processing: { icon: Loader2, color: 'text-purple-500', label: 'OCR Processing' },
  analyzing: { icon: Loader2, color: 'text-yellow-500', label: 'Analyzing' },
  completed: { icon: CheckCircle2, color: 'text-green-500', label: 'Completed' },
  failed: { icon: AlertCircle, color: 'text-red-500', label: 'Failed' },
}

export default function Dashboard() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (err) {
      setError('Failed to load documents. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-primary-700 via-primary-800 to-legal-navy rounded-2xl p-8 text-white">
        <div className="max-w-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Scale className="w-8 h-8 text-legal-gold" />
            <h1 className="text-3xl font-bold font-serif">LegalAI</h1>
          </div>
          <p className="text-lg text-primary-100 mb-6 leading-relaxed">
            AI-powered Indian Legal Document Analysis System. Upload judgments, FIRs, 
            charge sheets, and petitions to identify applicable laws, get summaries, 
            and find similar cases.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/upload" className="btn-primary bg-white text-primary-700 hover:bg-primary-50 inline-flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload Document
            </Link>
            <Link to="/chat" className="btn-secondary bg-transparent text-white border-white/30 hover:bg-white/10 inline-flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Chat with AI
            </Link>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="font-semibold text-gray-800 mb-1">Legal Section Prediction</h3>
          <p className="text-sm text-gray-500">
            Automatically identify applicable sections from BNS, IPC, IT Act, BNSS, and BSA.
          </p>
        </div>

        <div className="card">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-3">
            <Search className="w-5 h-5 text-green-600" />
          </div>
          <h3 className="font-semibold text-gray-800 mb-1">Similar Case Retrieval</h3>
          <p className="text-sm text-gray-500">
            Find landmark judgments similar to your case using semantic search.
          </p>
        </div>

        <div className="card">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
            <MessageSquare className="w-5 h-5 text-purple-600" />
          </div>
          <h3 className="font-semibold text-gray-800 mb-1">AI Chat Assistant</h3>
          <p className="text-sm text-gray-500">
            Ask questions about your documents and get AI-powered legal explanations.
          </p>
        </div>
      </div>

      {/* Document List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-800 font-serif">Your Documents</h2>
          <Link to="/upload" className="btn-ghost text-sm flex items-center gap-1">
            <Upload className="w-4 h-4" />
            Upload New
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          </div>
        ) : error ? (
          <div className="card text-center py-8">
            <AlertCircle className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">{error}</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="card text-center py-12">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">No documents yet</h3>
            <p className="text-sm text-gray-400 mb-4">
              Upload your first legal document to get started.
            </p>
            <Link to="/upload" className="btn-primary inline-flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload Document
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => {
              const status = statusConfig[doc.status] || statusConfig.uploaded
              const StatusIcon = status.icon
              return (
                <div key={doc.id} className="card flex items-center gap-4">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-gray-500" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-gray-800 truncate">
                      {doc.original_filename}
                    </h4>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span>{formatFileSize(doc.file_size)}</span>
                      <span>{doc.file_type.toUpperCase()}</span>
                      <span>{formatDate(doc.created_at)}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className={`flex items-center gap-1 ${status.color}`}>
                      <StatusIcon className={`w-4 h-4 ${doc.status.includes('extracting') || doc.status === 'analyzing' || doc.status === 'ocr_processing' ? 'animate-spin' : ''}`} />
                      <span className="text-xs font-medium">{status.label}</span>
                    </div>

                    {doc.status === 'completed' && (
                      <div className="flex items-center gap-1">
                        <Link
                          to={`/chat/${doc.id}`}
                          className="btn-ghost text-xs py-1 px-2"
                        >
                          <MessageSquare className="w-3 h-3" />
                        </Link>
                        <Link
                          to={`/summary/${doc.id}`}
                          className="btn-ghost text-xs py-1 px-2"
                        >
                          <FileText className="w-3 h-3" />
                        </Link>
                        <Link
                          to={`/cases/${doc.id}`}
                          className="btn-ghost text-xs py-1 px-2"
                        >
                          <Search className="w-3 h-3" />
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

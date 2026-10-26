import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { FileText, Loader2, AlertCircle } from 'lucide-react'
import ChatBox from '../components/ChatBox'
import { getDocument, predictSections, type DocumentInfo, type SectionPredictionResponse } from '../services/api'
import SectionCard from '../components/SectionCard'

export default function Chat() {
  const { documentId } = useParams<{ documentId?: string }>()
  const [document, setDocument] = useState<DocumentInfo | null>(null)
  const [sections, setSections] = useState<SectionPredictionResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activePanel, setActivePanel] = useState<'chat' | 'sections' | 'text'>('chat')

  useEffect(() => {
    if (documentId) {
      loadDocument()
      loadSections()
    }
  }, [documentId])

  const loadDocument = async () => {
    if (!documentId) return
    setLoading(true)
    try {
      const doc = await getDocument(documentId)
      setDocument(doc)
    } catch (err) {
      setError('Failed to load document')
    } finally {
      setLoading(false)
    }
  }

  const loadSections = async () => {
    if (!documentId) return
    try {
      const result = await predictSections(documentId)
      setSections(result)
    } catch (err) {
      // Sections loading failed silently — not critical
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 font-serif">Legal Chat Assistant</h1>
        <p className="text-gray-500 mt-1">
          {documentId
            ? `Ask questions about your document`
            : 'Ask general questions about Indian law'}
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel — Chat */}
        <div className="lg:col-span-2">
          <ChatBox
            documentId={documentId}
            documentTitle={document?.original_filename}
          />
        </div>

        {/* Right Panel — Info */}
        <div className="space-y-4">
          {/* Document Info */}
          {document && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <FileText className="w-4 h-4 text-gray-400" />
                Document Info
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Type</span>
                  <span className="font-medium text-gray-800 capitalize">
                    {document.document_type.replace('_', ' ')}
                  </span>
                </div>
                {document.metadata?.case_number && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Case No.</span>
                    <span className="font-mono text-gray-800 text-xs">{document.metadata.case_number}</span>
                  </div>
                )}
                {document.metadata?.court_name && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Court</span>
                    <span className="text-gray-800 text-xs text-right max-w-[180px]">{document.metadata.court_name}</span>
                  </div>
                )}
                {document.metadata?.crime_category && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Category</span>
                    <span className="badge-red text-xs">{document.metadata.crime_category}</span>
                  </div>
                )}
                {document.metadata?.parties && document.metadata.parties.length > 0 && (
                  <div>
                    <span className="text-gray-500 text-xs">Parties</span>
                    <div className="mt-1 space-y-0.5">
                      {document.metadata.parties.slice(0, 5).map((party, idx) => (
                        <div key={idx} className="text-xs text-gray-700 flex items-center gap-1">
                          <span className="w-1 h-1 bg-blue-400 rounded-full" />
                          {party}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Predicted Sections */}
          {sections && sections.predicted_sections.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Predicted Sections ({sections.total_sections_found})
              </h3>
              <div className="space-y-2 max-h-[400px] overflow-y-auto scrollbar-thin">
                {sections.predicted_sections.map((section, idx) => (
                  <SectionCard key={idx} section={section} />
                ))}
              </div>
            </div>
          )}

          {/* Extracted Text */}
          {document?.extracted_text && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Extracted Text</h3>
              <div className="max-h-[300px] overflow-y-auto scrollbar-thin">
                <p className="text-xs text-gray-600 whitespace-pre-line leading-relaxed">
                  {document.extracted_text.slice(0, 2000)}
                  {document.extracted_text.length > 2000 && '...'}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

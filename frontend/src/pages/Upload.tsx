import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, MessageSquare, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import FileUploader from '../components/FileUploader'
import { type DocumentInfo, getDocument } from '../services/api'

export default function Upload() {
  const navigate = useNavigate()
  const [uploadedDoc, setUploadedDoc] = useState<DocumentInfo | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [polling, setPolling] = useState(false)

  const handleUploadSuccess = async (doc: DocumentInfo) => {
    setUploadedDoc(doc)
    setError(null)
    setPolling(true)

    // Poll for processing completion
    let attempts = 0
    const maxAttempts = 60 // 2 minutes at 2s intervals

    const poll = async () => {
      try {
        const updatedDoc = await getDocument(doc.id)
        setUploadedDoc(updatedDoc)

        if (updatedDoc.status === 'completed' || updatedDoc.status === 'failed') {
          setPolling(false)
          return
        }

        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000)
        } else {
          setPolling(false)
        }
      } catch (err) {
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000)
        } else {
          setPolling(false)
        }
      }
    }

    setTimeout(poll, 2000)
  }

  const handleUploadError = (errMsg: string) => {
    setError(errMsg)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 font-serif">Upload Document</h1>
        <p className="text-gray-500 mt-1">
          Upload a legal document for AI-powered analysis
        </p>
      </div>

      {/* Upload Area */}
      <FileUploader onUploadSuccess={handleUploadSuccess} onUploadError={handleUploadError} />

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Processing Status */}
      {uploadedDoc && (
        <div className="card space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-gray-500" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">{uploadedDoc.original_filename}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-gray-500">
                  {(uploadedDoc.file_size / 1024).toFixed(1)} KB • {uploadedDoc.file_type.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          {/* Status */}
          <div className="flex items-center gap-2">
            {uploadedDoc.status === 'completed' ? (
              <>
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span className="text-sm font-medium text-green-700">Processing Complete</span>
              </>
            ) : uploadedDoc.status === 'failed' ? (
              <>
                <AlertCircle className="w-5 h-5 text-red-500" />
                <span className="text-sm font-medium text-red-700">Processing Failed</span>
              </>
            ) : (
              <>
                <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
                <span className="text-sm font-medium text-primary-700">
                  {uploadedDoc.status === 'extracting_text'
                    ? 'Extracting text...'
                    : uploadedDoc.status === 'ocr_processing'
                    ? 'Running OCR on scanned pages...'
                    : uploadedDoc.status === 'analyzing'
                    ? 'Analyzing legal content...'
                    : 'Processing...'}
                </span>
              </>
            )}
          </div>

          {/* Extracted Text Preview */}
          {uploadedDoc.extracted_text && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Extracted Text Preview</h4>
              <div className="bg-gray-50 rounded-lg p-4 max-h-48 overflow-y-auto scrollbar-thin">
                <p className="text-sm text-gray-700 whitespace-pre-line">
                  {uploadedDoc.extracted_text.slice(0, 1000)}
                  {uploadedDoc.extracted_text.length > 1000 && '...'}
                </p>
              </div>
            </div>
          )}

          {/* Entities */}
          {uploadedDoc.entities && uploadedDoc.entities.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Detected Entities</h4>
              <div className="flex flex-wrap gap-1.5">
                {uploadedDoc.entities.slice(0, 15).map((entity, idx) => (
                  <span
                    key={idx}
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                      ${entity.entity_type === 'party' ? 'bg-blue-100 text-blue-800' :
                        entity.entity_type === 'crime' ? 'bg-red-100 text-red-800' :
                        entity.entity_type === 'date' ? 'bg-purple-100 text-purple-800' :
                        entity.entity_type === 'court' ? 'bg-green-100 text-green-800' :
                        entity.entity_type === 'location' ? 'bg-yellow-100 text-yellow-800' :
                        entity.entity_type === 'evidence' ? 'bg-orange-100 text-orange-800' :
                        'bg-gray-100 text-gray-800'}`}
                  >
                    <span className="font-mono text-[10px] mr-1 opacity-70">{entity.entity_type}:</span>
                    {entity.value}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          {uploadedDoc.status === 'completed' && (
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => navigate(`/chat/${uploadedDoc.id}`)}
                className="btn-primary flex items-center gap-2"
              >
                <MessageSquare className="w-4 h-4" />
                Chat with Document
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

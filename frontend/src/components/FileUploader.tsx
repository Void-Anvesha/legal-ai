import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react'
import { uploadDocument, type DocumentInfo } from '../services/api'

interface FileUploaderProps {
  onUploadSuccess: (doc: DocumentInfo) => void
  onUploadError: (error: string) => void
}

export default function FileUploader({ onUploadSuccess, onUploadError }: FileUploaderProps) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState<string>('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploading(true)
    setProgress(`Uploading ${file.name}...`)

    try {
      const doc = await uploadDocument(file)
      setProgress('Document uploaded! Processing started...')
      onUploadSuccess(doc)
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Upload failed. Please try again.'
      onUploadError(message)
    } finally {
      setUploading(false)
      setTimeout(() => setProgress(''), 3000)
    }
  }, [onUploadSuccess, onUploadError])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tiff'],
      'image/bmp': ['.bmp'],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
    disabled: uploading,
  })

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200
          ${isDragActive ? 'border-primary-400 bg-primary-50' : 'border-gray-300 hover:border-primary-300 hover:bg-gray-50'}
          ${isDragReject ? 'border-red-400 bg-red-50' : ''}
          ${uploading ? 'opacity-60 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          {uploading ? (
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
          ) : isDragActive ? (
            <Upload className="w-12 h-12 text-primary-500" />
          ) : (
            <FileText className="w-12 h-12 text-gray-400" />
          )}

          {uploading ? (
            <div>
              <p className="text-lg font-medium text-primary-700">{progress}</p>
              <p className="text-sm text-gray-500 mt-1">Please wait...</p>
            </div>
          ) : isDragActive ? (
            <div>
              <p className="text-lg font-medium text-primary-700">Drop your document here</p>
              <p className="text-sm text-gray-500">Release to upload</p>
            </div>
          ) : (
            <div>
              <p className="text-lg font-medium text-gray-700">
                Drag & drop your legal document here
              </p>
              <p className="text-sm text-gray-500 mt-1">
                or <span className="text-primary-600 font-medium">click to browse</span>
              </p>
            </div>
          )}

          <div className="flex flex-wrap justify-center gap-2 mt-2">
            {['PDF', 'DOCX', 'TXT', 'PNG', 'JPG'].map((type) => (
              <span key={type} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                {type}
              </span>
            ))}
          </div>

          <p className="text-xs text-gray-400">Maximum file size: 50MB</p>
        </div>

        {isDragReject && (
          <div className="absolute inset-0 flex items-center justify-center bg-red-50/80 rounded-xl">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Unsupported file type</span>
            </div>
          </div>
        )}
      </div>

      {progress && !uploading && (
        <div className="mt-3 flex items-center gap-2 text-green-600 text-sm">
          <CheckCircle2 className="w-4 h-4" />
          <span>{progress}</span>
        </div>
      )}
    </div>
  )
}

/** Custom hook for document operations */
import { useState, useEffect, useCallback } from 'react'
import * as api from '../services/api'

export function useDocument(documentId: string | undefined) {
  const [document, setDocument] = useState<api.DocumentInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!documentId) return
    setLoading(true)
    try {
      const doc = await api.getDocument(documentId)
      setDocument(doc)
    } catch (err: any) {
      setError(err?.message || 'Failed to load document')
    } finally {
      setLoading(false)
    }
  }, [documentId])

  useEffect(() => {
    load()
  }, [load])

  return { document, loading, error, reload: load }
}

export function useDocuments() {
  const [documents, setDocuments] = useState<api.DocumentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const docs = await api.listDocuments()
      setDocuments(docs)
    } catch (err: any) {
      setError(err?.message || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const remove = async (documentId: string) => {
    try {
      await api.deleteDocument(documentId)
      setDocuments((prev) => prev.filter((d) => d.id !== documentId))
    } catch (err) {
      console.error('Failed to delete document:', err)
    }
  }

  return { documents, loading, error, reload: load, remove }
}

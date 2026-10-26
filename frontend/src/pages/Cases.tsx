import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Search, Loader2, AlertCircle } from 'lucide-react'
import { findSimilarCases, findSimilarCasesForDocument, type SimilarCaseResponse } from '../services/api'
import CaseCard from '../components/CaseCard'

export default function Cases() {
  const { documentId } = useParams<{ documentId?: string }>()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SimilarCaseResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (documentId) {
      searchForDocument()
    }
  }, [documentId])

  const searchForDocument = async () => {
    if (!documentId) return
    setLoading(true)
    try {
      const result = await findSimilarCasesForDocument(documentId, 5)
      setResults(result)
    } catch (err) {
      setError('Failed to find similar cases')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const result = await findSimilarCases(query, 5)
      setResults(result)
    } catch (err) {
      setError('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 font-serif">Similar Case Retrieval</h1>
        <p className="text-gray-500 mt-1">
          Find landmark judgments similar to your case or query
        </p>
      </div>

      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe a legal case or enter keywords (e.g., 'murder conviction death penalty', 'cyber fraud phishing')..."
            className="input-field pl-10"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="btn-primary"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
        </button>
      </div>

      {/* Document-linked search info */}
      {documentId && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          Showing cases similar to your uploaded document.
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Results */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <span className="ml-3 text-gray-500">Searching legal database...</span>
        </div>
      )}

      {results && !loading && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800">
              Search Results
            </h2>
            <span className="text-sm text-gray-500">
              {results.total_results} case{results.total_results !== 1 ? 's' : ''} found
            </span>
          </div>

          {results.similar_cases.length === 0 ? (
            <div className="card text-center py-8">
              <Search className="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No similar cases found. Try a different query.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {results.similar_cases.map((caseData, idx) => (
                <CaseCard key={caseData.id} caseData={caseData} rank={idx + 1} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Initial State */}
      {!results && !loading && !documentId && (
        <div className="card text-center py-12">
          <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-600 mb-2">Find Similar Cases</h3>
          <p className="text-sm text-gray-400 max-w-md mx-auto">
            Enter a legal query describing facts, charges, or legal issues to find 
            landmark judgments from the Supreme Court and High Courts of India.
          </p>
        </div>
      )}
    </div>
  )
}

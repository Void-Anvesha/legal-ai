import { Landmark, Calendar, Building2, Scale, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import type { SimilarCase } from '../services/api'

interface CaseCardProps {
  caseData: SimilarCase
  rank?: number
}

export default function CaseCard({ caseData, rank }: CaseCardProps) {
  const [expanded, setExpanded] = useState(false)

  const outcomeColors: Record<string, string> = {
    convicted: 'bg-red-100 text-red-800',
    acquitted: 'bg-green-100 text-green-800',
    dismissed: 'bg-gray-100 text-gray-800',
    settled: 'bg-blue-100 text-blue-800',
    pending: 'bg-yellow-100 text-yellow-800',
    bail_granted: 'bg-emerald-100 text-emerald-800',
    bail_denied: 'bg-orange-100 text-orange-800',
    appeal_allowed: 'bg-teal-100 text-teal-800',
    appeal_dismissed: 'bg-rose-100 text-rose-800',
  }

  const outcomeColor = outcomeColors[caseData.outcome] || 'bg-gray-100 text-gray-800'

  return (
    <div className="card hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            {rank && (
              <span className="w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-bold">
                {rank}
              </span>
            )}
            <Landmark className="w-4 h-4 text-legal-gold flex-shrink-0" />
            <h4 className="text-sm font-semibold text-gray-800 line-clamp-2">
              {caseData.case_title}
            </h4>
          </div>

          <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <Building2 className="w-3 h-3" />
              <span>{caseData.court}</span>
            </div>
            {caseData.date && (
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                <span>{caseData.date}</span>
              </div>
            )}
            {caseData.case_number && (
              <span className="font-mono">{caseData.case_number}</span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="text-right">
            <div className={`px-2 py-0.5 rounded-full text-xs font-semibold capitalize ${outcomeColor}`}>
              {caseData.outcome.replace('_', ' ')}
            </div>
            <div className="text-xs text-primary-600 font-mono mt-1">
              {Math.round(caseData.similarity_score * 100)}% match
            </div>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            {expanded ? (
              <ChevronUp className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Sections */}
      {caseData.acts_sections.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {caseData.acts_sections.map((s) => (
            <span key={s} className="badge-blue text-[10px]">{s}</span>
          ))}
        </div>
      )}

      {/* Expanded content */}
      {expanded && (
        <div className="mt-3 space-y-3 pt-3 border-t border-gray-200">
          <div>
            <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Brief Facts</h5>
            <p className="text-sm text-gray-700 leading-relaxed">{caseData.brief_facts}</p>
          </div>

          {caseData.key_holdings.length > 0 && (
            <div>
              <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Key Holdings</h5>
              <ul className="space-y-1">
                {caseData.key_holdings.map((holding, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                    <Scale className="w-3 h-3 text-legal-gold flex-shrink-0 mt-1" />
                    <span>{holding}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

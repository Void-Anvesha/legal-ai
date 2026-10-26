import { Scale, AlertTriangle, Shield, Lock, Unlock, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import type { PredictedSection } from '../services/api'

interface SectionCardProps {
  section: PredictedSection
  onExplain?: (act: string, sectionNumber: string) => void
}

export default function SectionCard({ section, onExplain }: SectionCardProps) {
  const [expanded, setExpanded] = useState(false)

  const confidenceColor = section.confidence >= 0.8
    ? 'text-green-600 bg-green-50'
    : section.confidence >= 0.6
    ? 'text-yellow-600 bg-yellow-50'
    : 'text-gray-600 bg-gray-50'

  const actColor = (() => {
    const act = section.section.act
    if (act.includes('BNS') || act.includes('IPC')) return 'border-l-red-500'
    if (act.includes('IT')) return 'border-l-blue-500'
    if (act.includes('BNSS') || act.includes('CrPC')) return 'border-l-green-500'
    if (act.includes('BSA') || act.includes('Evidence')) return 'border-l-purple-500'
    return 'border-l-gray-500'
  })()

  const punishment = section.section.punishment

  return (
    <div className={`legal-section-card ${actColor}`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <Scale className="w-4 h-4 text-legal-gold flex-shrink-0" />
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              {section.section.act}
            </span>
            <span className="text-xs text-gray-400">•</span>
            <span className="text-xs font-mono font-bold text-gray-700">
              Section {section.section.section_number}
            </span>
          </div>
          <h4 className="text-sm font-semibold text-gray-800 leading-snug">
            {section.section.section_title}
          </h4>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${confidenceColor}`}>
            {Math.round(section.confidence * 100)}%
          </span>
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

      {/* Expanded content */}
      {expanded && (
        <div className="mt-4 space-y-3">
          {/* Description */}
          <div>
            <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Description</h5>
            <p className="text-sm text-gray-700 leading-relaxed">
              {section.section.description}
            </p>
          </div>

          {/* Reason */}
          <div>
            <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Why This Applies</h5>
            <p className="text-sm text-gray-600 leading-relaxed">
              {section.reason}
            </p>
          </div>

          {/* Relevant Text */}
          {section.relevant_text && (
            <div>
              <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Relevant Text</h5>
              <blockquote className="text-sm text-gray-600 italic border-l-2 border-gray-300 pl-3">
                "{section.relevant_text}"
              </blockquote>
            </div>
          )}

          {/* Punishment */}
          {punishment && punishment.punishment_type !== 'none' && (
            <div>
              <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Punishment</h5>
              <div className="bg-red-50 border border-red-100 rounded-lg p-3 space-y-1">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
                  <span className="text-sm font-medium text-red-800 capitalize">
                    {punishment.punishment_type.replace('_', ' ')}
                  </span>
                </div>
                {punishment.minimum_duration && (
                  <p className="text-xs text-red-700 pl-6">
                    Minimum: {punishment.minimum_duration}
                  </p>
                )}
                {punishment.maximum_duration && (
                  <p className="text-xs text-red-700 pl-6">
                    Maximum: {punishment.maximum_duration}
                  </p>
                )}
                {punishment.fine_amount && (
                  <p className="text-xs text-red-700 pl-6">
                    Fine: {punishment.fine_amount}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Offence Type */}
          {punishment && (
            <div className="flex flex-wrap gap-2">
              {punishment.is_cognizable !== null && (
                <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                  punishment.is_cognizable ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-700'
                }`}>
                  <Shield className="w-3 h-3" />
                  {punishment.is_cognizable ? 'Cognizable' : 'Non-Cognizable'}
                </div>
              )}
              {punishment.is_bailable !== null && (
                <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                  punishment.is_bailable ? 'bg-green-50 text-green-700' : 'bg-orange-50 text-orange-700'
                }`}>
                  {punishment.is_bailable ? (
                    <Unlock className="w-3 h-3" />
                  ) : (
                    <Lock className="w-3 h-3" />
                  )}
                  {punishment.is_bailable ? 'Bailable' : 'Non-Bailable'}
                </div>
              )}
            </div>
          )}

          {/* Explain button */}
          {onExplain && (
            <button
              onClick={() => onExplain(section.section.act, section.section.section_number)}
              className="text-sm text-primary-600 hover:text-primary-800 font-medium"
            >
              Read simple explanation →
            </button>
          )}
        </div>
      )}
    </div>
  )
}

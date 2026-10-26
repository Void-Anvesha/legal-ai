import { FileText, Gavel, BookOpen, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import type { SummaryResponse } from '../services/api'

interface SummaryCardProps {
  summary: SummaryResponse
}

export default function SummaryCard({ summary }: SummaryCardProps) {
  const [activeTab, setActiveTab] = useState<'short' | 'detailed' | 'findings'>('short')

  const tabs = [
    { id: 'short' as const, label: 'Short Summary', icon: FileText },
    { id: 'detailed' as const, label: 'Detailed Summary', icon: BookOpen },
    { id: 'findings' as const, label: 'Key Findings', icon: Lightbulb },
  ]

  return (
    <div className="card-elevated">
      {/* Tabs */}
      <div className="flex items-center gap-1 mb-4 border-b border-gray-200 pb-3">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${activeTab === tab.id
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
                }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'short' && (
          <div>
            <p className="text-sm text-gray-700 leading-relaxed">
              {summary.short_summary}
            </p>
          </div>
        )}

        {activeTab === 'detailed' && (
          <div>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
              {summary.detailed_summary}
            </p>
          </div>
        )}

        {activeTab === 'findings' && (
          <div className="space-y-3">
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Key Findings</h4>
              <ul className="space-y-1.5">
                {summary.key_findings.map((finding, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="w-5 h-5 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span>{finding}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="section-divider" />

            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Legal Principles</h4>
              <ul className="space-y-1.5">
                {summary.legal_principles.map((principle, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                    <BookOpen className="w-4 h-4 text-legal-gold flex-shrink-0 mt-0.5" />
                    <span>{principle}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Final Verdict */}
        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <Gavel className="w-4 h-4 text-amber-700" />
            <h4 className="text-xs font-semibold text-amber-800 uppercase">Final Verdict</h4>
          </div>
          <p className="text-sm text-amber-900 font-medium">{summary.final_verdict}</p>
        </div>
      </div>
    </div>
  )
}

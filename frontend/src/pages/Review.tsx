import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  AlertCircle, CheckCircle2, ClipboardCheck, Edit3, FileText, Loader2,
  RotateCcw, ShieldAlert, XCircle
} from 'lucide-react'
import {
  getHitlAudit,
  getIntakeCase,
  listIntakeCases,
  recordHitlDecision,
  type CaseFile,
  type HitlDecision,
} from '../services/api'

const statusColor: Record<string, string> = {
  draft: 'badge-yellow',
  officer_review: 'badge-blue',
  approved: 'badge-green',
  rejected: 'badge-red',
  needs_more_info: 'badge-yellow',
  escalated: 'badge-red',
}

export default function Review() {
  const { caseId } = useParams()
  const [cases, setCases] = useState<CaseFile[]>([])
  const [caseFile, setCaseFile] = useState<CaseFile | null>(null)
  const [audit, setAudit] = useState<HitlDecision[]>([])
  const [editedStatement, setEditedStatement] = useState('')
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    load()
  }, [caseId])

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      if (caseId) {
        const selected = await getIntakeCase(caseId)
        setCaseFile(selected)
        setEditedStatement(selected.statement_draft)
        setAudit(await getHitlAudit(caseId))
      } else {
        const response = await listIntakeCases()
        setCases(response)
      }
    } catch {
      setError('Could not load review data.')
    } finally {
      setLoading(false)
    }
  }

  const decide = async (
    decisionType: 'approve' | 'edit' | 'reject' | 'request_more_info' | 'escalate',
    target: 'statement' | 'extracted_fact' | 'legal_section' | 'full_case' = 'full_case',
    originalValue?: string
  ) => {
    if (!caseFile) return
    setSaving(true)
    setError(null)
    try {
      const response = await recordHitlDecision(
        caseFile.case_id,
        decisionType,
        target,
        note || undefined,
        decisionType === 'edit' ? editedStatement : undefined,
        originalValue || (decisionType === 'edit' ? caseFile.statement_draft : undefined)
      )
      setCaseFile(response.case_file)
      setEditedStatement(response.case_file.statement_draft)
      setAudit(await getHitlAudit(caseFile.case_id))
      setNote('')
    } catch {
      setError('Could not save officer decision.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (!caseId) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Officer Review</h1>
          <p className="text-sm text-gray-500">Review case packets generated from victim intake sessions.</p>
        </div>
        {error && <ErrorBox message={error} />}
        {cases.length === 0 ? (
          <div className="card py-12 text-center">
            <ClipboardCheck className="mx-auto mb-3 h-10 w-10 text-gray-300" />
            <p className="text-gray-500">No intake cases are ready yet.</p>
            <Link to="/intake" className="btn-primary mt-4 inline-flex">Start Intake</Link>
          </div>
        ) : (
          <div className="space-y-3">
            {cases.map((item) => (
              <Link key={item.case_id} to={`/review/${item.case_id}`} className="card block">
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="font-semibold text-gray-900">{item.summary || 'Draft complaint'}</h2>
                      <span className={statusColor[item.status] || 'badge-blue'}>{formatLabel(item.status)}</span>
                    </div>
                    <p className="mt-1 text-sm text-gray-500">
                      {formatLabel(item.facts.type) || 'Unclassified'} at {item.facts.location || 'unknown location'}
                    </p>
                  </div>
                  <span className="text-sm font-medium text-primary-700">Open review</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    )
  }

  if (!caseFile) {
    return <ErrorBox message="Case not found." />
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">HITL Officer Review</h1>
          <p className="text-sm text-gray-500">Case {caseFile.case_id}</p>
        </div>
        <span className={statusColor[caseFile.status] || 'badge-blue'}>{formatLabel(caseFile.status)}</span>
      </div>

      {error && <ErrorBox message={error} />}

      {caseFile.status === 'escalated' && (
        <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <ShieldAlert className="mt-0.5 h-5 w-5" />
          <div>
            <p className="font-semibold">Escalated case</p>
            <p className="text-sm">Review immediately before continuing normal processing.</p>
          </div>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <div className="space-y-4">
          <div className="card">
            <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-gray-900">
              <FileText className="h-5 w-5 text-primary-600" />
              Complaint Statement
            </h2>
            <textarea
              className="input-field min-h-72 resize-y"
              value={editedStatement}
              onChange={(event) => setEditedStatement(event.target.value)}
            />
            <div className="mt-3 flex flex-wrap gap-2">
              <button className="btn-secondary inline-flex items-center gap-2" onClick={() => decide('edit', 'statement')} disabled={saving}>
                <Edit3 className="h-4 w-4" />
                Save Edits
              </button>
              <button className="btn-primary inline-flex items-center gap-2" onClick={() => decide('approve')} disabled={saving}>
                <CheckCircle2 className="h-4 w-4" />
                Approve
              </button>
              <button className="btn-secondary inline-flex items-center gap-2" onClick={() => decide('request_more_info')} disabled={saving}>
                <RotateCcw className="h-4 w-4" />
                More Info
              </button>
              <button className="btn-secondary inline-flex items-center gap-2 text-red-700" onClick={() => decide('reject')} disabled={saving}>
                <XCircle className="h-4 w-4" />
                Reject
              </button>
            </div>
          </div>

          <div className="card">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Officer Note</h2>
            <input
              className="input-field"
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Reason or review note..."
            />
          </div>
        </div>

        <aside className="space-y-4">
          <div className="card">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Extracted Facts</h2>
            <dl className="space-y-3 text-sm">
              <Fact label="Type" value={formatLabel(caseFile.facts.type)} />
              <Fact label="Victim" value={caseFile.victim.name} />
              <Fact label="Contact" value={caseFile.victim.contact} />
              <Fact label="Date" value={caseFile.facts.date} />
              <Fact label="Time" value={caseFile.facts.time} />
              <Fact label="Location" value={caseFile.facts.location} />
              <Fact label="Accused" value={caseFile.facts.accused.join(', ')} />
              <Fact label="Evidence" value={caseFile.facts.evidence.join(', ')} />
            </dl>
          </div>

          <div className="card">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Recommended Sections</h2>
            {caseFile.legal_recommendations.length === 0 ? (
              <p className="text-sm text-gray-500">No sections recommended yet.</p>
            ) : (
              <div className="space-y-3">
                {caseFile.legal_recommendations.map((item) => (
                  <div key={`${item.section.act}-${item.section.section_number}`} className="rounded-lg border border-gray-200 p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold text-gray-900">
                          Section {item.section.section_number}
                        </p>
                        <p className="text-xs text-gray-500">{item.section.act}</p>
                      </div>
                      <span className="badge-blue">{Math.round(item.confidence * 100)}%</span>
                    </div>
                    <p className="mt-2 text-sm text-gray-700">{item.section.section_title}</p>
                    <p className="mt-2 text-xs text-gray-500">{item.reason}</p>
                    {caseFile.legal_recommendation_notes
                      .filter((note) => note.law === item.section.act && note.section === item.section.section_number)
                      .map((note) => (
                        <div key={`${note.law}-${note.section}-notes`} className="mt-3 space-y-3 border-t border-gray-100 pt-3">
                          <p className="text-xs text-gray-600">{note.explanation}</p>
                          <FactList title="Supporting facts" items={note.supporting_facts} empty="No supporting facts captured." />
                          <FactList title="Needs confirmation" items={note.missing_facts} empty="No missing facts flagged." />
                          <div className="flex flex-wrap gap-2">
                            <button
                              className="btn-secondary px-3 py-1.5 text-xs"
                              onClick={() => decide('approve', 'legal_section', `${note.law} ${note.section}`)}
                              disabled={saving}
                            >
                              Accept Section
                            </button>
                            <button
                              className="btn-secondary px-3 py-1.5 text-xs text-red-700"
                              onClick={() => decide('reject', 'legal_section', `${note.law} ${note.section}`)}
                              disabled={saving}
                            >
                              Reject Section
                            </button>
                          </div>
                        </div>
                      ))}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Audit Trail</h2>
            {audit.length === 0 ? (
              <p className="text-sm text-gray-500">No officer decisions yet.</p>
            ) : (
              <div className="space-y-2">
                {audit.map((item) => (
                  <div key={item.decision_id} className="rounded-lg bg-gray-50 p-3 text-sm">
                    <p className="font-semibold text-gray-800">{formatLabel(item.decision_type)}</p>
                    <p className="text-xs text-gray-500">{item.reason || 'No reason provided'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}

function Fact({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</dt>
      <dd className="mt-1 text-gray-800">{value || 'Not captured'}</dd>
    </div>
  )
}

function ErrorBox({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      <AlertCircle className="h-4 w-4" />
      {message}
    </div>
  )
}

function FactList({ title, items, empty }: { title: string; items: string[]; empty: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">{title}</p>
      {items.length ? (
        <ul className="mt-1 space-y-1 text-xs text-gray-700">
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-1 text-xs text-gray-400">{empty}</p>
      )}
    </div>
  )
}

function formatLabel(value?: string | null) {
  return value ? value.split('_').join(' ') : value
}

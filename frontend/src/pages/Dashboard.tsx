import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Upload, FileText, MessageSquare, Search, Clock, CheckCircle2,
  AlertCircle, Loader2, Mic, UserCheck, ShieldCheck, ClipboardList,
  Radio, ArrowRight, Activity, Database
} from 'lucide-react'
import { listDocuments, listIntakeCases, type CaseFile, type DocumentInfo } from '../services/api'

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
  const [cases, setCases] = useState<CaseFile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    setError(null)

    const [documentsResult, casesResult] = await Promise.allSettled([
      listDocuments(),
      listIntakeCases(),
    ])

    if (documentsResult.status === 'fulfilled') {
      setDocuments(documentsResult.value)
    }

    if (casesResult.status === 'fulfilled') {
      setCases(casesResult.value)
    }

    const failedQueues = [
      documentsResult.status === 'rejected' ? 'documents' : null,
      casesResult.status === 'rejected' ? 'officer review cases' : null,
    ].filter(Boolean)

    if (failedQueues.length) {
      setError(`Could not refresh ${failedQueues.join(' and ')}. Other dashboard data is still available.`)
    }

    setLoading(false)
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

  const reviewCount = cases.filter((item) => item.status === 'officer_review' || item.status === 'escalated').length
  const completedDocuments = documents.filter((doc) => doc.status === 'completed').length

  return (
    <div className="min-h-[calc(100vh-7rem)] space-y-6">
      <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <div className="rounded-lg bg-gradient-to-br from-primary-700 via-primary-800 to-legal-navy p-8 text-white shadow-sm">
          <div className="flex h-full min-h-72 flex-col justify-between gap-8">
            <div className="max-w-4xl">
              <div className="mb-5 inline-flex items-center gap-2 rounded-lg bg-white/10 px-3 py-1.5 text-sm text-primary-50">
                <Radio className="h-4 w-4" />
                Multi-agent police intake console
              </div>
              <h1 className="font-serif text-4xl font-bold leading-tight lg:text-5xl">BolnaAI</h1>
              <p className="mt-4 max-w-3xl text-base leading-7 text-primary-50 lg:text-lg">
                Capture victim complaints, extract structured facts, draft police statements, recommend legal sections, and route every case through officer review.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link to="/intake" className="btn-primary inline-flex items-center gap-2 bg-white text-primary-700 hover:bg-primary-50">
                <Mic className="h-4 w-4" />
                Start Intake
              </Link>
              <Link to="/review" className="btn-secondary inline-flex items-center gap-2 border-white/30 bg-transparent text-white hover:bg-white/10">
                <UserCheck className="h-4 w-4" />
                Officer Review
              </Link>
              <Link to="/upload" className="btn-primary inline-flex items-center gap-2 bg-white text-primary-700 hover:bg-primary-50">
                <Upload className="h-4 w-4" />
                Upload Document
              </Link>
            </div>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
          <MetricCard icon={ClipboardList} label="Generated Cases" value={cases.length} detail={`${reviewCount} awaiting review`} tone="blue" />
          <MetricCard icon={FileText} label="Documents" value={documents.length} detail={`${completedDocuments} ready for analysis`} tone="green" />
          <MetricCard icon={ShieldCheck} label="HITL Gate" value="Active" detail="Officer approval required" tone="purple" />
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-4">
        <WorkflowStep icon={Mic} title="Intake" text="Voice or text complaint capture with consent." />
        <WorkflowStep icon={Activity} title="Agents" text="Safety, follow-up, facts, and draft generation." />
        <WorkflowStep icon={Database} title="Legal Match" text="Section prediction with supporting facts." />
        <WorkflowStep icon={UserCheck} title="Review" text="Officer edits, approval, rejection, or escalation." />
      </section>

      {error && (
        <div className="flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-serif text-xl font-bold text-gray-900">Document Analysis Queue</h2>
            <Link to="/upload" className="btn-ghost flex items-center gap-1 text-sm">
              <Upload className="h-4 w-4" />
              Upload New
            </Link>
          </div>

          {loading ? (
            <LoadingBlock />
          ) : documents.length === 0 ? (
            <EmptyBlock icon={FileText} title="No documents yet" text="Upload a legal document to analyze laws, summaries, and similar cases." actionPath="/upload" actionText="Upload Document" />
          ) : (
            <div className="grid gap-3 2xl:grid-cols-2">
              {documents.map((doc) => {
                const status = statusConfig[doc.status] || statusConfig.uploaded
                const StatusIcon = status.icon
                return (
                  <div key={doc.id} className="card flex items-center gap-4">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gray-100">
                      <FileText className="h-5 w-5 text-gray-500" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <h4 className="truncate text-sm font-semibold text-gray-800">{doc.original_filename}</h4>
                      <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                        <span>{formatFileSize(doc.file_size)}</span>
                        <span>{doc.file_type.toUpperCase()}</span>
                        <span>{formatDate(doc.created_at)}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <div className={`flex items-center gap-1 ${status.color}`}>
                        <StatusIcon className={`h-4 w-4 ${doc.status.includes('extracting') || doc.status === 'analyzing' || doc.status === 'ocr_processing' ? 'animate-spin' : ''}`} />
                        <span className="text-xs font-medium">{status.label}</span>
                      </div>

                      {doc.status === 'completed' && (
                        <div className="flex items-center gap-1">
                          <IconLink to={`/chat/${doc.id}`} icon={MessageSquare} />
                          <IconLink to={`/summary/${doc.id}`} icon={FileText} />
                          <IconLink to={`/cases/${doc.id}`} icon={Search} />
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-serif text-xl font-bold text-gray-900">Officer Review Queue</h2>
            <Link to="/review" className="btn-ghost flex items-center gap-1 text-sm">
              Open Review
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {loading ? (
            <LoadingBlock />
          ) : cases.length === 0 ? (
            <EmptyBlock icon={UserCheck} title="No intake cases yet" text="Start a complaint intake to generate a reviewable case packet." actionPath="/intake" actionText="Start Intake" />
          ) : (
            <div className="space-y-3">
              {cases.slice(0, 6).map((item) => (
                <Link key={item.case_id} to={`/review/${item.case_id}`} className="card block">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-gray-900">{item.summary || 'Draft complaint'}</p>
                      <p className="mt-1 text-sm text-gray-500">
                        {formatLabel(item.facts.type) || 'Unclassified'} at {item.facts.location || 'unknown location'}
                      </p>
                    </div>
                    <span className={statusBadge(item.status)}>{formatLabel(item.status)}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

function MetricCard({ icon: Icon, label, value, detail, tone }: {
  icon: typeof CheckCircle2
  label: string
  value: string | number
  detail: string
  tone: 'blue' | 'green' | 'purple'
}) {
  const colors = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-green-50 text-green-700',
    purple: 'bg-purple-50 text-purple-700',
  }

  return (
    <div className="card min-h-0">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`flex h-11 w-11 items-center justify-center rounded-lg ${colors[tone]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <p className="mt-4 text-sm text-gray-500">{detail}</p>
    </div>
  )
}

function WorkflowStep({ icon: Icon, title, text }: { icon: typeof CheckCircle2; title: string; text: string }) {
  return (
    <div className="card">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50 text-primary-700">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-gray-500">{text}</p>
    </div>
  )
}

function LoadingBlock() {
  return (
    <div className="flex min-h-48 items-center justify-center rounded-lg border border-gray-200 bg-white">
      <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
    </div>
  )
}

function EmptyBlock({ icon: Icon, title, text, actionPath, actionText }: {
  icon: typeof CheckCircle2
  title: string
  text: string
  actionPath: string
  actionText: string
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white px-6 py-12 text-center">
      <Icon className="mx-auto mb-4 h-12 w-12 text-gray-300" />
      <h3 className="text-lg font-medium text-gray-700">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm text-gray-500">{text}</p>
      <Link to={actionPath} className="btn-primary mt-5 inline-flex items-center gap-2">
        {actionText}
      </Link>
    </div>
  )
}

function IconLink({ to, icon: Icon }: { to: string; icon: typeof CheckCircle2 }) {
  return (
    <Link to={to} className="btn-ghost px-2 py-1 text-xs">
      <Icon className="h-3.5 w-3.5" />
    </Link>
  )
}

function statusBadge(status: string) {
  const map: Record<string, string> = {
    draft: 'badge-yellow',
    officer_review: 'badge-blue',
    approved: 'badge-green',
    rejected: 'badge-red',
    needs_more_info: 'badge-yellow',
    escalated: 'badge-red',
  }
  return map[status] || 'badge-blue'
}

function formatLabel(value?: string | null) {
  return value ? value.split('_').join(' ') : value
}

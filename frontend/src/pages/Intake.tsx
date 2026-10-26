import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertTriangle, CheckCircle2, FileText, Loader2, Mic, MicOff, Send,
  ShieldAlert, Upload, UserCheck
} from 'lucide-react'
import {
  completeIntakeSession,
  createIntakeSession,
  sendIntakeMessage,
  uploadIntakeAudio,
  type CaseFile,
  type ConversationMessage,
  type IntakeSession,
} from '../services/api'

type SpeechRecognitionCtor = new () => {
  lang: string
  interimResults: boolean
  continuous: boolean
  start: () => void
  stop: () => void
  onresult: ((event: { results: ArrayLike<{ 0: { transcript: string } }> }) => void) | null
  onend: (() => void) | null
}

export default function Intake() {
  const [language, setLanguage] = useState('en-IN')
  const [session, setSession] = useState<IntakeSession | null>(null)
  const [caseFile, setCaseFile] = useState<CaseFile | null>(null)
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [recording, setRecording] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canComplete = useMemo(() => {
    if (!caseFile) return false
    return caseFile.facts.description.length > 60 && Boolean(caseFile.facts.location)
  }, [caseFile])

  const startSession = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await createIntakeSession(language, true)
      setSession(response.session)
      setCaseFile(response.case_file)
      setMessages(response.messages)
    } catch {
      setError('Could not create intake session. Please check the backend.')
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async (source: 'text' | 'voice' = 'text') => {
    if (!session || !input.trim()) return
    setLoading(true)
    setError(null)
    try {
      const response = await sendIntakeMessage(session.session_id, input.trim(), source)
      setSession(response.session)
      setCaseFile(response.case_file)
      setMessages((current) => [
        ...current,
        response.message,
        ...(response.agent_message ? [response.agent_message] : []),
      ])
      setInput('')
    } catch {
      setError('Could not process the statement.')
    } finally {
      setLoading(false)
    }
  }

  const finishIntake = async () => {
    if (!session) return
    setLoading(true)
    setError(null)
    try {
      const response = await completeIntakeSession(session.session_id)
      setSession(response.session)
      setCaseFile(response.case_file)
    } catch {
      setError('Could not complete intake.')
    } finally {
      setLoading(false)
    }
  }

  const startVoice = () => {
    const SpeechRecognition =
      (window as unknown as { SpeechRecognition?: SpeechRecognitionCtor; webkitSpeechRecognition?: SpeechRecognitionCtor }).SpeechRecognition ||
      (window as unknown as { SpeechRecognition?: SpeechRecognitionCtor; webkitSpeechRecognition?: SpeechRecognitionCtor }).webkitSpeechRecognition

    if (!SpeechRecognition) {
      setError('Voice input is not supported in this browser. Please type the statement.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = language
    recognition.interimResults = false
    recognition.continuous = false
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInput((current) => [current, transcript].filter(Boolean).join(' '))
    }
    recognition.onend = () => setRecording(false)
    setRecording(true)
    recognition.start()
  }

  const uploadAudio = async (file: File | null) => {
    if (!session || !file) return
    setLoading(true)
    setError(null)
    try {
      const response = await uploadIntakeAudio(session.session_id, file, language)
      setSession(response.session)
      setCaseFile(response.case_file)
      setMessages((current) => [
        ...current,
        response.message,
        ...(response.agent_message ? [response.agent_message] : []),
      ])
    } catch {
      setError('Could not upload or process the audio.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Victim Intake</h1>
          <p className="text-sm text-gray-500">
            Record a complaint, ask follow-up questions, and generate a case packet for officer review.
          </p>
        </div>
        {caseFile?.status === 'officer_review' && (
          <Link to={`/review/${caseFile.case_id}`} className="btn-primary inline-flex items-center gap-2">
            <UserCheck className="h-4 w-4" />
            Open Review
          </Link>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertTriangle className="h-4 w-4" />
          {error}
        </div>
      )}

      {!session ? (
        <div className="card space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Start Intake Session</h2>
            <p className="mt-1 text-sm text-gray-500">
              The first version is text-first with optional browser voice input. The legal section engine runs after intake completion.
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-medium text-gray-700">Language</span>
              <select className="input-field" value={language} onChange={(event) => setLanguage(event.target.value)}>
                <option value="en-IN">English India</option>
                <option value="hi-IN">Hindi India</option>
              </select>
            </label>
            <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800">
              Consent is recorded for this demo session before complaint capture starts.
            </div>
          </div>
          <button className="btn-primary inline-flex items-center gap-2" onClick={startSession} disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mic className="h-4 w-4" />}
            Start Session
          </button>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-4">
            {session.emergency_flag && (
              <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
                <ShieldAlert className="mt-0.5 h-5 w-5" />
                <div>
                  <p className="font-semibold">Emergency flag raised</p>
                  <p className="text-sm">This case should be reviewed by a human officer immediately.</p>
                </div>
              </div>
            )}

            <div className="card space-y-4">
              <div className="rounded-lg bg-primary-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-primary-700">Current follow-up</p>
                <p className="mt-1 text-sm text-gray-800">
                  {session.current_question || 'Enough information has been collected to prepare officer review.'}
                </p>
              </div>

              <textarea
                className="input-field min-h-36 resize-y"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Type the victim statement or follow-up answer here..."
              />

              <div className="flex flex-wrap gap-2">
                <button className="btn-primary inline-flex items-center gap-2" onClick={() => sendMessage('text')} disabled={loading || !input.trim()}>
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  Submit Answer
                </button>
                <button className="btn-secondary inline-flex items-center gap-2" onClick={startVoice} disabled={recording}>
                  {recording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  {recording ? 'Listening' : 'Voice Input'}
                </button>
                <label className="btn-secondary inline-flex cursor-pointer items-center gap-2">
                  <Upload className="h-4 w-4" />
                  Upload Audio
                  <input
                    className="hidden"
                    type="file"
                    accept="audio/*,text/plain,.vtt"
                    onChange={(event) => uploadAudio(event.target.files?.[0] || null)}
                  />
                </label>
                <button className="btn-secondary inline-flex items-center gap-2" onClick={finishIntake} disabled={loading || !canComplete}>
                  <CheckCircle2 className="h-4 w-4" />
                  Complete Intake
                </button>
              </div>
            </div>

            <div className="card">
              <h2 className="mb-3 text-lg font-semibold text-gray-900">Conversation</h2>
              {messages.length === 0 ? (
                <p className="text-sm text-gray-500">No victim statement submitted yet.</p>
              ) : (
                <div className="space-y-3">
                  {messages.map((message) => (
                    <div key={message.message_id} className="rounded-lg border border-gray-200 bg-gray-50 p-3">
                      <div className="mb-1 flex items-center justify-between text-xs text-gray-500">
                        <span className="font-semibold uppercase">{message.role}</span>
                        <span>{message.source}</span>
                      </div>
                      <p className="text-sm text-gray-800">{message.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <aside className="space-y-4">
            <div className="card">
              <h2 className="mb-3 text-lg font-semibold text-gray-900">Extracted Case Facts</h2>
              <dl className="space-y-3 text-sm">
                <Fact label="Victim" value={caseFile?.victim.name} />
                <Fact label="Contact" value={caseFile?.victim.contact} />
                <Fact label="Type" value={formatLabel(caseFile?.facts.type)} />
                <Fact label="Date" value={caseFile?.facts.date} />
                <Fact label="Time" value={caseFile?.facts.time} />
                <Fact label="Location" value={caseFile?.facts.location} />
              </dl>
              <div className="mt-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Missing details</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {caseFile?.facts.missing_information.length ? (
                    caseFile.facts.missing_information.map((item) => (
                      <span key={item} className="badge-yellow">{item}</span>
                    ))
                  ) : (
                    <span className="badge-green">Ready for review</span>
                  )}
                </div>
              </div>
            </div>

            <div className="card">
              <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-gray-900">
                <FileText className="h-5 w-5 text-primary-600" />
                Draft Preview
              </h2>
              <pre className="whitespace-pre-wrap rounded-lg bg-gray-50 p-3 text-xs leading-relaxed text-gray-700">
                {caseFile?.statement_draft || 'Draft will appear after the first statement.'}
              </pre>
            </div>
          </aside>
        </div>
      )}
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

function formatLabel(value?: string | null) {
  return value ? value.split('_').join(' ') : value
}

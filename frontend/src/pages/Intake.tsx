import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertTriangle, CheckCircle2, FileText, Loader2, Mic, MicOff, Phone, PhoneOff, Send,
  ShieldAlert, Upload, UserCheck
} from 'lucide-react'
import Vapi from '@vapi-ai/web'
import {
  completeIntakeSession,
  createIntakeSession,
  getVapiConfig,
  sendIntakeMessage,
  sendVapiTranscript,
  uploadIntakeAudio,
  type CaseFile,
  type ConversationMessage,
  type IntakeSession,
  type AddIntakeMessageResponse,
  type VapiConfig,
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

type VapiTranscriptMessage = {
  type?: string
  role?: string
  transcript?: string
  transcriptType?: string
}

type VapiClient = {
  start: (assistantId: string, overrides?: Record<string, unknown>) => Promise<unknown>
  stop: () => void
  say?: (message: string, endCallAfterSpoken?: boolean) => void
  send?: (message: VapiClientMessage) => void
  on: (event: string, callback: (...args: unknown[]) => void) => void
}

type VapiClientMessage =
  | {
      type: 'add-message'
      message: {
        role: 'system'
        content: string
      }
      triggerResponseEnabled: false
    }
  | {
      type: 'control'
      control: 'mute-assistant' | 'unmute-assistant'
    }

const VAPI_LANGUAGE_PROMPTS = {
  'hi-IN': {
    firstMessage:
      'नमस्ते। मैं बोलना एआई हूँ। मैं आपकी शिकायत पुलिस समीक्षा के लिए रिकॉर्ड करने में मदद करूँगा। कृपया अपने शब्दों में बताइए कि क्या हुआ।',
    instruction:
      'The selected language is Hindi. Vapi must not generate its own conversational replies. The BolnaAI backend controls every spoken response. Only transcribe the user and stay silent unless the client explicitly calls say(). When say() is called, speak only the provided Hindi text using Devanagari pronunciation and a natural Indian Hindi accent. Never repeat the same sentence in English.',
  },
  'en-IN': {
    firstMessage:
      'Hello. I am BolnaAI. I can help record your complaint for police review. Please tell me what happened in your own words.',
    instruction:
      'The selected language is English. Vapi must not generate its own conversational replies. The BolnaAI backend controls every spoken response. Only transcribe the user and stay silent unless the client explicitly calls say().',
  },
} as const

const HINDI_FOLLOW_UPS: Record<string, string> = {
  'Please describe what happened in a little more detail.': 'कृपया थोड़ा और विस्तार से बताइए कि क्या हुआ।',
  'When did the incident happen?': 'यह घटना कब हुई?',
  'At what time did the incident happen?': 'यह घटना किस समय हुई?',
  'Where exactly did the incident happen?': 'यह घटना ठीक किस जगह हुई?',
  'Do you know who was involved or can you describe the suspect?': 'क्या आप जानते हैं कि इसमें कौन शामिल था, या आप संदिग्ध व्यक्ति का वर्णन कर सकते हैं?',
  'Do you have any evidence such as photos, videos, screenshots, documents, or witnesses?':
    'क्या आपके पास कोई सबूत है, जैसे फोटो, वीडियो, स्क्रीनशॉट, दस्तावेज़ या गवाह?',
  'This may need immediate attention. Are you currently safe, and do you need urgent police or medical help?':
    'इसमें तुरंत ध्यान देने की ज़रूरत हो सकती है। क्या आप अभी सुरक्षित हैं, और क्या आपको तुरंत पुलिस या मेडिकल मदद चाहिए?',
}

export default function Intake() {
  const [language, setLanguage] = useState('en-IN')
  const [session, setSession] = useState<IntakeSession | null>(null)
  const [caseFile, setCaseFile] = useState<CaseFile | null>(null)
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [recording, setRecording] = useState(false)
  const [vapiConfig, setVapiConfig] = useState<VapiConfig | null>(null)
  const [vapiConnecting, setVapiConnecting] = useState(false)
  const [vapiActive, setVapiActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sessionRef = useRef<IntakeSession | null>(null)
  const vapiRef = useRef<VapiClient | null>(null)
  const seenVapiTranscripts = useRef<Set<string>>(new Set())

  const canComplete = useMemo(() => {
    if (!caseFile) return false
    return caseFile.facts.description.length > 60 && Boolean(caseFile.facts.location)
  }, [caseFile])

  useEffect(() => {
    sessionRef.current = session
  }, [session])

  useEffect(() => {
    getVapiConfig()
      .then((config) => setVapiConfig(withFrontendVapiFallback(config)))
      .catch(() => setVapiConfig(withFrontendVapiFallback({ enabled: false, public_key: null, assistant_id: null })))
  }, [])

  const applyIntakeResponse = (response: AddIntakeMessageResponse) => {
    setSession(response.session)
    setCaseFile(response.case_file)
    setMessages((current) => [
      ...current,
      response.message,
      ...(response.agent_message ? [response.agent_message] : []),
    ])
    return response.agent_message
  }

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
      applyIntakeResponse(response)
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
      applyIntakeResponse(response)
    } catch {
      setError('Could not upload or process the audio.')
    } finally {
      setLoading(false)
    }
  }

  const ensureVapiClient = () => {
    if (vapiRef.current || !vapiConfig?.public_key) return vapiRef.current

    const client = new Vapi(vapiConfig.public_key) as VapiClient
    client.on('call-start', () => {
      setVapiActive(true)
      setVapiConnecting(false)
      setError(null)
    })
    client.on('call-end', () => {
      setVapiActive(false)
      setVapiConnecting(false)
    })
    client.on('error', (event) => {
      setVapiActive(false)
      setVapiConnecting(false)
      setError(event instanceof Error ? event.message : 'Vapi call failed. Please check microphone permissions and Vapi setup.')
    })
    client.on('message', (event) => {
      void handleVapiMessage(event as VapiTranscriptMessage)
    })
    vapiRef.current = client
    return client
  }

  const handleVapiMessage = async (message: VapiTranscriptMessage) => {
    const activeSession = sessionRef.current
    const transcript = message.transcript?.trim()
    const transcriptType = message.transcriptType?.toLowerCase()

    if (!activeSession || message.type !== 'transcript' || message.role !== 'user' || !transcript || transcriptType === 'partial') {
      return
    }

    const key = `${activeSession.session_id}:${transcript}`
    if (seenVapiTranscripts.current.has(key)) return
    seenVapiTranscripts.current.add(key)

    try {
      const response = await sendVapiTranscript(activeSession.session_id, transcript, 'user')
      if (response.processed && response.intake) {
        const agentMessage = applyIntakeResponse(response.intake)
        if (agentMessage?.content && vapiRef.current?.say) {
          vapiRef.current.say(toSpokenLanguage(agentMessage.content, language), false)
        }
      }
    } catch {
      setError('Vapi transcript was captured, but BolnaAI could not process it.')
    }
  }

  const startVapiCall = async () => {
    if (!session) {
      setError('Start an intake session before opening a Vapi call.')
      return
    }
    if (!vapiConfig?.enabled || !vapiConfig.public_key || !vapiConfig.assistant_id) {
      setError('Vapi is not configured. Add VITE_VAPI_PUBLIC_KEY/VITE_VAPI_ASSISTANT_ID or backend VAPI_PUBLIC_KEY/VAPI_ASSISTANT_ID.')
      return
    }

    const client = ensureVapiClient()
    if (!client) return

    setVapiConnecting(true)
    setError(null)
    try {
      const languagePrompt = getVapiLanguagePrompt(language)
      await client.start(vapiConfig.assistant_id, {
        firstMessage: '',
        firstMessageMode: 'assistant-waits-for-user',
        firstMessageInterruptionsEnabled: false,
        startSpeakingPlan: {
          waitSeconds: language === 'hi-IN' ? 2.2 : 1.3,
          smartEndpointingEnabled: false,
          transcriptionEndpointingPlan: {
            onPunctuationSeconds: language === 'hi-IN' ? 1.2 : 0.6,
            onNoPunctuationSeconds: language === 'hi-IN' ? 2.8 : 1.8,
            onNumberSeconds: 2.8,
          },
          customEndpointingRules: [
            {
              type: 'customer',
              regex: '.+',
              timeoutSeconds: language === 'hi-IN' ? 2.8 : 1.8,
            },
          ],
        },
        stopSpeakingPlan: {
          numWords: 3,
          voiceSeconds: 0.4,
          backoffSeconds: 2,
        },
        variableValues: {
          sessionId: session.session_id,
          language,
          languageInstruction: languagePrompt.instruction,
        },
        metadata: {
          sessionId: session.session_id,
          language,
        },
        recordingEnabled: false,
      })
      client.send?.({
        type: 'add-message',
        message: {
          role: 'system',
          content: languagePrompt.instruction,
        },
        triggerResponseEnabled: false,
      })
      client.send?.({
        type: 'control',
        control: 'mute-assistant',
      })
      if (client.say) {
        client.say(languagePrompt.firstMessage, false)
      }
    } catch {
      setVapiConnecting(false)
      setError('Could not start the Vapi call. Check your Vapi keys, assistant ID, and microphone permissions.')
    }
  }

  const stopVapiCall = () => {
    vapiRef.current?.stop()
    setVapiActive(false)
    setVapiConnecting(false)
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
                {vapiActive || vapiConnecting ? (
                  <button className="btn-secondary inline-flex items-center gap-2" onClick={stopVapiCall}>
                    {vapiConnecting ? <Loader2 className="h-4 w-4 animate-spin" /> : <PhoneOff className="h-4 w-4" />}
                    End Vapi Call
                  </button>
                ) : (
                  <button className="btn-secondary inline-flex items-center gap-2" onClick={startVapiCall} disabled={!vapiConfig?.enabled}>
                    <Phone className="h-4 w-4" />
                    Vapi Live Call
                  </button>
                )}
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

function withFrontendVapiFallback(config: VapiConfig): VapiConfig {
  const publicKey = config.public_key || import.meta.env.VITE_VAPI_PUBLIC_KEY || null
  const assistantId = config.assistant_id || import.meta.env.VITE_VAPI_ASSISTANT_ID || null
  return {
    enabled: config.enabled || Boolean(publicKey && assistantId),
    public_key: publicKey,
    assistant_id: assistantId,
  }
}

function getVapiLanguagePrompt(language: string) {
  return language === 'hi-IN' ? VAPI_LANGUAGE_PROMPTS['hi-IN'] : VAPI_LANGUAGE_PROMPTS['en-IN']
}

function toSpokenLanguage(text: string, language: string) {
  if (language !== 'hi-IN') return text
  return HINDI_FOLLOW_UPS[text] || text
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

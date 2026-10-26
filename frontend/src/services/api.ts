import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ─── Types ──────────────────────────────────────────────────

export interface DocumentInfo {
  id: string
  filename: string
  original_filename: string
  file_type: string
  file_size: number
  document_type: string
  status: string
  extracted_text: string | null
  metadata: DocumentMetadata | null
  entities: ExtractedEntity[]
  created_at: string
  updated_at: string
}

export interface DocumentMetadata {
  case_number: string | null
  court_name: string | null
  judge_name: string | null
  date_of_filing: string | null
  date_of_judgment: string | null
  parties: string[]
  location: string | null
  crime_category: string | null
  evidence_list: string[]
  keywords: string[]
}

export interface ExtractedEntity {
  entity_type: string
  value: string
  confidence: number
  context: string | null
}

export interface PredictedSection {
  section: {
    act: string
    section_number: string
    section_title: string
    description: string
    punishment: {
      punishment_type: string
      minimum_duration: string | null
      maximum_duration: string | null
      fine_amount: string | null
      is_cognizable: boolean | null
      is_bailable: boolean | null
    } | null
  }
  confidence: number
  reason: string
  relevant_text: string
}

export interface SectionPredictionResponse {
  document_id: string
  predicted_sections: PredictedSection[]
  total_sections_found: number
  acts_referenced: string[]
}

export interface SummaryResponse {
  document_id: string
  short_summary: string
  detailed_summary: string
  key_findings: string[]
  final_verdict: string
  legal_principles: string[]
}

export interface SimilarCase {
  id: string
  case_title: string
  case_number: string | null
  court: string
  date: string | null
  acts_sections: string[]
  brief_facts: string
  outcome: string
  key_holdings: string[]
  similarity_score: number
}

export interface SimilarCaseResponse {
  query: string
  similar_cases: SimilarCase[]
  total_results: number
}

export interface ChatResponse {
  id: string
  message: string
  sources: Array<{
    text_snippet: string
    similarity: number
    metadata: Record<string, unknown>
  }>
  context_used: number
  document_id: string | null
}

export interface SectionExplanation {
  act: string
  section_number: string
  section_title: string
  simple_explanation: string
  legal_implications: string
  punishment_details: {
    punishment_type: string
    minimum_duration: string | null
    maximum_duration: string | null
    fine_amount: string | null
    is_cognizable: boolean | null
    is_bailable: boolean | null
  } | null
  when_applies: string
  example_cases: string[]
}

export interface VictimProfile {
  name: string | null
  age: string | null
  gender: string | null
  contact: string | null
  address: string | null
}

export interface IncidentFacts {
  type: string | null
  date: string | null
  time: string | null
  location: string | null
  description: string
  sequence_of_events: string[]
  accused: string[]
  witnesses: string[]
  evidence: string[]
  injuries: string[]
  property_loss: string[]
  threats: string[]
  digital_elements: string[]
  missing_information: string[]
}

export interface IntakeSession {
  session_id: string
  language: string
  status: string
  consent_given: boolean
  emergency_flag: boolean
  current_question: string | null
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  message_id: string
  session_id: string
  role: 'victim' | 'agent' | 'officer'
  content: string
  source: string
  timestamp: string
}

export interface CaseFile {
  case_id: string
  session_id: string
  status: string
  victim: VictimProfile
  facts: IncidentFacts
  summary: string
  statement_draft: string
  legal_recommendations: PredictedSection[]
  legal_recommendation_notes: LegalRecommendationNote[]
  officer_notes: string[]
  audit_log: Array<Record<string, unknown>>
  created_at: string
  updated_at: string
}

export interface LegalRecommendationNote {
  law: string
  section: string
  title: string
  confidence: number
  supporting_facts: string[]
  missing_facts: string[]
  explanation: string
  officer_decision: string
}

export interface IntakeSessionResponse {
  session: IntakeSession
  messages: ConversationMessage[]
  case_file: CaseFile
}

export interface AddIntakeMessageResponse {
  session: IntakeSession
  message: ConversationMessage
  agent_message: ConversationMessage | null
  case_file: CaseFile
  next_question: string | null
  is_complete_enough: boolean
}

export interface CompleteIntakeResponse {
  session: IntakeSession
  case_file: CaseFile
}

export interface HitlDecision {
  decision_id: string
  case_id: string
  officer_id: string
  decision_type: string
  target: string
  original_value: string | null
  updated_value: string | null
  reason: string | null
  timestamp: string
}

export interface HitlDecisionResponse {
  decision: HitlDecision
  case_file: CaseFile
}

export interface TranscriptResponse {
  transcript: string
  language: string
  confidence: number
  audio_path: string | null
}

// ─── API Functions ──────────────────────────────────────────

export const uploadDocument = async (file: File): Promise<DocumentInfo> => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const getDocument = async (documentId: string): Promise<DocumentInfo> => {
  const response = await api.get(`/upload/${documentId}`)
  return response.data
}

export const listDocuments = async (): Promise<DocumentInfo[]> => {
  const response = await api.get('/upload/')
  return response.data
}

export const deleteDocument = async (documentId: string): Promise<void> => {
  await api.delete(`/upload/${documentId}`)
}

export const predictSections = async (documentId: string): Promise<SectionPredictionResponse> => {
  const response = await api.get(`/sections/predict/${documentId}`)
  return response.data
}

export const explainSection = async (act: string, sectionNumber: string): Promise<SectionExplanation> => {
  const response = await api.get(`/sections/explain/${act}/${sectionNumber}`)
  return response.data
}

export const getSummary = async (documentId: string): Promise<SummaryResponse> => {
  const response = await api.get(`/summary/${documentId}`)
  return response.data
}

export const findSimilarCases = async (
  query: string,
  topK: number = 5
): Promise<SimilarCaseResponse> => {
  const response = await api.post('/cases/similar', {
    query,
    top_k: topK,
  })
  return response.data
}

export const findSimilarCasesForDocument = async (
  documentId: string,
  topK: number = 5
): Promise<SimilarCaseResponse> => {
  const response = await api.get(`/cases/similar/${documentId}`, {
    params: { top_k: topK },
  })
  return response.data
}

export const sendChatMessage = async (
  message: string,
  documentId?: string,
  chatHistory?: Array<{ role: string; content: string }>
): Promise<ChatResponse> => {
  const response = await api.post('/chat/', {
    message,
    document_id: documentId || null,
    chat_history: chatHistory || [],
  })
  return response.data
}

export const explainJudgment = async (documentId: string): Promise<{ explanation: string }> => {
  const response = await api.post(`/chat/explain-judgment?document_id=${documentId}`)
  return response.data
}

export const explainLaws = async (documentId: string): Promise<{ explanation: string }> => {
  const response = await api.post(`/chat/explain-laws?document_id=${documentId}`)
  return response.data
}

export const explainPunishment = async (documentId: string): Promise<{ explanation: string }> => {
  const response = await api.post(`/chat/explain-punishment?document_id=${documentId}`)
  return response.data
}

export const createIntakeSession = async (
  language: string = 'en-IN',
  consentGiven: boolean = true
): Promise<IntakeSessionResponse> => {
  const response = await api.post('/intake/sessions', {
    language,
    consent_given: consentGiven,
  })
  return response.data
}

export const getIntakeSession = async (sessionId: string): Promise<IntakeSessionResponse> => {
  const response = await api.get(`/intake/sessions/${sessionId}`)
  return response.data
}

export const sendIntakeMessage = async (
  sessionId: string,
  content: string,
  source: 'text' | 'voice' = 'text'
): Promise<AddIntakeMessageResponse> => {
  const response = await api.post(`/intake/sessions/${sessionId}/message`, {
    content,
    role: 'victim',
    source,
  })
  return response.data
}

export const uploadIntakeAudio = async (
  sessionId: string,
  file: File,
  language: string = 'en-IN'
): Promise<AddIntakeMessageResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post(`/intake/${sessionId}/audio`, formData, {
    params: { language },
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const transcribeAudio = async (
  file: File,
  language: string = 'en-IN'
): Promise<TranscriptResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/voice/transcribe-audio', formData, {
    params: { language },
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const speakPrompt = async (
  transcript: string,
  language: string = 'en-IN'
): Promise<{ text: string; language: string; audio_url: string | null; provider: string }> => {
  const response = await api.post('/voice/speak', { transcript, language })
  return response.data
}

export const completeIntakeSession = async (sessionId: string): Promise<CompleteIntakeResponse> => {
  const response = await api.post(`/intake/sessions/${sessionId}/complete`)
  return response.data
}

export const listIntakeCases = async (): Promise<CaseFile[]> => {
  const response = await api.get('/intake/cases')
  return response.data
}

export const getIntakeCase = async (caseId: string): Promise<CaseFile> => {
  const response = await api.get(`/intake/cases/${caseId}`)
  return response.data
}

export const recordHitlDecision = async (
  caseId: string,
  decisionType: 'approve' | 'edit' | 'reject' | 'request_more_info' | 'escalate',
  target: 'statement' | 'extracted_fact' | 'legal_section' | 'full_case',
  reason?: string,
  updatedValue?: string,
  originalValue?: string
): Promise<HitlDecisionResponse> => {
  const response = await api.post(`/hitl/${caseId}/decision`, {
    officer_id: 'officer-demo',
    decision_type: decisionType,
    target,
    reason: reason || null,
    updated_value: updatedValue || null,
    original_value: originalValue || null,
  })
  return response.data
}

export const getHitlAudit = async (caseId: string): Promise<HitlDecision[]> => {
  const response = await api.get(`/hitl/${caseId}/audit`)
  return response.data
}

export const healthCheck = async (): Promise<{ status: string; version: string }> => {
  const response = await api.get('/health')
  return response.data
}

export default api

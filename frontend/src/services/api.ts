import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

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

export const healthCheck = async (): Promise<{ status: string; version: string }> => {
  const response = await api.get('/health')
  return response.data
}

export default api

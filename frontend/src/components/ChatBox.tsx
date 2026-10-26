import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { sendChatMessage, type ChatResponse } from '../services/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: ChatResponse['sources']
  contextUsed?: number
}

interface ChatBoxProps {
  documentId?: string
  documentTitle?: string
}

const QUICK_PROMPTS = [
  { label: 'Explain this judgment', icon: '⚖️', prompt: 'Explain this judgment in simple terms' },
  { label: 'Which laws apply?', icon: '📋', prompt: 'Which laws and legal sections apply to this document?' },
  { label: 'What punishment is possible?', icon: '🔨', prompt: 'What are the possible punishments for the offences in this document?' },
  { label: 'Show similar cases', icon: '🔍', prompt: 'Find similar cases and precedents related to this document' },
]

export default function ChatBox({ documentId, documentTitle }: ChatBoxProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (messageText?: string) => {
    const text = messageText || input.trim()
    if (!text || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const chatHistory = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const response = await sendChatMessage(text, documentId, chatHistory)

      const assistantMessage: Message = {
        id: response.id,
        role: 'assistant',
        content: response.message,
        sources: response.sources,
        contextUsed: response.context_used,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please ensure the backend server is running and try again.',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-xl border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 rounded-t-xl">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary-500" />
          <h3 className="font-semibold text-gray-800">
            LegalAI Assistant
          </h3>
          {documentTitle && (
            <span className="text-xs text-gray-500 ml-2">
              — {documentTitle}
            </span>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <Bot className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              How can I help you?
            </h3>
            <p className="text-sm text-gray-400 mb-6 max-w-md">
              {documentId
                ? 'Ask me anything about this legal document — I can explain judgments, identify applicable laws, discuss punishments, and find similar cases.'
                : 'Upload a document first, then ask me questions about it. I can also answer general questions about Indian law.'}
            </p>

            {/* Quick prompts */}
            {documentId && (
              <div className="grid grid-cols-2 gap-2 max-w-lg w-full">
                {QUICK_PROMPTS.map((prompt) => (
                  <button
                    key={prompt.label}
                    onClick={() => handleSend(prompt.prompt)}
                    className="flex items-center gap-2 px-3 py-2.5 bg-gray-50 hover:bg-primary-50 
                             border border-gray-200 hover:border-primary-200 rounded-lg text-sm 
                             text-gray-700 hover:text-primary-700 transition-all duration-200 text-left"
                  >
                    <span>{prompt.icon}</span>
                    <span className="font-medium">{prompt.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message-enter flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-primary-600" />
              </div>
            )}

            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <div className="text-sm leading-relaxed prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5">
                {message.role === 'assistant' ? (
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                ) : (
                  message.content
                )}
              </div>

              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500 mb-1">
                    Sources ({message.contextUsed} retrieved):
                  </p>
                  {message.sources.slice(0, 3).map((source, idx) => (
                    <p key={idx} className="text-xs text-gray-400 italic truncate">
                      {source.text_snippet}
                    </p>
                  ))}
                </div>
              )}
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="chat-message-enter flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-primary-600" />
            </div>
            <div className="bg-gray-100 rounded-xl px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />
                <span className="text-sm text-gray-500">Analyzing...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-gray-200">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              documentId
                ? 'Ask about this document...'
                : 'Ask a question about Indian law...'
            }
            rows={1}
            className="flex-1 resize-none rounded-lg border border-gray-300 bg-white px-4 py-2.5 
                     text-sm text-gray-900 placeholder-gray-400 focus:border-primary-500 
                     focus:ring-2 focus:ring-primary-200 focus:outline-none transition-all"
            style={{ maxHeight: '120px' }}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="btn-primary flex items-center gap-1 py-2.5"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

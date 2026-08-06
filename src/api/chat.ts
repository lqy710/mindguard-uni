/**
 * AI 咨询聊天 API（从原项目复用，仅改用 uni.request 封装）
 * 对应 legacy/frontend/src/api/chat.ts
 *
 * 发送消息走 HTTP POST（/chat/send），实时推送走 WebSocket（见 utils/websocket.ts）
 * 小程序不支持 SSE，AI 流式回复须用 uni.connectSocket（wss://）
 */
import { get, post, del } from '@/utils/request'
import type { KnowledgeReference } from './knowledge'

/** AI 可调用的工具名 */
export type ToolName = 'analyze_emotion' | 'knowledge_query' | 'trigger_warning'

/** analyze_emotion 的返回结构 */
export interface EmotionToolResult {
  sentimentScore?: number
  emotionType?: string
  emotions?: string[]
  keywords?: string[]
  crisisDetected?: boolean
  recommendation?: string
}

/** knowledge_query 的返回结构 */
export interface KnowledgeToolResult {
  query?: string
  items?: KnowledgeReference[]
}

/** trigger_warning 的返回结构 */
export interface WarningToolResult {
  riskLevel?: 'high' | 'medium' | 'low'
  needImmediateAttention?: boolean
  recommendation?: string
  reason?: string
  warningPushed?: boolean
  warningId?: number | null
  pushError?: string | null
}

export type ToolCallResult =
  | EmotionToolResult
  | KnowledgeToolResult
  | WarningToolResult
  | { error?: string }

/** 一次 function calling 的调用记录，用于向用户展示 AI 的思考链路 */
export interface ToolCall {
  name: ToolName | string
  arguments?: Record<string, unknown>
  result?: ToolCallResult
  status: 'success' | 'error'
  durationMs?: number
}

/** 会话阶段：评估 → 深度访谈 → 资源推荐，危机可随时短路进入 */
export type SessionStage = 'assessment' | 'interview' | 'resource' | 'crisis'

export interface ChatMessage {
  id: number
  /** 所属会话 id，发送消息时返回（可能是后端新建的会话） */
  sessionId?: number
  role: 'user' | 'assistant'
  content: string
  sentimentScore: number
  createdAt: string
  /** RAG 参考来源，仅 AI 实时回复携带，历史消息为空 */
  references?: KnowledgeReference[]
  /** 本次回复触发的工具调用链路，仅 AI 实时回复携带 */
  toolCalls?: ToolCall[]
  /** 当前会话阶段，仅 AI 实时回复携带 */
  stage?: SessionStage
  /** 阶段中文名，由后端下发 */
  stageLabel?: string
  /** 阶段说明文案 */
  stageDescription?: string
  /** 本轮是否发生阶段切换，用于决定是否插入阶段提示气泡 */
  stageChanged?: boolean
}

/** 工具展示元信息：图标 + 中文名 */
export const TOOL_META: Record<string, { icon: string; label: string }> = {
  analyze_emotion: { icon: '🧠', label: '情绪分析' },
  knowledge_query: { icon: '📚', label: '知识库检索' },
  trigger_warning: { icon: '⚠️', label: '风险预警' }
}

/** 阶段展示元信息：图标 + 中文名 + 主题色 */
export const STAGE_META: Record<
  SessionStage,
  { icon: string; label: string; desc: string; color: string; bg: string }
> = {
  assessment: {
    icon: '🔍',
    label: '情况评估',
    desc: '正在了解你的整体状态',
    color: '#2563eb',
    bg: 'rgba(37, 99, 235, 0.1)'
  },
  interview: {
    icon: '💬',
    label: '深度倾谈',
    desc: '正在和你深入聊聊具体情况',
    color: '#7c3aed',
    bg: 'rgba(124, 58, 237, 0.1)'
  },
  resource: {
    icon: '📚',
    label: '资源建议',
    desc: '正在为你整理可行的建议与资料',
    color: '#059669',
    bg: 'rgba(5, 150, 105, 0.1)'
  },
  crisis: {
    icon: '🆘',
    label: '危机支持',
    desc: '已进入紧急支持模式，你的安全最重要',
    color: '#dc2626',
    bg: 'rgba(220, 38, 38, 0.12)'
  }
}

/** 阶段流转顺序，用于进度条展示（危机为特殊态，不在主链路中） */
export const STAGE_FLOW: SessionStage[] = ['assessment', 'interview', 'resource']

/** 创建新会话，返回 sessionId */
export function createSession(): Promise<number> {
  return post<number>('/chat/session')
}

/** 发送消息，返回 AI 回复（含会话 id） */
export function sendMessage(sessionId: number | null, message: string): Promise<ChatMessage> {
  return post<ChatMessage>('/chat/send', { sessionId, message })
}

/** 获取某会话的历史消息 */
export function getSessionMessages(sessionId: number): Promise<ChatMessage[]> {
  return get<ChatMessage[]>(`/chat/session/${sessionId}/messages`)
}

/** 获取当前用户的全部会话 id */
export function getUserSessions(): Promise<number[]> {
  return get<number[]>('/chat/sessions')
}

/** 删除指定会话 */
export function deleteSession(sessionId: number): Promise<void> {
  return del<void>(`/chat/session/${sessionId}`)
}

/** 负反馈原因分类 */
export type FeedbackCategory = 'irrelevant' | 'unsafe' | 'unprofessional' | 'other'

/** 负反馈原因选项，供前端渲染 */
export const FEEDBACK_CATEGORIES: { value: FeedbackCategory; label: string }[] = [
  { value: 'irrelevant', label: '答非所问' },
  { value: 'unsafe', label: '不安全' },
  { value: 'unprofessional', label: '不专业' },
  { value: 'other', label: '其他' }
]

export interface ChatFeedback {
  id: number
  recordId: number
  sessionId: number
  /** 1=点赞，-1=点踩 */
  rating: 1 | -1
  category?: FeedbackCategory
  categoryLabel?: string
  comment?: string
  stage?: SessionStage
  createdAt: string
}

/** 提交对某条 AI 回复的反馈；同一条回复重复提交视为修改 */
export function submitFeedback(params: {
  recordId: number
  rating: 1 | -1
  category?: FeedbackCategory
  comment?: string
}): Promise<ChatFeedback> {
  return post<ChatFeedback>('/chat/feedback', params)
}

/** 获取某会话已提交的反馈，用于回显按钮选中态 */
export function getSessionFeedback(sessionId: number): Promise<ChatFeedback[]> {
  return get<ChatFeedback[]>(`/chat/session/${sessionId}/feedback`)
}

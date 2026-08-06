<template>
  <view class="chat-page">
    <!-- 0. 对话头部：surface 背景 + hairline 底边 -->
    <view class="chat-header">
      <view class="chat-avatar">
        <MIcon name="sparkles" :size="22" color="#3A6359" />
      </view>
      <view class="chat-header-info">
        <text class="chat-header-name">MindGuard AI</text>
        <view class="chat-header-status">
          <view class="status-dot"></view>
          <text class="status-text">在线 · 随时倾听</text>
        </view>
      </view>

      <!-- 当前阶段徽标 -->
      <view
        v-if="messages.length > 0"
        class="stage-badge"
        :class="{ 'stage-badge-crisis': isCrisisStage }"
        :style="{ background: stageInfo.bg, color: stageInfo.color }"
      >
        <text class="stage-badge-text">{{ stageInfo.icon }} {{ stageInfo.label }}</text>
      </view>
    </view>

    <!-- 0.1 阶段进度条：评估 → 深度倾谈 → 资源建议 -->
    <view v-if="messages.length > 0" class="stage-bar">
      <view v-if="isCrisisStage" class="stage-crisis-tip">
        <text class="stage-crisis-text">{{ stageInfo.icon }} {{ stageInfo.desc }}</text>
      </view>
      <view v-else class="stage-steps">
        <view
          v-for="(step, idx) in stageSteps"
          :key="step.stage"
          class="stage-step"
        >
          <view
            class="stage-dot"
            :class="{ 'stage-dot-active': step.active, 'stage-dot-done': step.done }"
          ></view>
          <text
            class="stage-step-label"
            :class="{ 'stage-step-label-active': step.active }"
          >{{ step.label }}</text>
          <view
            v-if="idx < stageSteps.length - 1"
            class="stage-line"
            :class="{ 'stage-line-done': step.done }"
          ></view>
        </view>
      </view>
    </view>

    <!-- 1. 消息区域（flex:1 滚动） -->
    <scroll-view
      class="messages-scroll"
      scroll-y
      :scroll-into-view="scrollIntoView"
      :scroll-with-animation="true"
    >
      <!-- 初始状态：欢迎卡片 + 建议话题 -->
      <view v-if="messages.length === 0" class="welcome-section">
        <view class="welcome-card">
          <view class="welcome-brand">
            <MIcon name="sparkles" :size="22" color="#FBFAF6" />
            <text class="welcome-brand-text">心灵驿站 AI</text>
          </view>
          <text class="welcome-desc">你好！我是你的AI心理助手，有什么想聊的吗？</text>
          <view class="welcome-privacy">
            <MIcon name="lock" :size="16" color="#FBFAF6" />
            <text class="welcome-privacy-text">对话内容将被严格保密</text>
          </view>
        </view>

        <view class="topics">
          <text class="topics-label">你可以这样开始</text>
          <view class="topics-grid">
            <view
              v-for="topic in topicList"
              :key="topic.title"
              class="topic-card"
              @click="sendQuickReply(topic.text)"
            >
              <view class="topic-icon" :style="{ background: topic.bg }">
                <MIcon :name="topic.icon" :size="22" :color="topic.color" />
              </view>
              <text class="topic-title">{{ topic.title }}</text>
              <text class="topic-desc">{{ topic.desc }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 对话状态：消息气泡 -->
      <view v-else class="messages-list">
        <!-- 阶段切换提示：居中细条，不占用对话气泡样式 -->
        <template v-for="msg in messages" :key="msg.id">
        <view
          v-if="msg.stageNotice"
          :id="'msg-' + msg.id"
          class="stage-notice"
        >
          <text
            class="stage-notice-text"
            :style="{
              background: STAGE_META[msg.stageNotice.stage].bg,
              color: STAGE_META[msg.stageNotice.stage].color
            }"
          >
            {{ STAGE_META[msg.stageNotice.stage].icon }} 已进入「{{ msg.stageNotice.label }}」· {{ msg.stageNotice.reason }}
          </text>
        </view>

        <view
          v-else
          :id="'msg-' + msg.id"
          class="message-row"
          :class="msg.role"
        >
          <!-- AI 头像（左） -->
          <view v-if="msg.role === 'assistant'" class="avatar ai-avatar">
            <MIcon name="sparkles" :size="16" color="#3A6359" />
          </view>

          <view class="message-body">
            <!-- 工具调用链路：展示 AI 本轮实际做了什么 -->
            <view
              v-if="msg.role === 'assistant' && msg.toolCalls && msg.toolCalls.length"
              class="tool-calls"
            >
              <view class="tool-chips" @click="toggleToolDetail(msg.id)">
                <view
                  v-for="(tc, idx) in msg.toolCalls"
                  :key="idx"
                  class="tool-chip"
                  :class="{ 'tool-chip-error': tc.status === 'error' }"
                >
                  <text class="tool-chip-text">{{ toolIcon(tc.name) }} {{ toolLabel(tc.name) }}</text>
                </view>
                <text class="tool-toggle">{{ expandedTools.has(msg.id) ? '收起' : '详情' }}</text>
              </view>

              <view v-if="expandedTools.has(msg.id)" class="tool-detail">
                <view v-for="(tc, idx) in msg.toolCalls" :key="'d' + idx" class="tool-detail-item">
                  <text class="tool-detail-name">
                    {{ toolIcon(tc.name) }} {{ toolLabel(tc.name) }}
                    <text v-if="tc.durationMs" class="tool-detail-time"> · {{ tc.durationMs }}ms</text>
                  </text>
                  <text class="tool-detail-summary">{{ toolSummary(tc) }}</text>
                </view>
              </view>
            </view>

            <view class="bubble" :class="msg.role">
              <text class="bubble-text">{{ getDisplayContent(msg) }}</text>
              <view v-if="msg.suggestions && msg.suggestions.length" class="suggestions">
                <view
                  v-for="(s, idx) in msg.suggestions"
                  :key="idx"
                  class="suggestion-item"
                >
                  <text class="suggestion-title">{{ s.title }}</text>
                  <text class="suggestion-content">{{ s.content }}</text>
                </view>
              </view>

              <!-- RAG 参考来源 -->
              <view v-if="msg.references && msg.references.length" class="references">
                <view class="references-head">
                  <MIcon name="notebook-pen" :size="14" color="#6B645C" />
                  <text class="references-label">参考来源</text>
                </view>
                <view
                  v-for="ref in msg.references"
                  :key="ref.articleId"
                  class="reference-item"
                  @click="openReference(ref)"
                >
                  <text class="reference-title">{{ ref.title }}</text>
                  <text class="reference-snippet">{{ truncate(ref.snippet, 50) }}</text>
                </view>
              </view>
            </view>

            <!-- 负反馈采集：仅对有后端 recordId 的 AI 回复展示 -->
            <view v-if="msg.role === 'assistant' && msg.recordId" class="feedback">
              <view class="feedback-actions">
                <view
                  class="feedback-btn"
                  :class="{ active: feedbackMap[msg.recordId] === 1 }"
                  @click="handleLike(msg.recordId)"
                >
                  <text class="feedback-icon">👍</text>
                </view>
                <view
                  class="feedback-btn"
                  :class="{ active: feedbackMap[msg.recordId] === -1 }"
                  @click="handleDislike(msg.recordId)"
                >
                  <text class="feedback-icon">👎</text>
                </view>
                <text v-if="feedbackMap[msg.recordId]" class="feedback-thanks">已反馈</text>
              </view>

              <!-- 点踩后展开原因选择 -->
              <view v-if="feedbackPanelId === msg.recordId" class="feedback-reasons">
                <text class="feedback-reasons-title">哪里不合适？（可选）</text>
                <view class="feedback-reason-list">
                  <view
                    v-for="c in FEEDBACK_CATEGORIES"
                    :key="c.value"
                    class="feedback-reason"
                    @click="handlePickCategory(msg.recordId, c.value)"
                  >
                    <text class="feedback-reason-text">{{ c.label }}</text>
                  </view>
                </view>
              </view>
            </view>

            <text class="msg-time" :class="msg.role">{{ formatTime(msg.createdAt) }}</text>
          </view>

          <!-- 用户头像（右） -->
          <view v-if="msg.role === 'user'" class="avatar user-avatar">
            <text class="avatar-text">{{ userInitial }}</text>
          </view>
        </view>
        </template>

        <!-- AI 思考动画 -->
        <view v-if="loading" class="message-row assistant" id="msg-loading">
          <view class="avatar ai-avatar">
            <MIcon name="sparkles" :size="16" color="#3A6359" />
          </view>
          <view class="message-body">
            <view class="bubble assistant typing-bubble">
              <view class="typing">
                <view class="dot"></view>
                <view class="dot"></view>
                <view class="dot"></view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 2. 快捷回复（对话进行中、非加载态显示） -->
    <view v-if="messages.length > 0 && !loading" class="quick-replies">
      <scroll-view scroll-x class="quick-scroll">
        <view class="quick-track">
          <view
            v-for="reply in quickReplies"
            :key="reply.label"
            class="quick-reply-btn"
            @click="sendQuickReply(reply.text)"
          >
            <text>{{ reply.label }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 3. 底部输入区（固定，适配键盘） -->
    <view class="input-bar" :style="inputBarStyle">
      <view class="input-wrapper">
        <input
          class="input-field"
          v-model="inputMessage"
          placeholder="说点什么..."
          placeholder-class="input-placeholder"
          confirm-type="send"
          :adjust-position="false"
          @confirm="sendMessage"
          @keyboardheightchange="onKeyboardHeightChange"
        />
      </view>
      <view
        class="send-btn"
        :class="{ disabled: !canSend }"
        @click="sendMessage"
      >
        <MIcon name="send" :size="20" color="#FBFAF6" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { onLoad, onShow, onUnload } from '@dcloudio/uni-app'
import {
  sendMessage as sendChatMessage,
  submitFeedback,
  TOOL_META,
  STAGE_META,
  STAGE_FLOW,
  FEEDBACK_CATEGORIES,
  type ChatMessage,
  type ToolCall,
  type SessionStage,
  type EmotionToolResult,
  type KnowledgeToolResult,
  type WarningToolResult,
  type FeedbackCategory
} from '@/api/chat'
import type { KnowledgeReference } from '@/api/knowledge'
import { useUserStore } from '@/stores/user'
import { wsService, WS_MESSAGE_TYPES } from '@/utils/websocket'
import MIcon from '@/components/MIcon.vue'

interface Suggestion {
  title: string
  content: string
}

interface MessageItem extends ChatMessage {
  suggestions?: Suggestion[]
  /** 阶段切换提示气泡（插在消息流中，非真实对话内容） */
  stageNotice?: { stage: SessionStage; label: string; reason: string }
  /**
   * 后端 chat_record.id。消息流内的 id 是前端自增序号，提交反馈必须用这个真实 id。
   * 本地兜底消息（如发送失败提示）没有该字段，不展示反馈入口。
   */
  recordId?: number
}

interface QuickReply {
  label: string
  text: string
}

interface Topic {
  icon: string
  title: string
  desc: string
  text: string
  bg: string
  color: string
}

const userStore = useUserStore()

const messages = ref<MessageItem[]>([])
const inputMessage = ref('')
const loading = ref(false)
const sessionId = ref<number | null>(null)
const scrollIntoView = ref('')
const keyboardHeight = ref(0)
/** 展开了工具详情的消息 id 集合 */
const expandedTools = ref<Set<number>>(new Set())
/** 当前会话阶段，由后端每轮回复下发 */
const currentStage = ref<SessionStage>('assessment')

/** 已提交反馈的结果，key 为后端 recordId，用于渲染选中态 */
const feedbackMap = ref<Record<number, 1 | -1>>({})
/** 当前正在选择负反馈原因的 recordId，null 表示没有展开的原因面板 */
const feedbackPanelId = ref<number | null>(null)
/** 正在提交中的 recordId 集合，避免重复点击 */
const feedbackSubmitting = ref<Set<number>>(new Set())

let idSeed = 0
let unsubscribe: (() => void) | null = null

const userInitial = computed(() => {
  const name = userStore.userInfo?.nickname || userStore.userInfo?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const canSend = computed(() => inputMessage.value.trim().length > 0 && !loading.value)

/** 当前阶段的展示元信息 */
const stageInfo = computed(() => STAGE_META[currentStage.value] || STAGE_META.assessment)

/** 危机阶段单独高亮，样式与常规阶段区分 */
const isCrisisStage = computed(() => currentStage.value === 'crisis')

/** 主链路进度：危机态不参与进度条 */
const stageSteps = computed(() =>
  STAGE_FLOW.map((s) => ({
    stage: s,
    label: STAGE_META[s].label,
    active: s === currentStage.value,
    done: !isCrisisStage.value && STAGE_FLOW.indexOf(currentStage.value) > STAGE_FLOW.indexOf(s)
  }))
)

const inputBarStyle = computed(() => {
  if (keyboardHeight.value > 0) {
    return `padding-bottom: ${keyboardHeight.value}px`
  }
  return 'padding-bottom: calc(16rpx + env(safe-area-inset-bottom))'
})

// 初始建议话题（点击即发送）
const topicList: Topic[] = [
  { icon: 'chat', title: '我想找人聊聊', desc: '陪你聊聊天', text: '我想找人聊聊', bg: '#E6EEEA', color: '#3A6359' },
  { icon: 'cloud', title: '最近心情不好', desc: '倾诉你的烦恼', text: '最近心情不好', bg: '#F4E3DB', color: '#C26B4F' },
  { icon: 'briefcase', title: '工作压力大', desc: '一起想办法', text: '工作压力大', bg: '#F0E8D4', color: '#B8862F' },
  { icon: 'users', title: '人际关系问题', desc: '聊聊相处困惑', text: '人际关系问题', bg: '#E8E3F0', color: '#6B5B9E' }
]

// 对话进行中的快捷回复
const quickReplies: QuickReply[] = [
  { label: '这些建议很有帮助', text: '这些建议很有帮助' },
  { label: '了解更多方法', text: '我想了解更多缓解压力的方法' },
  { label: '还有其他烦恼', text: '我还有其他烦恼' },
  { label: '谢谢你的倾听', text: '谢谢你的倾听' }
]

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `今天 ${hours}:${minutes}`
}

/** 解析回复中的编号列表 "1. 标题\n内容" */
function parseSuggestions(content: string): Suggestion[] {
  const suggestions: Suggestion[] = []
  const regex = /\d+\.\s*([^\n]+)\n([^\n]+)/g
  let match: RegExpExecArray | null
  while ((match = regex.exec(content)) !== null) {
    suggestions.push({ title: match[1].trim(), content: match[2].trim() })
  }
  return suggestions
}

/** 展示用文案：有建议列表时移除编号部分，仅保留前文，避免与建议块重复 */
function getDisplayContent(msg: MessageItem): string {
  if (!msg.suggestions || msg.suggestions.length === 0) {
    return msg.content
  }
  return msg.content
    .replace(/\d+\.\s*[^\n]+\n[^\n]+/g, '')
    .replace(/\n{2,}/g, '\n')
    .trim()
}

/** 截断过长片段，避免气泡被参考来源撑爆 */
function truncate(text: string, max: number): string {
  if (!text) return ''
  return text.length > max ? `${text.slice(0, max)}…` : text
}

/** 点击参考来源跳转文章详情；兜底语料（id<=0）无详情页 */
function openReference(ref: KnowledgeReference): void {
  if (!ref.articleId || ref.articleId <= 0) {
    uni.showToast({ title: '该内容暂无详情页', icon: 'none' })
    return
  }
  uni.navigateTo({ url: `/pages/knowledge/detail?id=${ref.articleId}` })
}

function toolIcon(name: string): string {
  return TOOL_META[name]?.icon ?? '🔧'
}

function toolLabel(name: string): string {
  return TOOL_META[name]?.label ?? name
}

/** 把工具原始结果转成一句人话，避免把 JSON 直接怼给用户 */
function toolSummary(tc: ToolCall): string {
  if (tc.status === 'error') {
    return '执行失败，已使用备用方案回复'
  }

  const result = tc.result ?? {}

  if (tc.name === 'analyze_emotion') {
    const r = result as EmotionToolResult
    const parts: string[] = []
    if (r.emotionType) parts.push(`情绪：${r.emotionType}`)
    if (typeof r.sentimentScore === 'number') {
      parts.push(`情绪分值：${r.sentimentScore.toFixed(2)}`)
    }
    if (r.keywords?.length) parts.push(`关键词：${r.keywords.slice(0, 3).join('、')}`)
    return parts.length ? parts.join('　') : '已完成情绪分析'
  }

  if (tc.name === 'knowledge_query') {
    const r = result as KnowledgeToolResult
    const count = r.items?.length ?? 0
    if (count === 0) return '知识库未命中相关内容'
    const titles = (r.items ?? []).slice(0, 2).map((i) => i.title).join('、')
    return `命中 ${count} 篇资料：${titles}`
  }

  if (tc.name === 'trigger_warning') {
    const r = result as WarningToolResult
    const level = r.riskLevel === 'high' ? '高风险' : r.riskLevel === 'medium' ? '中风险' : '低风险'
    if (r.warningPushed) {
      return `${level} · 已通知心理老师介入`
    }
    const why = r.reason || r.pushError || '未达到预警推送条件'
    return `${level} · 未推送：${why}`
  }

  return '已完成'
}

function toggleToolDetail(msgId: number): void {
  // 小程序端 Set 不是深响应，需替换引用触发更新
  const next = new Set(expandedTools.value)
  if (next.has(msgId)) {
    next.delete(msgId)
  } else {
    next.add(msgId)
  }
  expandedTools.value = next
}

function addMessage(
  content: string,
  role: 'user' | 'assistant',
  suggestions?: Suggestion[],
  references?: KnowledgeReference[],
  toolCalls?: ToolCall[],
  recordId?: number
): void {
  const msg: MessageItem = {
    id: ++idSeed,
    role,
    content,
    sentimentScore: 0,
    createdAt: new Date().toISOString(),
    suggestions,
    references,
    toolCalls,
    recordId
  }
  messages.value.push(msg)
  scrollToLatest()
}

/** 点赞：直接提交，无需选原因 */
async function handleLike(recordId?: number): Promise<void> {
  if (!recordId) return
  feedbackPanelId.value = null
  await doSubmitFeedback(recordId, 1)
}

/** 点踩：先展开原因面板，选完原因再提交 */
function handleDislike(recordId?: number): void {
  if (!recordId) return
  feedbackPanelId.value = feedbackPanelId.value === recordId ? null : recordId
}

/** 选择负反馈原因后提交 */
async function handlePickCategory(recordId: number, category: FeedbackCategory): Promise<void> {
  feedbackPanelId.value = null
  await doSubmitFeedback(recordId, -1, category)
}

async function doSubmitFeedback(
  recordId: number,
  rating: 1 | -1,
  category?: FeedbackCategory
): Promise<void> {
  if (feedbackSubmitting.value.has(recordId)) return
  const submitting = new Set(feedbackSubmitting.value)
  submitting.add(recordId)
  feedbackSubmitting.value = submitting

  // 乐观更新，失败再回滚，避免用户点完没反应
  const previous = feedbackMap.value[recordId]
  feedbackMap.value = { ...feedbackMap.value, [recordId]: rating }

  try {
    await submitFeedback({ recordId, rating, category })
    uni.showToast({ title: '感谢你的反馈', icon: 'none' })
  } catch (error) {
    console.error('提交反馈失败:', error)
    const rollback = { ...feedbackMap.value }
    if (previous === undefined) {
      delete rollback[recordId]
    } else {
      rollback[recordId] = previous
    }
    feedbackMap.value = rollback
    uni.showToast({ title: '提交失败，请稍后再试', icon: 'none' })
  } finally {
    const next = new Set(feedbackSubmitting.value)
    next.delete(recordId)
    feedbackSubmitting.value = next
  }
}

/** 在消息流中插入一条阶段切换提示（居中的浅色小条，不是对话气泡） */
function addStageNotice(stage: SessionStage, label?: string): void {
  const meta = STAGE_META[stage] || STAGE_META.assessment
  messages.value.push({
    id: ++idSeed,
    role: 'assistant',
    content: '',
    sentimentScore: 0,
    createdAt: new Date().toISOString(),
    stageNotice: {
      stage,
      label: label || meta.label,
      reason: meta.desc
    }
  })
  scrollToLatest()
}

function scrollToLatest(): void {
  nextTick(() => {
    // 先清空再赋值，确保即便同 id 也能触发滚动
    scrollIntoView.value = ''
    nextTick(() => {
      scrollIntoView.value = loading.value ? 'msg-loading' : 'msg-' + idSeed
    })
  })
}

async function sendMessage(): Promise<void> {
  const message = inputMessage.value.trim()
  if (!message || loading.value) return

  inputMessage.value = ''
  addMessage(message, 'user')
  loading.value = true
  scrollToLatest()

  try {
    const reply = await sendChatMessage(sessionId.value, message)
    // 后端返回本次回复所属的会话 id（首轮为新建会话），据此延续多轮上下文
    if (reply.sessionId != null) {
      sessionId.value = reply.sessionId
    }
    // 阶段更新：先插切换提示，再放 AI 回复，顺序上更符合阅读直觉
    if (reply.stage) {
      const changed = reply.stageChanged && reply.stage !== currentStage.value
      currentStage.value = reply.stage
      if (changed) {
        addStageNotice(reply.stage, reply.stageLabel)
      }
    }

    const suggestions = parseSuggestions(reply.content)
    addMessage(
      reply.content,
      'assistant',
      suggestions.length ? suggestions : undefined,
      reply.references?.length ? reply.references : undefined,
      reply.toolCalls?.length ? reply.toolCalls : undefined,
      reply.id
    )
  } catch (error) {
    console.error('发送消息失败:', error)
    addMessage('抱歉，我暂时无法回应，请稍后再试。', 'assistant')
  } finally {
    loading.value = false
    // loading 关闭后重新定位到最终消息（loading 占位已移除）
    scrollToLatest()
  }
}

function sendQuickReply(text: string): void {
  inputMessage.value = text
  sendMessage()
}

function onKeyboardHeightChange(e: { height: number }): void {
  keyboardHeight.value = e.height
  if (e.height > 0) {
    scrollToLatest()
  }
}

onLoad(() => {
  // 订阅 WebSocket 推送的聊天消息（实时通知）
  unsubscribe = wsService.subscribe(WS_MESSAGE_TYPES.CHAT, (message) => {
    const data = message.data as { sessionId?: number; content?: string } | undefined
    if (!data || !data.content) return
    // 当前会话的回复已通过 HTTP 处理，忽略避免重复
    if (data.sessionId === sessionId.value) return
    if (loading.value) return
    const suggestions = parseSuggestions(data.content)
    addMessage(data.content, 'assistant', suggestions.length ? suggestions : undefined)
  })
})

onShow(() => {
  // 登录守卫：未登录跳转登录页
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
  if (!userStore.userInfo) {
    userStore.fetchUserInfo().catch(() => {})
  }
  // 小程序切后台会断连，每次 onShow 重连（connect 为幂等）
  if (userStore.token) {
    wsService.connect(userStore.token).catch(() => {})
  }
})

onUnload(() => {
  if (unsubscribe) {
    unsubscribe()
    unsubscribe = null
  }
  wsService.disconnect()
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #EDE9E1;
  overflow: hidden;
}

/* 0. 对话头部：surface 背景 + hairline 底边 */
.chat-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 40rpx;
  background: #FBFAF6;
  border-bottom: 2rpx solid #E2DDD2;
}

.chat-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 999rpx;
  background: #E6EEEA;
  border: 3rpx solid #4A7C6F;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-header-info {
  flex: 1;
  min-width: 0;
}

.chat-header-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #2A2722;
  line-height: 1.4;
}

.chat-header-status {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 4rpx;
}

.status-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #4A7C6F;
  flex-shrink: 0;
}

.status-text {
  font-size: 24rpx;
  color: #4A7C6F;
}

/* 0.1 当前阶段徽标 */
.stage-badge {
  flex-shrink: 0;
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
}

.stage-badge-text {
  font-size: 22rpx;
  font-weight: 600;
  white-space: nowrap;
}

.stage-badge-crisis {
  animation: stage-pulse 1.6s ease-in-out infinite;
}

@keyframes stage-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.55; }
}

/* 0.2 阶段进度条 */
.stage-bar {
  flex-shrink: 0;
  padding: 16rpx 40rpx;
  background: #FBFAF6;
  border-bottom: 2rpx solid #E2DDD2;
}

.stage-steps {
  display: flex;
  align-items: center;
}

.stage-step {
  display: flex;
  align-items: center;
  flex: 1;
}

.stage-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 999rpx;
  background: #D6D0C4;
  flex-shrink: 0;
}

.stage-dot-done {
  background: #4A7C6F;
}

.stage-dot-active {
  background: #3A6359;
  box-shadow: 0 0 0 6rpx rgba(74, 124, 111, 0.18);
}

.stage-step-label {
  font-size: 22rpx;
  color: #8A8378;
  margin-left: 10rpx;
  white-space: nowrap;
}

.stage-step-label-active {
  color: #3A6359;
  font-weight: 600;
}

.stage-line {
  flex: 1;
  height: 2rpx;
  background: #E2DDD2;
  margin: 0 12rpx;
  min-width: 20rpx;
}

.stage-line-done {
  background: #4A7C6F;
}

.stage-crisis-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8rpx 0;
}

.stage-crisis-text {
  font-size: 24rpx;
  font-weight: 600;
  color: #dc2626;
}

/* 阶段切换提示条 */
.stage-notice {
  display: flex;
  justify-content: center;
  margin: 16rpx 0;
}

.stage-notice-text {
  font-size: 22rpx;
  padding: 10rpx 24rpx;
  border-radius: 999rpx;
  text-align: center;
  max-width: 88%;
}

/* 1. 消息滚动区 */
.messages-scroll {
  flex: 1;
  min-height: 0;
  box-sizing: border-box;
}

/* —— 初始状态：欢迎卡片 —— */
.welcome-section {
  padding: 32rpx;
}

.welcome-card {
  background: #3A6359;
  border-radius: 32rpx;
  padding: 40rpx 32rpx;
  display: flex;
  flex-direction: column;
}

.welcome-brand {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.welcome-brand-text {
  font-size: 36rpx;
  font-weight: 700;
  color: #FBFAF6;
  line-height: 1.4;
}

.welcome-desc {
  font-size: 28rpx;
  color: #FBFAF6;
  line-height: 1.6;
  margin-top: 16rpx;
}

.welcome-privacy {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 24rpx;
}

.welcome-privacy-text {
  font-size: 24rpx;
  color: rgba(251, 250, 246, 0.75);
}

/* —— 建议话题卡片 —— */
.topics {
  margin-top: 32rpx;
}

.topics-label {
  font-size: 26rpx;
  color: #6B645C;
  margin-bottom: 20rpx;
  display: block;
}

.topics-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.topic-card {
  width: 331rpx;
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-radius: 32rpx;
  padding: 28rpx 24rpx;
  margin-bottom: 24rpx;
  display: flex;
  flex-direction: column;
}

.topic-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
}

.topic-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #2A2722;
  margin-bottom: 8rpx;
}

.topic-desc {
  font-size: 24rpx;
  color: #6B645C;
  line-height: 1.5;
}

/* —— 消息气泡 —— */
.messages-list {
  padding: 32rpx 40rpx;
}

.message-row {
  display: flex;
  margin-bottom: 32rpx;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-avatar {
  background: #E6EEEA;
  margin-right: 16rpx;
}

.user-avatar {
  background: #E8E3F0;
  margin-left: 16rpx;
}

.avatar-text {
  font-size: 24rpx;
  font-weight: 600;
  color: #6B5B9E;
}

.message-body {
  max-width: 76%;
  display: flex;
  flex-direction: column;
}

.message-row.user .message-body {
  align-items: flex-end;
}

.bubble {
  padding: 24rpx;
  border-radius: 32rpx;
}

.bubble.assistant {
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-top-left-radius: 16rpx;
}

.bubble.user {
  background: #3A6359;
  border-top-right-radius: 16rpx;
}

.bubble-text {
  font-size: 28rpx;
  line-height: 1.7;
  color: #2A2722;
  /* 保留 \n 换行 */
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble.user .bubble-text {
  color: #FBFAF6;
}

/* —— 建议列表 —— */
.suggestions {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 2rpx solid #E2DDD2;
}

.suggestion-item {
  margin-bottom: 16rpx;
}

.suggestion-item:last-child {
  margin-bottom: 0;
}

.suggestion-title {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: #3A6359;
  margin-bottom: 6rpx;
}

.suggestion-content {
  font-size: 24rpx;
  color: #4A453E;
  line-height: 1.6;
}

/* —— 工具调用链路 —— */
.tool-calls {
  margin-bottom: 12rpx;
}

.tool-chips {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10rpx;
}

.tool-chip {
  padding: 6rpx 16rpx;
  background: #EFECE3;
  border: 2rpx solid #E2DDD2;
  border-radius: 24rpx;
}

.tool-chip-error {
  background: #FBEEE9;
  border-color: #F0D3C6;
}

.tool-chip-text {
  font-size: 20rpx;
  color: #6B645C;
}

.tool-toggle {
  font-size: 20rpx;
  color: #A89F92;
  text-decoration: underline;
}

.tool-detail {
  margin-top: 12rpx;
  padding: 16rpx;
  background: #F7F5EF;
  border-radius: 12rpx;
}

.tool-detail-item {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.tool-detail-item + .tool-detail-item {
  margin-top: 14rpx;
  padding-top: 14rpx;
  border-top: 2rpx dashed #E2DDD2;
}

.tool-detail-name {
  font-size: 21rpx;
  color: #4A453E;
  font-weight: 500;
}

.tool-detail-time {
  font-size: 20rpx;
  color: #A89F92;
  font-weight: 400;
}

.tool-detail-summary {
  font-size: 21rpx;
  color: #6B645C;
  line-height: 1.5;
}

/* —— RAG 参考来源 —— */
.references {
  margin-top: 20rpx;
  padding-top: 16rpx;
  border-top: 2rpx dashed #E2DDD2;
}

.references-head {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 12rpx;
}

.references-label {
  font-size: 22rpx;
  color: #6B645C;
}

.reference-item {
  background: #F3F1EA;
  border-radius: 16rpx;
  padding: 14rpx 18rpx;
  margin-bottom: 10rpx;
  display: flex;
  flex-direction: column;
}

.reference-item:last-child {
  margin-bottom: 0;
}

.reference-title {
  font-size: 24rpx;
  font-weight: 600;
  color: #3A6359;
  line-height: 1.5;
}

.reference-snippet {
  font-size: 22rpx;
  color: #6B645C;
  line-height: 1.5;
  margin-top: 4rpx;
}

/* —— 时间戳 —— */
/* —— 负反馈采集 —— */
.feedback {
  margin-top: 12rpx;
}

.feedback-actions {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.feedback-btn {
  padding: 6rpx 18rpx;
  background: #EFECE3;
  border: 2rpx solid #E2DDD2;
  border-radius: 24rpx;
}

.feedback-btn.active {
  background: #DDEAE4;
  border-color: #3A6359;
}

.feedback-icon {
  font-size: 24rpx;
}

.feedback-thanks {
  font-size: 22rpx;
  color: #6B645C;
}

.feedback-reasons {
  margin-top: 12rpx;
  padding: 16rpx;
  background: #F7F5EF;
  border: 2rpx solid #E2DDD2;
  border-radius: 16rpx;
}

.feedback-reasons-title {
  font-size: 22rpx;
  color: #6B645C;
}

.feedback-reason-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 12rpx;
}

.feedback-reason {
  padding: 6rpx 18rpx;
  background: #FFFFFF;
  border: 2rpx solid #E2DDD2;
  border-radius: 24rpx;
}

.feedback-reason-text {
  font-size: 22rpx;
  color: #3D3934;
}

.msg-time {
  font-size: 24rpx;
  color: #6B645C;
  margin-top: 8rpx;
}

.msg-time.assistant {
  text-align: left;
}

.msg-time.user {
  text-align: right;
}

/* —— AI 思考动画 —— */
.typing-bubble {
  padding: 24rpx 28rpx;
}

.typing {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #4A7C6F;
  animation: typing 1.4s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8rpx);
    opacity: 1;
  }
}

/* 2. 快捷回复 */
.quick-replies {
  flex-shrink: 0;
  background: #FBFAF6;
  border-top: 2rpx solid #E2DDD2;
  padding: 16rpx 0;
}

.quick-scroll {
  width: 100%;
  white-space: nowrap;
}

.quick-track {
  display: inline-flex;
  align-items: center;
  padding: 0 32rpx;
  gap: 16rpx;
}

.quick-reply-btn {
  flex-shrink: 0;
  padding: 12rpx 28rpx;
  border-radius: 999rpx;
  background: #E6EEEA;
  font-size: 26rpx;
  color: #3A6359;
  font-weight: 500;
  white-space: nowrap;
}

/* 3. 底部输入区 */
.input-bar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 32rpx;
  background: #FBFAF6;
  border-top: 2rpx solid #E2DDD2;
  box-sizing: border-box;
}

.input-wrapper {
  flex: 1;
  height: 76rpx;
  background: #EDE9E1;
  border: 2rpx solid #E2DDD2;
  border-radius: 999rpx;
  padding: 0 28rpx;
  display: flex;
  align-items: center;
}

.input-field {
  flex: 1;
  height: 76rpx;
  font-size: 28rpx;
  color: #2A2722;
}

.input-placeholder {
  color: #6B645C;
  font-size: 28rpx;
}

.send-btn {
  width: 76rpx;
  height: 76rpx;
  border-radius: 50%;
  background: #3A6359;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-btn.disabled {
  background: #E2DDD2;
}
</style>

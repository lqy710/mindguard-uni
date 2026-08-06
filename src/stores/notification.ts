/**
 * 全局通知状态管理（从原项目迁移，改造点：
 * - ElNotification → uni.showToast（普通通知）/ uni.showModal（危机预警等重要通知）
 * - window.dispatchEvent(new CustomEvent(...)) → uni.$emit('data-update', data)
 * - init() 中已登录则建立 WebSocket 连接（connect 幂等，可与 chat 页共存）
 * 对应 legacy/frontend/src/stores/notification.ts
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { wsService, WS_MESSAGE_TYPES } from '@/utils/websocket'
import type { WebSocketMessage, ConnectionStatus } from '@/utils/websocket'
import { useUserStore } from '@/stores/user'

/** 通知条目类型 */
export type NotificationType = 'warning' | 'chat' | 'data_update' | 'system'

export interface NotificationItem {
  id: string
  type: NotificationType
  title: string
  content: string
  data?: unknown
  read: boolean
  createdAt: number
}

/** 预警消息 data 结构 */
interface WarningData {
  riskLevel: string
  summary: string
}

/** 数据更新消息 data 结构 */
interface DataUpdateData {
  module?: string
  action?: string
  message?: string
}

/** 聊天消息 data 结构 */
interface ChatData {
  content: string
}

/** 数据更新事件名（供各页面 uni.$on 订阅，刷新本地数据） */
export const DATA_UPDATE_EVENT = 'data-update'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<NotificationItem[]>([])
  const wsStatus = ref<ConnectionStatus>('disconnected')

  /** 未读数（供首页消息按钮显示徽标） */
  const unreadCount = computed(() => notifications.value.filter((n) => !n.read).length)

  /**
   * 初始化：订阅 WebSocket 推送，已登录则建立连接。
   * 应在 App.vue 的 onLaunch 中调用一次。
   */
  function init(): void {
    wsService.onStatusChange((status) => {
      wsStatus.value = status
    })

    wsService.subscribe(WS_MESSAGE_TYPES.WARNING, handleWarning)
    wsService.subscribe(WS_MESSAGE_TYPES.CHAT, handleChat)
    wsService.subscribe(WS_MESSAGE_TYPES.DATA_UPDATE, handleDataUpdate)
    wsService.subscribe(WS_MESSAGE_TYPES.SYSTEM, handleSystem)
    wsService.subscribe('*', handleAllMessages)

    // 已登录则建立 WebSocket 连接（connect 幂等；未登录时由登录流程或 chat 页触发）
    const token = useUserStore().token
    if (token) {
      wsService
        .connect(token)
        .catch((err: unknown) => {
          console.warn('[Notification] WebSocket 连接失败:', err)
        })
    }
  }

  /** 预警通知：危机/风险等级，用 showModal 强提示（需用户确认） */
  function handleWarning(message: WebSocketMessage<WarningData>): void {
    const data = message.data
    const content = `检测到${data.riskLevel}风险: ${data.summary}`
    addNotification({
      type: 'warning',
      title: '预警通知',
      content,
      data
    })

    uni.showModal({
      title: '预警通知',
      content,
      showCancel: false,
      confirmText: '我知道了'
    })
  }

  /** 聊天新消息：仅入库，不打断用户 */
  function handleChat(message: WebSocketMessage<ChatData>): void {
    const data = message.data
    addNotification({
      type: 'chat',
      title: '新消息',
      content: data.content,
      data
    })
  }

  /** 数据更新：入库 + 通过 uni 事件总线广播，供各页面刷新本地数据 */
  function handleDataUpdate(message: WebSocketMessage<DataUpdateData>): void {
    const data = message.data
    addNotification({
      type: 'data_update',
      title: '数据更新',
      content: data.message || `${data.module}数据已${data.action}`,
      data
    })

    uni.$emit(DATA_UPDATE_EVENT, data)
  }

  /** 系统通知：普通提示，用 showToast */
  function handleSystem(message: WebSocketMessage<string>): void {
    const content = message.data
    addNotification({
      type: 'system',
      title: '系统通知',
      content,
      data: null
    })

    uni.showToast({
      title: content,
      icon: 'none',
      duration: 2500
    })
  }

  function handleAllMessages(message: WebSocketMessage): void {
    console.log('[WebSocket] 收到消息:', message)
  }

  /** 新增通知（最新在前，最多保留 100 条） */
  function addNotification(item: Omit<NotificationItem, 'id' | 'read' | 'createdAt'>): void {
    const notification: NotificationItem = {
      ...item,
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
      read: false,
      createdAt: Date.now()
    }
    notifications.value.unshift(notification)

    if (notifications.value.length > 100) {
      notifications.value = notifications.value.slice(0, 100)
    }
  }

  function markAsRead(id: string): void {
    const notification = notifications.value.find((n) => n.id === id)
    if (notification) {
      notification.read = true
    }
  }

  function markAllAsRead(): void {
    notifications.value.forEach((n) => {
      n.read = true
    })
  }

  function clearNotifications(): void {
    notifications.value = []
  }

  function removeNotification(id: string): void {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  return {
    notifications,
    wsStatus,
    unreadCount,
    init,
    markAsRead,
    markAllAsRead,
    clearNotifications,
    removeNotification
  }
})

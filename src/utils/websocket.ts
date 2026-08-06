/**
 * WebSocket 服务（替代浏览器原生 WebSocket）
 * 对应 legacy/frontend/src/utils/websocket.ts
 *
 * 小程序不支持 new WebSocket()，必须用 uni.connectSocket（wss://）
 * wss 域名须在小程序后台"socket 合法域名"白名单配置
 * 小程序切后台会断连，需在页面 onShow 中重连（wsService.connect 为幂等）
 */
import { BASE_URL } from '@/config'

export interface WebSocketMessage<T = unknown> {
  type: string
  data: T
  timestamp: number
}

export type MessageHandler<T = unknown> = (message: WebSocketMessage<T>) => void

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

/** 由 HTTP 后端地址推导 wss/ws 地址 */
function buildWsUrl(token: string): string {
  const wsScheme = BASE_URL.startsWith('https') ? 'wss' : 'ws'
  const host = BASE_URL.replace(/^https?:\/\//, '')
  return `${wsScheme}://${host}/ws?token=${encodeURIComponent(token)}`
}

class WebSocketService {
  private socketTask: UniApp.SocketTask | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private reconnectAttempts = 0
  private readonly maxReconnectAttempts = 5
  private readonly reconnectDelay = 3000
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private status: ConnectionStatus = 'disconnected'
  private statusListeners: Set<(status: ConnectionStatus) => void> = new Set()
  private currentToken = ''

  connect(token: string): Promise<void> {
    return new Promise<void>((resolve, reject) => {
      // 已连接直接返回
      if (this.status === 'connected') {
        resolve()
        return
      }
      // 正在连接中，复用既有握手
      if (this.status === 'connecting') {
        resolve()
        return
      }
      if (!token) {
        reject(new Error('缺少 token'))
        return
      }

      this.currentToken = token
      this.setStatus('connecting')

      const socketTask = uni.connectSocket({
        url: buildWsUrl(token),
        complete: () => {}
      })
      this.socketTask = socketTask

      socketTask.onOpen(() => {
        console.log('[WebSocket] 连接成功')
        this.reconnectAttempts = 0
        this.setStatus('connected')
        resolve()
      })

      socketTask.onMessage((res) => {
        try {
          const message = JSON.parse(res.data as string) as WebSocketMessage
          this.handleMessage(message)
        } catch (error) {
          console.error('[WebSocket] 解析消息失败:', error)
        }
      })

      socketTask.onError(() => {
        console.error('[WebSocket] 连接错误')
        this.setStatus('error')
        reject(new Error('WebSocket 连接错误'))
      })

      socketTask.onClose((res) => {
        console.log('[WebSocket] 连接关闭', res.code, res.reason)
        this.socketTask = null
        this.setStatus('disconnected')
        this.scheduleReconnect(this.currentToken)
      })
    })
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.socketTask) {
      try {
        this.socketTask.close({})
      } catch (error) {
        console.warn('[WebSocket] 关闭连接异常:', error)
      }
      this.socketTask = null
    }
    this.reconnectAttempts = 0
    this.setStatus('disconnected')
  }

  private setStatus(status: ConnectionStatus): void {
    this.status = status
    this.statusListeners.forEach((listener) => listener(status))
  }

  /** 指数退避重连 */
  private scheduleReconnect(token: string): void {
    if (!token) return
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WebSocket] 达到最大重连次数，停止重连')
      return
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    console.log(`[WebSocket] ${delay / 1000}秒后尝试第${this.reconnectAttempts}次重连`)

    this.reconnectTimer = setTimeout(() => {
      this.connect(token).catch(() => {})
    }, delay)
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.handlers.get(message.type)
    if (handlers) {
      handlers.forEach((handler) => handler(message))
    }
    const allHandlers = this.handlers.get('*')
    if (allHandlers) {
      allHandlers.forEach((handler) => handler(message))
    }
  }

  /** 订阅某类型消息，返回取消订阅函数 */
  subscribe<T = unknown>(type: string, handler: MessageHandler<T>): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set())
    }
    this.handlers.get(type)!.add(handler as MessageHandler)

    return () => {
      const handlers = this.handlers.get(type)
      if (handlers) {
        handlers.delete(handler as MessageHandler)
        if (handlers.size === 0) {
          this.handlers.delete(type)
        }
      }
    }
  }

  /** 监听连接状态变化 */
  onStatusChange(listener: (status: ConnectionStatus) => void): () => void {
    this.statusListeners.add(listener)
    listener(this.status)
    return () => {
      this.statusListeners.delete(listener)
    }
  }

  getStatus(): ConnectionStatus {
    return this.status
  }

  isConnected(): boolean {
    return this.status === 'connected'
  }

  /** 主动发送消息，返回是否发送成功 */
  send(message: unknown): boolean {
    if (this.socketTask && this.status === 'connected') {
      this.socketTask.send({ data: JSON.stringify(message) })
      return true
    }
    return false
  }
}

export const wsService = new WebSocketService()

export const WS_MESSAGE_TYPES = {
  WARNING: 'WARNING',
  CHAT: 'CHAT',
  DATA_UPDATE: 'DATA_UPDATE',
  SYSTEM: 'SYSTEM'
} as const

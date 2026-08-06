/**
 * 情绪日记 API（从原项目复用，改用 uni.request 封装）
 * 对应 legacy/frontend/src/api/diary.ts
 */
import { get, post, del } from '@/utils/request'
import type { PageResult, PageParams } from '@/types/api'

/** 日记记录 */
export interface Diary {
  id: number
  emotionType: string
  emotionScore: number
  content: string
  sentimentScore: number
  aiAnalysis: string
  /** 标签（后端可能不返回，前端兜底） */
  tags?: string[]
  createdAt: string
}

/** 创建日记入参 */
export interface DiaryCreate {
  emotionType: string
  emotionScore: number
  content: string
  tags?: string[]
}

/** 日记统计 */
export interface DiaryStatistics {
  totalDiaries: number
  monthlyNew: number
  streak: number
  positiveRate: number
  positiveChange: number
  improvement: number
}

/** 情绪趋势单点 */
export interface EmotionTrendItem {
  date: string
  score: number
}

export function createDiary(data: DiaryCreate): Promise<Diary> {
  return post<Diary>('/diary', data as unknown as Record<string, unknown>)
}

export function getDiaryList(
  params: PageParams & { emotionType?: string }
): Promise<PageResult<Diary>> {
  return get<PageResult<Diary>>(
    '/diary/page',
    params as unknown as Record<string, unknown>
  )
}

export function getDiaryDetail(id: number): Promise<Diary> {
  return get<Diary>(`/diary/${id}`)
}

export function deleteDiary(id: number): Promise<void> {
  return del<void>(`/diary/${id}`)
}

export function getDiaryStatistics(): Promise<DiaryStatistics> {
  return get<DiaryStatistics>('/diary/statistics')
}

export function getEmotionTrend(days: number = 7): Promise<EmotionTrendItem[]> {
  return get<EmotionTrendItem[]>('/diary/trend', { days })
}

/**
 * 首页统计 API（从原项目复用，改用 uni.request 封装）
 * 对应 legacy/frontend/src/api/stats.ts
 */
import { get } from '@/utils/request'

export interface HomeStats {
  userCount: number
  assessmentCount: number
  diaryCount: number
  articleCount: number
  scaleCount: number
}

export function getHomeStats(): Promise<HomeStats> {
  return get<HomeStats>('/stats/home')
}

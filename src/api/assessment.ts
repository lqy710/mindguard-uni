/**
 * 心理测评 API（从原项目复用，改用 uni.request 封装）
 * 对应 legacy/frontend/src/api/assessment.ts
 */
import { get, post } from '@/utils/request'
import type { PageResult, PageParams } from '@/types/api'

export interface Scale {
  id: number
  name: string
  description: string
  category: string
  questionNum: number
  estimatedTime: number
  status: number
  createdAt: string
}

export interface Question {
  id: number
  orderNum: number
  content: string
  options: string
}

export interface ScaleDetail extends Scale {
  questions: Question[]
}

export interface AssessmentResult {
  assessmentId: number
  scaleId: number
  scaleName: string
  totalScore: number
  riskLevel: string
  riskText: string
  createdAt: string
}

export interface SubmitAnswer {
  questionId: number
  answer: number
}

/** 清洗后端可能返回的乱码字符（与原项目保持一致） */
const cleanText = (text: string | undefined): string => {
  if (!text) return ''
  return text
    .replace(/\?/g, '')
    .replace(/[\uFFFD]/g, '')
    .replace(/[\u003F]/g, '')
    .replace(/[^\u4e00-\u9fa5a-zA-Z0-9\s\-_,.!?;:'"()（）【】《》、，。！？；：""''·…—]/g, '')
    .trim()
}

export function getScaleList(category?: string): Promise<Scale[]> {
  return get<Scale[]>('/assessment/scales', { category }).then((data) => {
    return data.map((scale: Scale) => ({
      ...scale,
      name: cleanText(scale.name),
      description: cleanText(scale.description),
      category: cleanText(scale.category)
    }))
  })
}

export function getScaleDetail(scaleId: number): Promise<ScaleDetail> {
  return get<ScaleDetail>(`/assessment/scales/${scaleId}`).then((data) => {
    return {
      ...data,
      name: cleanText(data.name),
      description: cleanText(data.description),
      category: cleanText(data.category),
      questions: data.questions.map((question: Question) => ({
        ...question,
        content: cleanText(question.content),
        options: cleanText(question.options)
      }))
    }
  })
}

export function submitAssessment(
  scaleId: number,
  answers: SubmitAnswer[]
): Promise<AssessmentResult> {
  return post<AssessmentResult>('/assessment/submit', { scaleId, answers })
}

export function getAssessmentHistory(
  params: PageParams
): Promise<PageResult<AssessmentResult>> {
  return get<PageResult<AssessmentResult>>(
    '/assessment/history',
    params as unknown as Record<string, unknown>
  )
}

export function getAssessmentReport(assessmentId: number): Promise<AssessmentResult> {
  return get<AssessmentResult>(`/assessment/report/${assessmentId}`)
}

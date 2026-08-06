/**
 * 知识库 API（从原项目复用，改用 uni.request 封装）
 * 对应 legacy/frontend/src/api/knowledge.ts
 */
import { get, post } from '@/utils/request'
import type { PageResult, PageParams } from '@/types/api'

export interface Article {
  id: number
  categoryId: number
  categoryName: string
  title: string
  summary: string
  coverImage: string
  author: string
  viewCount: number
  likeCount?: number
  commentCount?: number
  readTime?: number
  createdAt: string
}

export interface ArticleDetail extends Article {
  content: string
}

export function getArticleList(
  params: PageParams & { categoryId?: number; keyword?: string }
): Promise<PageResult<Article>> {
  return get<PageResult<Article>>(
    '/knowledge/articles',
    params as unknown as Record<string, unknown>
  )
}

export function getArticleDetail(id: number): Promise<ArticleDetail> {
  return get<ArticleDetail>(`/knowledge/article/${id}`)
}

export function getHotArticles(limit: number = 5): Promise<Article[]> {
  return get<Article[]>('/knowledge/hot', { limit })
}

/** 文章分类 */
export interface ArticleCategory {
  id: number
  name: string
  description: string
  sort: number
  articleCount: number
}

/** RAG 检索命中的知识片段 */
export interface KnowledgeReference {
  /** 命中的文章 id；负数表示 AI 服务内置兜底语料，无对应详情页 */
  articleId: number
  title: string
  category: string
  snippet: string
  /** 相似度 0~1 */
  score: number
}

export interface RetrieveResult {
  query: string
  references: KnowledgeReference[]
}

/** 获取全部文章分类 */
export function getCategories(): Promise<ArticleCategory[]> {
  return get<ArticleCategory[]>('/knowledge/categories')
}

/**
 * 知识库语义检索（RAG）
 * @param query 查询内容
 * @param topK 返回条数，1~10，默认 3
 */
export function retrieveKnowledge(query: string, topK = 3): Promise<RetrieveResult> {
  return post<RetrieveResult>('/knowledge/retrieve', { query, topK })
}

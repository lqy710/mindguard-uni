<template>
  <view class="knowledge-page">
    <!-- 1. 顶部搜索 + 2. 分类筛选（合并为 sticky 头部，一起吸顶） -->
    <view class="header-sticky">
      <!-- 搜索区域 -->
      <view class="search-section">
        <view class="search-box">
          <MIcon class="search-icon" name="search" :size="19" color="#6B645C" />
          <input
            class="search-input"
            :value="keyword"
            placeholder="搜索文章、话题、关键词..."
            placeholder-class="search-placeholder"
            confirm-type="search"
            @input="onSearchInput"
            @confirm="onSearchConfirm"
          />
          <view v-if="keyword" class="clear-btn" @click="clearSearch">
            <MIcon name="x" :size="16" color="#6B645C" />
          </view>
        </view>

        <!-- 热门搜索标签（横向滚动） -->
        <scroll-view scroll-x class="hot-scroll" :show-scrollbar="false">
          <view class="hot-track">
            <text class="hot-label">热门：</text>
            <view
              v-for="tag in hotKeywords"
              :key="tag"
              class="hot-tag"
              @click="searchByKeyword(tag)"
            >
              <text>{{ tag }}</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 分类筛选 -->
      <scroll-view scroll-x class="filter-scroll" :show-scrollbar="false">
        <view class="filter-track">
          <view
            v-for="cat in categories"
            :key="cat.value"
            class="filter-tag"
            :class="{ active: activeCategory === cat.value }"
            @click="switchCategory(cat.value)"
          >
            <text>{{ cat.label }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 3. 文章列表 -->
    <view class="article-list">
      <!-- 首次加载骨架屏 -->
      <template v-if="initialLoading">
        <view v-for="i in 3" :key="'sk' + i" class="skeleton-card">
          <view class="skeleton-cover"></view>
          <view class="skeleton-body">
            <view class="skeleton-line short"></view>
            <view class="skeleton-line"></view>
            <view class="skeleton-line long"></view>
          </view>
        </view>
      </template>

      <template v-else>
        <!-- 文章卡片 -->
        <view
          v-for="article in articles"
          :key="article.id"
          class="article-card"
          @click="goDetail(article.id)"
        >
          <!-- 有封面：左图右文 -->
          <view v-if="article.coverImage" class="card-main">
            <image
              class="card-cover"
              :src="article.coverImage"
              mode="aspectFill"
            />
            <view class="card-content">
              <view class="card-cat" :style="{ background: getCategoryColor(article.categoryId) }">
                <text class="card-cat-text">{{ article.categoryName }}</text>
              </view>
              <text class="card-title text-clamp-2">{{ article.title }}</text>
              <view class="card-meta">
                <view class="meta-item">
                  <MIcon name="clock" :size="18" color="#6B645C" />
                  <text>{{ article.readTime ?? 5 }}分钟</text>
                </view>
                <view class="meta-item">
                  <MIcon name="eye" :size="18" color="#6B645C" />
                  <text>{{ formatCount(article.viewCount) }}</text>
                </view>
                <view class="meta-item">
                  <MIcon name="heart" :size="18" color="#6B645C" />
                  <text>{{ formatCount(article.likeCount ?? 0) }}</text>
                </view>
              </view>
            </view>
          </view>

          <!-- 无封面：纯文字卡片 -->
          <view v-else class="card-text-only">
            <view class="card-cat" :style="{ background: getCategoryColor(article.categoryId) }">
              <text class="card-cat-text">{{ article.categoryName }}</text>
            </view>
            <text class="card-title text-clamp-2">{{ article.title }}</text>
            <text class="card-summary text-clamp-2">{{ article.summary }}</text>
            <view class="card-meta">
              <view class="meta-item">
                <MIcon name="clock" :size="18" color="#6B645C" />
                <text>{{ article.readTime ?? 5 }}分钟</text>
              </view>
              <view class="meta-item">
                <MIcon name="eye" :size="18" color="#6B645C" />
                <text>{{ formatCount(article.viewCount) }}</text>
              </view>
              <view class="meta-item">
                <MIcon name="heart" :size="18" color="#6B645C" />
                <text>{{ formatCount(article.likeCount ?? 0) }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 空状态 -->
        <view v-if="!loading && !articles.length" class="empty-state">
          <MIcon class="empty-emoji" name="file-text" :size="32" color="#6B645C" />
          <text class="empty-text">暂无相关文章</text>
        </view>

        <!-- 触底加载 -->
        <view v-if="loading && articles.length" class="loading-tip">
          <view class="loading-dot"></view>
          <text class="loading-text">加载中...</text>
        </view>
        <view v-if="!loading && articles.length && !hasMore" class="loading-tip">
          <text class="loading-text">— 已经到底啦 —</text>
        </view>
      </template>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShow, onReachBottom, onUnload } from '@dcloudio/uni-app'
import { getArticleList, type Article } from '@/api/knowledge'
import { useUserStore } from '@/stores/user'
import MIcon from '@/components/MIcon.vue'

const userStore = useUserStore()

const PAGE_SIZE = 10

// ===== 状态 =====
const keyword = ref('')
const activeCategory = ref('all')
const articles = ref<Article[]>([])
const currentPage = ref(1)
const hasMore = ref(true)
const loading = ref(false)
const initialLoading = ref(true)

// 搜索防抖定时器
let searchTimer: ReturnType<typeof setTimeout> | null = null

// 热门搜索关键词
const hotKeywords = ['焦虑', '抑郁', '压力', '睡眠', '人际关系', '正念']

// 分类列表（value 与后端 categoryId 对应）
const categories = [
  { label: '全部', value: 'all' },
  { label: '焦虑', value: 'anxiety' },
  { label: '抑郁', value: 'depression' },
  { label: '压力', value: 'stress' },
  { label: '情绪管理', value: 'emotion' },
  { label: '人际关系', value: 'relationship' },
  { label: '个人成长', value: 'growth' }
]

// 分类 value → 后端 categoryId 映射（沿用原项目 categoryMap）
const CATEGORY_ID_MAP: Record<string, number> = {
  anxiety: 1,
  depression: 2,
  stress: 3,
  relationship: 4,
  growth: 5,
  emotion: 6
}

// 卡片分类标签配色（按 categoryId 取色，使用新设计令牌）
const CATEGORY_COLOR: Record<number, string> = {
  1: '#C26B4F', // 焦虑-coral
  2: '#6B5B9E', // 抑郁-lavender
  3: '#B8862F', // 压力-amber
  4: '#4A7C6F', // 人际关系-sage
  5: '#3A6359', // 个人成长-sage-deep
  6: '#C26B4F'  // 情绪管理-coral
}
const MAIN_COLOR = '#3A6359'

// 兜底封面（本地占位，避免接口失败时加载远程图超时断网）
// 上线前如有服务器图床，替换为真实封面 URL 即可
const COVER_ANXIETY = '/static/logo.png'
const COVER_FOREST = '/static/logo.png'
const COVER_GROWTH = '/static/logo.png'

// 兜底文章（接口失败时使用，保证页面非空，同时演示有图/无图两种布局）
const DEFAULT_ARTICLES: Article[] = [
  { id: 1, categoryId: 1, categoryName: '焦虑', title: '当你感到焦虑时：5 个快速平复情绪的呼吸法', summary: '焦虑来袭时，简单的呼吸调节能帮你在几分钟内找回平静。本文介绍 5 种实用呼吸技巧。', coverImage: COVER_ANXIETY, author: 'MindGuard', viewCount: 2356, likeCount: 156, commentCount: 23, readTime: 5, createdAt: '2026-07-28 10:00:00' },
  { id: 2, categoryId: 2, categoryName: '抑郁', title: '抑郁情绪不是软弱：科学认识它，温柔对待自己', summary: '抑郁是一种常见的情绪信号，并非意志薄弱。理解它的成因，是自我关怀的第一步。', coverImage: '', author: 'MindGuard', viewCount: 1892, likeCount: 203, commentCount: 41, readTime: 7, createdAt: '2026-07-26 15:30:00' },
  { id: 3, categoryId: 4, categoryName: '人际关系', title: '人际边界感：如何在亲密关系中保持自我', summary: '好的关系不是融为一体，而是两个独立个体的相互尊重。聊聊如何建立健康的边界。', coverImage: COVER_FOREST, author: 'MindGuard', viewCount: 1567, likeCount: 98, commentCount: 19, readTime: 6, createdAt: '2026-07-24 09:20:00' },
  { id: 4, categoryId: 3, categoryName: '压力', title: '高压时代下的自我松绑：给身心留白的方法', summary: '持续的高压会消耗心理资源。学会主动留白，让紧绷的神经得到真正的休息。', coverImage: '', author: 'MindGuard', viewCount: 1234, likeCount: 87, commentCount: 15, readTime: 5, createdAt: '2026-07-22 14:10:00' },
  { id: 5, categoryId: 5, categoryName: '个人成长', title: '从自我接纳开始：建立可持续的成长心态', summary: '成长不必苛责自己。接纳当下，才能蓄积持续向前的力量。', coverImage: COVER_GROWTH, author: 'MindGuard', viewCount: 987, likeCount: 134, commentCount: 22, readTime: 6, createdAt: '2026-07-20 11:00:00' }
]

// ===== 工具函数 =====
function getCategoryColor(categoryId: number): string {
  return CATEGORY_COLOR[categoryId] || MAIN_COLOR
}

/** 格式化阅读/点赞数：>=1000 显示为 x.xk */
function formatCount(n: number): string {
  if (n >= 1000) {
    return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k'
  }
  return String(n)
}

// ===== 数据加载 =====
/** 重置分页并拉取第一页（搜索/分类切换/清除时调用） */
function resetAndLoad(): void {
  currentPage.value = 1
  hasMore.value = true
  loadArticles(true)
}

async function loadArticles(reset = false): Promise<void> {
  if (loading.value) return
  if (!hasMore.value && !reset) return
  loading.value = true
  try {
    const categoryId =
      activeCategory.value !== 'all' ? CATEGORY_ID_MAP[activeCategory.value] : undefined
    const res = await getArticleList({
      current: currentPage.value,
      size: PAGE_SIZE,
      keyword: keyword.value.trim() || undefined,
      categoryId
    })
    const records = res?.records || []
    articles.value = reset ? records : [...articles.value, ...records]
    hasMore.value = articles.value.length < (res?.total || 0)
  } catch (error) {
    console.error('加载文章列表失败:', error)
    // 接口失败：首次加载用兜底数据演示，保证页面非空
    if (reset && !articles.value.length) {
      articles.value = DEFAULT_ARTICLES
      hasMore.value = false
    }
  } finally {
    loading.value = false
    initialLoading.value = false
  }
}

// ===== 搜索交互（防抖 500ms） =====
function onSearchInput(e: InputEvent): void {
  // uni-app InputEvent.detail 类型宽松，按 input 实际结构取 value
  const value = (e.detail as unknown as { value: string }).value
  keyword.value = value
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(resetAndLoad, 500)
}

/** 键盘"搜索"按钮：立即触发，跳过防抖等待 */
function onSearchConfirm(): void {
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
  resetAndLoad()
}

/** 点击热门标签：立即搜索 */
function searchByKeyword(kw: string): void {
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
  keyword.value = kw
  resetAndLoad()
}

/** 清除搜索词并重新加载 */
function clearSearch(): void {
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
  keyword.value = ''
  resetAndLoad()
}

function switchCategory(value: string): void {
  if (activeCategory.value === value) return
  activeCategory.value = value
  resetAndLoad()
}

// 防止快速双击重复入栈
let navigating = false
function goDetail(id: number): void {
  if (navigating) return
  navigating = true
  uni.navigateTo({
    url: `/pages/knowledge/detail?id=${id}`,
    complete: () => {
      setTimeout(() => {
        navigating = false
      }, 400)
    }
  })
}

// ===== 生命周期 =====
onLoad(() => {
  loadArticles(true)
})

onShow(() => {
  // 登录守卫：未登录跳转登录页
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
})

onReachBottom(() => {
  if (loading.value || !hasMore.value) return
  currentPage.value++
  loadArticles(false)
})

onUnload(() => {
  // 清理防抖定时器，避免内存泄漏
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
})
</script>

<style scoped>
.knowledge-page {
  min-height: 100vh;
  background: #EDE9E1;
  padding-bottom: calc(80rpx + env(safe-area-inset-bottom));
}

/* 顶部 sticky 头部（搜索 + 分类一起吸顶） */
.header-sticky {
  position: sticky;
  top: 0;
  z-index: 20;
  background: #FBFAF6;
  border-bottom: 2rpx solid #E2DDD2;
}

/* 搜索区域 */
.search-section {
  padding: 20rpx 32rpx 16rpx;
}

.search-box {
  display: flex;
  align-items: center;
  background: #F2EFE8;
  border: 2rpx solid #E2DDD2;
  border-radius: 999rpx;
  padding: 0 24rpx;
  height: 72rpx;
}

.search-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  min-width: 0;
  height: 72rpx;
  font-size: 28rpx;
  color: #2A2722;
}

.search-placeholder {
  color: #6B645C;
  font-size: 28rpx;
}

.clear-btn {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #E2DDD2;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-left: 12rpx;
}

/* 热门搜索 */
.hot-scroll {
  width: 100%;
  white-space: nowrap;
  margin-top: 16rpx;
}

.hot-track {
  display: inline-flex;
  align-items: center;
  padding: 4rpx 0;
  gap: 12rpx;
}

.hot-label {
  font-size: 24rpx;
  color: #6B645C;
  flex-shrink: 0;
}

.hot-tag {
  flex-shrink: 0;
  padding: 8rpx 20rpx;
  background: #E6EEEA;
  border-radius: 999rpx;
  font-size: 24rpx;
  color: #3A6359;
}

/* 分类筛选 */
.filter-scroll {
  width: 100%;
  white-space: nowrap;
  border-top: 2rpx solid #F2EFE8;
}

.filter-track {
  display: inline-flex;
  align-items: center;
  padding: 20rpx 32rpx;
  gap: 16rpx;
}

.filter-tag {
  flex-shrink: 0;
  padding: 12rpx 28rpx;
  border-radius: 999rpx;
  background: #F2EFE8;
  font-size: 26rpx;
  color: #6B645C;
  transition: all 0.25s ease;
}

.filter-tag.active {
  background: #3A6359;
  color: #FBFAF6;
}

/* 文章列表 */
.article-list {
  padding: 24rpx 32rpx 0;
}

.article-card {
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}

.card-main {
  display: flex;
  align-items: flex-start;
}

.card-cover {
  width: 200rpx;
  height: 140rpx;
  border-radius: 16rpx;
  flex-shrink: 0;
  background: #F2EFE8;
}

.card-content {
  flex: 1;
  min-width: 0;
  margin-left: 20rpx;
  display: flex;
  flex-direction: column;
}

.card-text-only {
  display: flex;
  flex-direction: column;
}

.card-cat {
  align-self: flex-start;
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  margin-bottom: 12rpx;
}

.card-cat-text {
  font-size: 22rpx;
  color: #FBFAF6;
  font-weight: 500;
}

.card-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #2A2722;
  line-height: 1.4;
}

.card-summary {
  font-size: 26rpx;
  color: #6B645C;
  line-height: 1.5;
  margin-top: 8rpx;
}

.card-meta {
  display: flex;
  gap: 20rpx;
  margin-top: 16rpx;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #6B645C;
}

/* 骨架屏 */
.skeleton-card {
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  display: flex;
  align-items: flex-start;
}

.skeleton-cover {
  width: 200rpx;
  height: 140rpx;
  border-radius: 16rpx;
  background: #F2EFE8;
  flex-shrink: 0;
}

.skeleton-body {
  flex: 1;
  margin-left: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding-top: 8rpx;
}

.skeleton-line {
  height: 24rpx;
  border-radius: 12rpx;
  background: #F2EFE8;
}

.skeleton-line.short {
  width: 120rpx;
  height: 20rpx;
}

.skeleton-line.long {
  width: 60%;
}

@keyframes skeleton-pulse {
  0% { opacity: 0.55; }
  50% { opacity: 1; }
  100% { opacity: 0.55; }
}

.skeleton-cover,
.skeleton-line {
  animation: skeleton-pulse 1.4s ease-in-out infinite;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;
}

.empty-emoji {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #6B645C;
}

/* 加载提示 */
.loading-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 32rpx 0;
}

.loading-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #4A7C6F;
  animation: dot-blink 1s ease-in-out infinite;
}

@keyframes dot-blink {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}

.loading-text {
  font-size: 24rpx;
  color: #6B645C;
}

/* 通用：两行截断 */
.text-clamp-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 隐藏横向滚动条（H5 兜底，小程序用 show-scrollbar="false"） */
.hot-scroll ::-webkit-scrollbar,
.filter-scroll ::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}
</style>

<template>
  <view class="detail-page">
    <!-- 1. 自定义导航栏：返回 + 标题 + 收藏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-row" :style="{ height: navBarHeight + 'px', paddingRight: navPadRight + 'px' }">
        <view class="nav-back" @click="onBack">
          <view class="back-arrow"></view>
        </view>
        <text class="nav-title">心理知识</text>
        <view class="nav-fav" @click="toggleFav">
          <MIcon
            class="nav-fav-icon"
            :class="{ active: isFavorited }"
            name="star"
            :size="22"
            :color="isFavorited ? '#B8862F' : '#6B645C'"
          />
        </view>
      </view>
    </view>

    <!-- 占位：状态栏 + 导航栏高度，避免内容被导航栏遮挡 -->
    <view class="nav-placeholder" :style="{ height: (statusBarHeight + navBarHeight) + 'px' }"></view>

    <!-- 加载骨架 -->
    <view v-if="loading" class="skeleton">
      <view class="sk-line short"></view>
      <view class="sk-line long"></view>
      <view class="sk-block"></view>
      <view class="sk-line"></view>
      <view class="sk-line"></view>
      <view class="sk-line long"></view>
    </view>

    <!-- 文章内容 -->
    <template v-else-if="article">
      <view class="article-wrap">
        <!-- 2. 文章头部 -->
        <view class="art-header">
          <view class="art-cat" :style="{ background: getCategoryColor(article.categoryId) }">
            <text class="art-cat-text">{{ article.categoryName || '心理知识' }}</text>
          </view>
          <text class="art-title">{{ article.title }}</text>

          <view class="author-row">
            <view class="author-avatar">
              <text class="author-initial">{{ getAuthorInitial(article.author) }}</text>
            </view>
            <view class="author-info">
              <text class="author-name">{{ article.author || '心理师' }}</text>
              <text class="author-date">{{ formatDate(article.createdAt) }}</text>
            </view>
          </view>

          <view class="stats-row">
            <view class="stat-item">
              <MIcon name="eye" :size="18" color="#6B645C" />
              <text>{{ formatCount(article.viewCount) }} 阅读</text>
            </view>
            <text class="stat-divider">|</text>
            <view class="stat-item">
              <MIcon name="clock" :size="18" color="#6B645C" />
              <text>{{ article.readTime ?? 5 }} 分钟阅读</text>
            </view>
          </view>
        </view>

        <!-- 3. 封面图 -->
        <view v-if="article.coverImage" class="art-cover">
          <image
            class="cover-img"
            :src="article.coverImage"
            mode="aspectFill"
          />
        </view>

        <!-- 4. 文章正文 -->
        <view class="art-body">
          <view v-if="article.summary" class="art-lead">
            <text class="art-lead-text">{{ article.summary }}</text>
          </view>
          <rich-text class="art-content" :nodes="contentNodes"></rich-text>
        </view>
      </view>

      <!-- 6. 相关推荐 -->
      <view class="related-section">
        <view class="related-title">
          <MIcon name="notebook-pen" :size="20" color="#2A2722" />
          <text>相关推荐</text>
        </view>
        <view
          v-for="item in related"
          :key="item.id"
          class="related-card"
          @click="goRelated(item.id)"
        >
          <view class="related-cat" :style="{ background: getCategoryColor(item.categoryId) }">
            <text class="related-cat-text">{{ item.categoryName }}</text>
          </view>
          <text class="related-card-title text-clamp-2">{{ item.title }}</text>
          <text class="related-arrow">></text>
        </view>
      </view>

      <!-- 底部留白，避免被固定操作栏遮挡 -->
      <view class="bottom-spacer"></view>
    </template>

    <!-- 空状态 -->
    <view v-else class="empty-state">
      <MIcon class="empty-emoji" name="file-text" :size="32" color="#6B645C" />
      <text class="empty-text">文章加载失败</text>
    </view>

    <!-- 5. 底部固定操作栏 -->
    <view v-if="article && !loading" class="bottom-bar">
      <view class="bar-left">
        <view class="bar-btn" @click="toggleLike">
          <MIcon class="bar-icon" :class="{ active: isLiked }" name="thumbs-up" :size="19" :color="isLiked ? '#C26B4F' : '#6B645C'" />
          <text class="bar-count">{{ formatCount(likeCount) }}</text>
        </view>
        <view class="bar-btn" @click="toggleFav">
          <MIcon class="bar-icon" :class="{ active: isFavorited }" name="star" :size="19" :color="isFavorited ? '#B8862F' : '#6B645C'" />
          <text class="bar-text">{{ isFavorited ? '已收藏' : '收藏' }}</text>
        </view>
      </view>
      <!-- 分享：小程序用 button open-type="share" 触发原生分享；其他端用点击复制链接 -->
      <!-- #ifdef MP -->
      <button class="bar-share" open-type="share">分享</button>
      <!-- #endif -->
      <!-- #ifndef MP -->
      <view class="bar-share" @click="onShareClick">分享</view>
      <!-- #endif -->
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad, onUnload, onShareAppMessage, onShareTimeline } from '@dcloudio/uni-app'
import { getArticleDetail, getArticleList, type ArticleDetail } from '@/api/knowledge'
import MIcon from '@/components/MIcon.vue'

// ===== 相关推荐条目类型 =====
interface RelatedArticle {
  id: number
  title: string
  categoryName: string
  categoryId: number
}

// ===== 分类配色（与 list.vue 保持一致，使用新设计令牌） =====
const CATEGORY_COLOR: Record<number, string> = {
  1: '#C26B4F', // 焦虑-coral
  2: '#6B5B9E', // 抑郁-lavender
  3: '#B8862F', // 压力-amber
  4: '#4A7C6F', // 人际关系-sage
  5: '#3A6359', // 个人成长-sage-deep
  6: '#C26B4F'  // 情绪管理-coral
}
const MAIN_COLOR = '#3A6359'
function getCategoryColor(id: number): string {
  return CATEGORY_COLOR[id] || MAIN_COLOR
}

// ===== 收藏 / 点赞本地持久化（uni.getStorageSync） =====
const FAV_KEY = 'mg_article_fav_ids'
const LIKE_KEY = 'mg_article_like_ids'

function readIds(key: string): number[] {
  try {
    const v = uni.getStorageSync(key)
    return Array.isArray(v) ? (v as number[]) : []
  } catch {
    return []
  }
}
function writeIds(key: string, ids: number[]): void {
  try {
    uni.setStorageSync(key, ids)
  } catch {
    /* 忽略写入失败 */
  }
}
/** 切换某 id 的存在状态，返回切换后是否为「已加入」 */
function toggleId(key: string, id: number): boolean {
  const ids = readIds(key)
  const idx = ids.indexOf(id)
  let added: boolean
  if (idx >= 0) {
    ids.splice(idx, 1)
    added = false
  } else {
    ids.push(id)
    added = true
  }
  writeIds(key, ids)
  return added
}

// ===== 状态 =====
const statusBarHeight = ref(0)
const navBarHeight = ref(44) // px，默认导航栏内容高度
const navPadRight = ref(16) // px，右侧内边距（MP 预留胶囊空间）
const loading = ref(true)
const article = ref<ArticleDetail | null>(null)
const related = ref<RelatedArticle[]>([])
const isFavorited = ref(false)
const isLiked = ref(false)
const likeCount = ref(0)
const articleId = ref(0)

// 防止快速双击重复入栈
let navigating = false

// 兜底封面（本地占位，避免接口失败时加载远程图超时断网）
// 上线前如有服务器图床，替换为真实封面 URL 即可
const FALLBACK_COVER = '/static/logo.png'

// 兜底文章详情（接口失败时使用，保证页面非空）
const FALLBACK_ARTICLE: ArticleDetail = {
  id: 0,
  categoryId: 1,
  categoryName: '焦虑',
  title: '当你感到焦虑时：5 个快速平复情绪的呼吸法',
  summary: '焦虑来袭时，简单的呼吸调节能帮你在几分钟内找回平静。本文介绍 5 种实用呼吸技巧。',
  coverImage: FALLBACK_COVER,
  author: 'MindGuard',
  viewCount: 2356,
  likeCount: 156,
  commentCount: 23,
  readTime: 5,
  createdAt: '2026-07-28 10:00:00',
  content: `<p>焦虑是身体面对压力时的自然反应，但当它过度涌现，会影响日常生活。以下是 5 种经过验证的快速呼吸法，帮助你在几分钟内平复情绪。</p>
<h2>1. 4-7-8 呼吸法</h2>
<p>用鼻子吸气 4 秒，屏息 7 秒，再用嘴缓慢呼气 8 秒，重复 4 个循环。这个方法能激活副交感神经，迅速降低心率。</p>
<h2>2. 腹式呼吸</h2>
<p>一手放胸口、一手放腹部，吸气时腹部鼓起，呼气时收缩。每天练习 5 分钟，长期可降低基础焦虑水平。</p>
<blockquote>小贴士：练习时闭眼，想象一个安全的场景，效果会更好。</blockquote>
<h2>3. 箱式呼吸</h2>
<p>吸气 4 秒、屏息 4 秒、呼气 4 秒、屏息 4 秒，像方盒子的四个边。许多高压职业人群都在用这个方法。</p>
<h2>4. 数数呼吸</h2>
<p>缓慢吸气时默数到 6，呼气时默数到 6。专注在数字上，能打断焦虑的思绪循环。</p>
<h2>5. 叹气呼吸</h2>
<p>深吸一口气，再补吸一小口，然后长长地呼出。重复 3 次，能缓解胸闷感。</p>
<p>记住，呼吸法是工具而非万能解药。如果焦虑持续影响生活，请主动寻求专业帮助。</p>`
}

// 兜底相关推荐
const FALLBACK_RELATED: RelatedArticle[] = [
  { id: 2, title: '抑郁情绪不是软弱：科学认识它，温柔对待自己', categoryName: '抑郁', categoryId: 2 },
  { id: 3, title: '人际边界感：如何在亲密关系中保持自我', categoryName: '人际关系', categoryId: 4 },
  { id: 4, title: '高压时代下的自我松绑：给身心留白的方法', categoryName: '压力', categoryId: 3 }
]

// ===== 工具函数 =====
/** 格式化数量：>=1000 显示为 x.xk */
function formatCount(n: number): string {
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k'
  return String(n)
}
/** 格式化日期：取 YYYY-MM-DD */
function formatDate(s: string): string {
  if (!s) return ''
  return s.length >= 10 ? s.slice(0, 10) : s
}
function getAuthorInitial(name?: string): string {
  return name ? name.charAt(0) : '心'
}

/**
 * 预处理文章 HTML：注入内联样式。
 * 原因：rich-text 在小程序端不继承外部 CSS，只能靠节点内联样式控制排版。
 */
function processContent(html: string): string {
  if (!html) return ''
  let s = html
  // 规范化图片：保证自适应宽度 + 圆角
  s = s.replace(/<img([^>]*)>/gi, (_m, attrs: string) => {
    if (/style\s*=/i.test(attrs)) {
      return `<img${attrs.replace(/style="([^"]*)"/i, (_mm, st: string) =>
        `style="${st.replace(/max-width\s*:[^;]+;?/gi, '').replace(/height\s*:\s*\d+(px|rpx)?;?/gi, '')};max-width:100%;height:auto;border-radius:16rpx;"`
      )}>`
    }
    return `<img${attrs} style="max-width:100%;height:auto;border-radius:16rpx;">`
  })
  // 包裹基础排版样式（字号 30rpx，行高 1.8）
  return `<div style="font-size:30rpx;line-height:1.8;color:#4A453E;word-break:break-word;">${s}</div>`
}
const contentNodes = computed(() => processContent(article.value?.content || ''))

// ===== 交互 =====
function onBack(): void {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    uni.redirectTo({ url: '/pages/knowledge/list' })
  }
}

function toggleFav(): void {
  if (!articleId.value) return
  isFavorited.value = toggleId(FAV_KEY, articleId.value)
  uni.showToast({ title: isFavorited.value ? '已收藏' : '已取消收藏', icon: 'none' })
}

function toggleLike(): void {
  if (!articleId.value) return
  isLiked.value = toggleId(LIKE_KEY, articleId.value)
  likeCount.value += isLiked.value ? 1 : -1
  if (likeCount.value < 0) likeCount.value = 0
}

/** 非小程序端的分享：复制链接到剪贴板 */
function onShareClick(): void {
  // #ifndef MP
  const g = globalThis as unknown as {
    location?: { href: string }
    navigator?: { clipboard?: { writeText(t: string): Promise<void> } }
  }
  const url = g.location?.href || ''
  if (g.navigator?.clipboard) {
    g.navigator.clipboard.writeText(url).then(
      () => uni.showToast({ title: '链接已复制', icon: 'success' }),
      () => uni.showToast({ title: '复制失败，请手动复制', icon: 'none' })
    )
  } else {
    uni.showToast({ title: '请使用浏览器菜单分享', icon: 'none' })
  }
  // #endif
}

function goRelated(id: number): void {
  if (navigating) return
  if (id === articleId.value) return
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

// ===== 数据加载 =====
async function loadArticle(id: number): Promise<void> {
  loading.value = true
  try {
    const data = await getArticleDetail(id)
    if (!data) throw new Error('文章不存在')
    article.value = data
  } catch (err) {
    console.error('加载文章详情失败:', err)
    // 兜底：用本地数据保证页面非空
    article.value = { ...FALLBACK_ARTICLE, id }
  } finally {
    loading.value = false
    if (article.value) {
      const aid = article.value.id
      isFavorited.value = readIds(FAV_KEY).includes(aid)
      const liked = readIds(LIKE_KEY).includes(aid)
      isLiked.value = liked
      likeCount.value = (article.value.likeCount ?? 0) + (liked ? 1 : 0)
    }
  }
}

async function loadRelated(id: number): Promise<void> {
  try {
    const res = await getArticleList({ current: 1, size: 6 })
    const records = res?.records || []
    const list = records
      .filter(a => a.id !== id)
      .slice(0, 3)
      .map(a => ({
        id: a.id,
        title: a.title,
        categoryName: a.categoryName,
        categoryId: a.categoryId
      }))
    related.value = list.length ? list : FALLBACK_RELATED.filter(r => r.id !== id).slice(0, 3)
  } catch (err) {
    console.error('加载相关推荐失败:', err)
    related.value = FALLBACK_RELATED.filter(r => r.id !== id).slice(0, 3)
  }
}

// ===== 生命周期 =====
onLoad((options) => {
  // 状态栏高度
  let screenWidth = 375
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 0
    screenWidth = sys.screenWidth || 375
  } catch {
    /* 忽略 */
  }
  // #ifdef MP-WEIXIN
  // 适配胶囊按钮：导航栏内容高度与右侧预留空间
  try {
    const menu = uni.getMenuButtonBoundingClientRect()
    navBarHeight.value = (menu.top - statusBarHeight.value) * 2 + menu.height
    navPadRight.value = screenWidth - menu.left + 8
  } catch {
    /* 忽略 */
  }
  // #endif

  const id = Number(options?.id)
  if (!id || Number.isNaN(id)) {
    uni.showToast({ title: '参数错误', icon: 'none' })
    setTimeout(onBack, 600)
    return
  }
  articleId.value = id
  loadArticle(id)
  loadRelated(id)
})

onUnload(() => {
  navigating = false
})

// 小程序：转发分享
onShareAppMessage(() => ({
  title: article.value?.title || '心理知识',
  path: `/pages/knowledge/detail?id=${articleId.value}`,
  imageUrl: article.value?.coverImage || ''
}))

// 小程序：分享到朋友圈
onShareTimeline(() => ({
  title: article.value?.title || '心理知识',
  query: `id=${articleId.value}`
}))
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #EDE9E1;
}

/* ===== 自定义导航栏 ===== */
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #FBFAF6;
  border-bottom: 2rpx solid #E2DDD2;
}
.nav-row {
  display: flex;
  align-items: center;
  position: relative;
}
.nav-back {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.back-arrow {
  width: 20rpx;
  height: 20rpx;
  border-left: 4rpx solid #2A2722;
  border-bottom: 4rpx solid #2A2722;
  transform: rotate(45deg);
  margin-left: 8rpx;
}
.nav-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 34rpx;
  font-weight: 600;
  color: #2A2722;
}
.nav-fav {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-left: auto;
}
.nav-fav-icon {
  font-size: 40rpx;
  color: #6B645C;
  line-height: 1;
}
.nav-fav-icon.active {
  color: #B8862F;
}
.nav-placeholder {
  width: 100%;
}

/* ===== 骨架屏 ===== */
.skeleton {
  padding: 40rpx 32rpx;
}
.sk-line {
  height: 28rpx;
  border-radius: 14rpx;
  background: #F2EFE8;
  margin-bottom: 24rpx;
}
.sk-line.short { width: 140rpx; }
.sk-line.long { width: 80%; }
.sk-block {
  height: 360rpx;
  border-radius: 16rpx;
  background: #F2EFE8;
  margin: 24rpx 0 32rpx;
}
@keyframes sk-pulse {
  0% { opacity: 0.55; }
  50% { opacity: 1; }
  100% { opacity: 0.55; }
}
.sk-line, .sk-block { animation: sk-pulse 1.4s ease-in-out infinite; }

/* ===== 文章主体 ===== */
.article-wrap {
  background: #FBFAF6;
  padding: 8rpx 0 16rpx;
}
.art-header {
  padding: 24rpx 32rpx 20rpx;
}
.art-cat {
  align-self: flex-start;
  display: inline-flex;
  padding: 6rpx 18rpx;
  border-radius: 999rpx;
  margin-bottom: 20rpx;
}
.art-cat-text {
  font-size: 22rpx;
  color: #FBFAF6;
  font-weight: 500;
  line-height: 1.4;
}
.art-title {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
  color: #2A2722;
  line-height: 1.4;
  margin-bottom: 24rpx;
}
.author-row {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}
.author-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #E6EEEA;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 16rpx;
}
.author-initial {
  font-size: 28rpx;
  color: #3A6359;
  font-weight: 600;
}
.author-info {
  display: flex;
  flex-direction: column;
}
.author-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #2A2722;
  line-height: 1.4;
}
.author-date {
  font-size: 22rpx;
  color: #6B645C;
  line-height: 1.4;
  margin-top: 2rpx;
}
.stats-row {
  display: flex;
  align-items: center;
}
.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  font-size: 24rpx;
  color: #6B645C;
}
.stat-divider {
  font-size: 24rpx;
  color: #E2DDD2;
  margin: 0 16rpx;
}

/* 封面图 */
.art-cover {
  padding: 8rpx 32rpx 24rpx;
}
.cover-img {
  width: 100%;
  height: 360rpx;
  border-radius: 16rpx;
  background: #F2EFE8;
}

/* 正文 */
.art-body {
  padding: 0 32rpx 32rpx;
}
.art-lead {
  padding: 20rpx 24rpx;
  background: #E6EEEA;
  border-left: 6rpx solid #3A6359;
  border-radius: 0 16rpx 16rpx 0;
  margin-bottom: 24rpx;
}
.art-lead-text {
  font-size: 28rpx;
  line-height: 1.7;
  color: #4A453E;
}
.art-content {
  width: 100%;
}

/* ===== 相关推荐 ===== */
.related-section {
  margin-top: 24rpx;
  padding: 32rpx;
  background: #FBFAF6;
}
.related-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 32rpx;
  font-weight: 700;
  color: #2A2722;
  margin-bottom: 24rpx;
}
.related-card {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 2rpx solid #E2DDD2;
}
.related-card:last-child {
  border-bottom: none;
}
.related-cat {
  flex-shrink: 0;
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  margin-right: 16rpx;
}
.related-cat-text {
  font-size: 20rpx;
  color: #FBFAF6;
  font-weight: 500;
}
.related-card-title {
  flex: 1;
  min-width: 0;
  font-size: 28rpx;
  color: #2A2722;
  line-height: 1.4;
}
.related-arrow {
  font-size: 32rpx;
  color: #6B645C;
  margin-left: 12rpx;
  flex-shrink: 0;
}

/* ===== 底部留白 + 空状态 ===== */
.bottom-spacer {
  height: calc(140rpx + env(safe-area-inset-bottom));
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 160rpx 0;
}
.empty-emoji {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}
.empty-text {
  font-size: 28rpx;
  color: #6B645C;
}

/* ===== 固定底部操作栏 ===== */
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 90;
  display: flex;
  align-items: center;
  padding: 16rpx 32rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #FBFAF6;
  border-top: 2rpx solid #E2DDD2;
}
.bar-left {
  display: flex;
  align-items: center;
  gap: 24rpx;
  flex: 1;
}
.bar-btn {
  display: flex;
  align-items: center;
  height: 72rpx;
  padding: 0 20rpx;
  border-radius: 999rpx;
  background: #F2EFE8;
}
.bar-icon {
  font-size: 28rpx;
  line-height: 1;
  margin-right: 8rpx;
}
.bar-icon.active {
  transform: scale(1.05);
}
.bar-count {
  font-size: 24rpx;
  color: #6B645C;
}
.bar-text {
  font-size: 24rpx;
  color: #6B645C;
}
.bar-share {
  height: 72rpx;
  line-height: 72rpx;
  padding: 0 40rpx;
  border-radius: 999rpx;
  background: #3A6359;
  color: #FBFAF6;
  font-size: 28rpx;
  font-weight: 600;
  text-align: center;
  border: none;
}
/* button 元素在 MP 下有默认边框，需重置 */
.bar-share::after {
  border: none;
}

/* 通用：两行截断 */
.text-clamp-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

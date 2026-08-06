<template>
  <view class="assessment-page">
    <!-- 1. 页面头部：标题 + 搜索按钮 -->
    <view class="page-header">
      <text class="page-title">心理测评</text>
      <view class="icon-btn" @tap="onSearch">
        <MIcon name="search" :size="20" color="#4A453E" />
      </view>
    </view>

    <!-- 2. 进行中测评 banner -->
    <view
      v-if="featuredScale"
      class="assess-banner"
      @tap="goDetail(featuredScale.id)"
    >
      <view class="assess-banner-top">
        <view class="assess-banner-icon">
          <MIcon name="clipboard-check" :size="22" color="#3A6359" />
        </view>
        <text class="assess-banner-title">{{ featuredScale.name }}</text>
      </view>
      <text class="assess-banner-desc">
        已完成 {{ featuredCompleted }}/{{ featuredScale.questionNum }} 题，继续完成评估
      </text>
      <view class="assess-progress">
        <view class="assess-progress-bar" :style="{ width: featuredProgress }"></view>
      </view>
      <text class="assess-banner-meta">约 {{ featuredScale.estimatedTime || 3 }} 分钟可完成</text>
    </view>

    <!-- 3. 全部量表 -->
    <view class="section-block">
      <view class="section-head">
        <text class="section-title">全部量表</text>
        <text class="section-more">{{ scales.length }} 套</text>
      </view>
      <view class="scale-list">
        <view
          v-for="(scale, index) in filteredScales"
          :key="scale.id"
          class="scale-row"
          @tap="goDetail(scale.id)"
        >
          <view class="scale-row-icon" :class="getCategoryStyle(scale.category).cls">
            <MIcon
              :name="getCategoryEmoji(scale.category)"
              :size="22"
              :color="getCategoryStyle(scale.category).color"
            />
          </view>
          <view class="scale-row-body">
            <text class="scale-row-name">{{ scale.name }}</text>
            <text class="scale-row-desc">
              {{ scale.questionNum }}题 · 约{{ scale.estimatedTime || 3 }}分钟 · {{ getCategoryLabel(scale.category) }}
            </text>
          </view>
          <text
            v-if="getScaleTag(index).text"
            class="scale-row-tag"
            :class="getScaleTag(index).cls"
          >{{ getScaleTag(index).text }}</text>
          <MIcon name="chevron" :size="14" color="#6B645C" />
        </view>
      </view>
      <view v-if="loading" class="state-tip"><text>加载中...</text></view>
      <view v-if="!loading && !filteredScales.length" class="state-tip">
        <text>暂无该分类的量表</text>
      </view>
    </view>

    <!-- 4. 测评历史 -->
    <view class="section-block">
      <view class="section-head">
        <text class="section-title">测评历史</text>
        <text class="section-more" @tap="goHistory">全部 ›</text>
      </view>
      <view class="history-card">
        <view
          v-for="item in historyList"
          :key="item.assessmentId"
          class="history-item"
          @tap="goResult(item.assessmentId)"
        >
          <view class="history-item-info">
            <text class="history-item-name">{{ item.scaleName }}</text>
            <text class="history-item-meta">{{ formatHistoryDate(item.createdAt) }}</text>
          </view>
          <text class="history-item-result" :class="getRiskTag(item).type">
            {{ getRiskTag(item).label }}
          </text>
        </view>
        <view v-if="!historyList.length" class="history-empty">
          <text>{{ historyLoading ? '加载中...' : '暂无测评记录' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import {
  getScaleList,
  getAssessmentHistory,
  type Scale,
  type AssessmentResult
} from '@/api/assessment'
import { useUserStore } from '@/stores/user'
import MIcon from '@/components/MIcon.vue'

const userStore = useUserStore()

const loading = ref(false)
const activeCategory = ref('')
const scales = ref<Scale[]>([])

// 测评历史
const historyList = ref<AssessmentResult[]>([])
const historyLoading = ref(false)

const categories = [
  { value: '', label: '全部' },
  { value: 'depression', label: '抑郁' },
  { value: 'anxiety', label: '焦虑' },
  { value: 'stress', label: '压力' },
  { value: 'emotion', label: '情绪' }
]

// 分类图标（对齐原型：sage/coral/lavender/amber）
const CATEGORY_EMOJI: Record<string, string> = {
  depression: 'heart-pulse',
  anxiety: 'wind',
  stress: 'sparkles',
  emotion: 'brain',
  sleep: 'activity',
  personality: 'brain'
}

// 分类色板（新设计令牌：tint 背景 + solid 图标色）
const CATEGORY_STYLE: Record<string, { cls: string; color: string }> = {
  depression: { cls: 'sage', color: '#3A6359' },
  anxiety: { cls: 'coral', color: '#C26B4F' },
  stress: { cls: 'lavender', color: '#6B5B9E' },
  emotion: { cls: 'amber', color: '#B8862F' },
  sleep: { cls: 'sage', color: '#3A6359' },
  personality: { cls: 'amber', color: '#B8862F' }
}
const DEFAULT_CATEGORY_STYLE = { cls: 'sage', color: '#3A6359' }

// 分类描述短标签
const CATEGORY_LABEL: Record<string, string> = {
  depression: '国际标准',
  anxiety: '焦虑筛查',
  stress: '压力来源',
  emotion: '快速筛查',
  sleep: '睡眠评估',
  personality: '人格特质'
}

// 量表附加展示数据（后端 Scale 不含评分/参与人数/进度，前端按序兜底）
const SCALE_STATS = [
  { rating: '4.9', users: '12,345', progress: '85%' },
  { rating: '4.8', users: '10,234', progress: '70%' },
  { rating: '4.7', users: '8,567', progress: '60%' },
  { rating: '4.9', users: '6,789', progress: '50%' },
  { rating: '4.6', users: '5,432', progress: '45%' },
  { rating: '4.7', users: '4,567', progress: '40%' },
  { rating: '4.8', users: '3,890', progress: '35%' },
  { rating: '4.5', users: '2,156', progress: '25%' }
]

// 兜底量表（接口失败或为空时使用，保证页面始终有内容）
const DEFAULT_SCALES: Scale[] = [
  { id: 1, name: 'PHQ-9 抑郁自评量表', description: '国际通用的抑郁筛查工具，快速评估抑郁症状严重程度', category: 'depression', questionNum: 9, estimatedTime: 3, status: 1, createdAt: '' },
  { id: 2, name: 'GAD-7 焦虑自评量表', description: '广泛性焦虑障碍筛查，评估焦虑症状严重程度', category: 'anxiety', questionNum: 7, estimatedTime: 2, status: 1, createdAt: '' },
  { id: 3, name: 'PSS-10 压力知觉量表', description: '评估近期压力水平，了解压力来源和应对方式', category: 'stress', questionNum: 10, estimatedTime: 3, status: 1, createdAt: '' },
  { id: 4, name: 'SCL-90 症状自评量表', description: '综合心理健康评估，全面了解心理健康状况', category: 'depression', questionNum: 90, estimatedTime: 15, status: 1, createdAt: '' },
  { id: 5, name: 'SDS 抑郁自评量表', description: '标准抑郁自评工具，评估抑郁程度', category: 'depression', questionNum: 20, estimatedTime: 5, status: 1, createdAt: '' },
  { id: 6, name: 'SAS 焦虑自评量表', description: '标准焦虑自评工具，评估焦虑程度', category: 'anxiety', questionNum: 20, estimatedTime: 5, status: 1, createdAt: '' },
  { id: 7, name: 'PSQI 睡眠质量指数', description: '评估睡眠质量，了解睡眠问题的影响因素', category: 'sleep', questionNum: 19, estimatedTime: 5, status: 1, createdAt: '' },
  { id: 8, name: 'PANAS 情绪量表', description: '评估积极和消极情绪状态，了解情绪构成', category: 'emotion', questionNum: 20, estimatedTime: 3, status: 1, createdAt: '' }
]

const filteredScales = computed(() => {
  if (!activeCategory.value) return scales.value
  return scales.value.filter((s) => s.category === activeCategory.value)
})

// 进行中测评 banner：取列表首项作为"继续测评"，进度为演示值
const featuredScale = computed(() => filteredScales.value[0] || null)
const featuredCompleted = computed(() => {
  const s = featuredScale.value
  if (!s || !s.questionNum) return 0
  return Math.round(s.questionNum * 0.67)
})
const featuredProgress = computed(() => {
  const s = featuredScale.value
  if (!s || !s.questionNum) return '0%'
  return Math.round((featuredCompleted.value / s.questionNum) * 100) + '%'
})

function getCategoryEmoji(cat: string): string {
  return CATEGORY_EMOJI[cat] || 'clipboard-check'
}

function getCategoryStyle(cat: string) {
  return CATEGORY_STYLE[cat] || DEFAULT_CATEGORY_STYLE
}

function getCategoryLabel(cat: string): string {
  return CATEGORY_LABEL[cat] || '心理评估'
}

function getScaleStats(index: number) {
  return SCALE_STATS[index % SCALE_STATS.length]
}

// 量表行角标（已测 / 推荐 / 新上；空字符串表示无角标）
function getScaleTag(index: number): { text: string; cls: string } {
  if (index === 0) return { text: '已测', cls: 'done' }
  if (index === 1) return { text: '推荐', cls: 'recommend' }
  if (index === 2) return { text: '新上', cls: 'new' }
  return { text: '', cls: '' }
}

function switchCategory(value: string) {
  activeCategory.value = value
}

// 防止快速双击重复入栈
let navigating = false
function goDetail(id: number) {
  if (navigating) return
  navigating = true
  uni.navigateTo({
    url: `/pages/assessment/detail?id=${id}`,
    complete: () => {
      setTimeout(() => {
        navigating = false
      }, 400)
    }
  })
}

function goResult(id: number) {
  uni.navigateTo({ url: `/pages/assessment/result?id=${id}` })
}

function goHistory() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function onSearch() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

// 历史结果标签：mild=amber, normal=sage
function getRiskTag(item: AssessmentResult): { label: string; type: 'mild' | 'normal' } {
  const text = (item.riskText || '').trim()
  const level = (item.riskLevel || '').toLowerCase()
  if (!text || text.includes('正常') || text.includes('无') || level === 'normal' || level === 'none') {
    return { label: text || '正常', type: 'normal' }
  }
  return { label: text, type: 'mild' }
}

function formatHistoryDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return dateStr.slice(0, 10)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

async function loadScales() {
  loading.value = true
  try {
    const data = await getScaleList()
    scales.value = data && data.length ? data : DEFAULT_SCALES
  } catch (error) {
    console.error('加载量表失败:', error)
    scales.value = DEFAULT_SCALES
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const res = await getAssessmentHistory({ current: 1, size: 3 })
    historyList.value = res?.records || []
  } catch (error) {
    console.error('加载测评历史失败:', error)
    historyList.value = []
  } finally {
    historyLoading.value = false
  }
}

onLoad(() => {
  // 初始化：分类默认"全部"，数据在 onShow 拉取以保证每次进入刷新
})

onShow(() => {
  // 登录守卫：未登录跳转登录页
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
  loadScales()
  loadHistory()
})
</script>

<style scoped>
.assessment-page {
  min-height: 100vh;
  background: #EDE9E1; /* bg */
  padding-bottom: 48rpx;
}

/* 1. 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 40rpx 24rpx; /* sp-4 sp-5 sp-3 */
}

.page-title {
  font-size: 48rpx; /* fz-display 24px */
  font-weight: 700;
  color: #2A2722; /* ink */
  letter-spacing: -0.6rpx;
}

.icon-btn {
  width: 80rpx; /* 40px */
  height: 80rpx;
  border-radius: 999rpx;
  background: #FBFAF6; /* surface */
  border: 2rpx solid #E2DDD2; /* border */
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:active {
  background: #F2EFE8; /* surface-2 */
}

/* 2. 进行中测评 banner */
.assess-banner {
  margin: 0 40rpx; /* sp-5 */
  padding: 40rpx; /* sp-5 */
  background: #E6EEEA; /* sage-tint */
  border-radius: 32rpx; /* r-md */
  box-shadow: 0 2rpx 6rpx rgba(42, 39, 34, 0.05);
}

.assess-banner-top {
  display: flex;
  align-items: center;
  gap: 24rpx; /* sp-3 */
  margin-bottom: 16rpx; /* sp-2 */
}

.assess-banner-icon {
  width: 84rpx; /* 42px */
  height: 84rpx;
  border-radius: 16rpx; /* r-xs */
  background: #FBFAF6; /* surface */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.assess-banner-title {
  font-size: 34rpx; /* fz-h2 17px */
  font-weight: 700;
  color: #2A2722; /* ink */
  flex: 1;
}

.assess-banner-desc {
  font-size: 26rpx; /* fz-cap 13px */
  color: #4A453E; /* ink-2 */
  line-height: 1.45;
}

.assess-progress {
  margin-top: 24rpx; /* sp-3 */
  height: 12rpx; /* 6px */
  background: #FBFAF6; /* surface */
  border-radius: 999rpx;
  overflow: hidden;
}

.assess-progress-bar {
  height: 100%;
  background: #4A7C6F; /* sage */
  border-radius: 999rpx;
  transition: width 0.3s ease;
}

.assess-banner-meta {
  font-size: 24rpx; /* fz-micro 12px */
  color: #3A6359; /* sage-deep */
  margin-top: 16rpx; /* sp-2 */
  font-weight: 600;
}

/* 通用 section */
.section-block {
  margin-top: 48rpx; /* sp-6 */
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 0 40rpx 24rpx; /* sp-5 sp-3 */
}

.section-title {
  font-size: 34rpx; /* fz-h2 17px */
  font-weight: 700;
  color: #2A2722; /* ink */
}

.section-more {
  font-size: 26rpx; /* fz-cap 13px */
  color: #3A6359; /* sage-deep */
  font-weight: 500;
}

/* 3. 全部量表列表 */
.scale-list {
  padding: 0 40rpx; /* sp-5 */
}

.scale-row {
  display: flex;
  align-items: center;
  gap: 24rpx; /* sp-3 */
  padding: 32rpx 0; /* sp-4 */
  border-bottom: 2rpx solid #E2DDD2; /* border */
}

.scale-row:last-child {
  border-bottom: none;
}

.scale-row:active .scale-row-name {
  color: #3A6359; /* sage-deep */
}

.scale-row-icon {
  width: 88rpx; /* 44px */
  height: 88rpx;
  border-radius: 24rpx; /* r-sm */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.scale-row-icon.sage {
  background: #E6EEEA; /* sage-tint */
}

.scale-row-icon.coral {
  background: #F4E3DB; /* coral-tint */
}

.scale-row-icon.lavender {
  background: #E8E3F0; /* lavender-tint */
}

.scale-row-icon.amber {
  background: #F0E8D4; /* amber-tint */
}

.scale-row-body {
  flex: 1;
  min-width: 0;
}

.scale-row-name {
  font-size: 28rpx; /* fz-body 14px */
  font-weight: 600;
  color: #2A2722; /* ink */
  transition: color 0.2s;
}

.scale-row-desc {
  font-size: 24rpx; /* fz-micro 12px */
  color: #6B645C; /* muted */
  margin-top: 4rpx;
}

.scale-row-tag {
  font-size: 20rpx; /* 10px */
  padding: 4rpx 16rpx; /* 2px 8px */
  border-radius: 999rpx;
  font-weight: 600;
  flex-shrink: 0;
}

.scale-row-tag.done {
  color: #3A6359; /* sage-deep */
  background: #E6EEEA; /* sage-tint */
}

.scale-row-tag.recommend {
  color: #C26B4F; /* coral */
  background: #F4E3DB; /* coral-tint */
}

.scale-row-tag.new {
  color: #6B5B9E; /* lavender */
  background: #E8E3F0; /* lavender-tint */
}

/* 4. 测评历史 */
.history-card {
  margin: 0 40rpx; /* sp-5 */
  background: #FBFAF6; /* surface */
  border: 2rpx solid #E2DDD2; /* border */
  border-radius: 32rpx; /* r-md */
  overflow: hidden;
  box-shadow: 0 2rpx 6rpx rgba(42, 39, 34, 0.04);
}

.history-item {
  display: flex;
  align-items: center;
  gap: 24rpx; /* sp-3 */
  padding: 24rpx 40rpx; /* sp-3 sp-5 */
  border-bottom: 2rpx solid #E2DDD2; /* border */
}

.history-item:last-child {
  border-bottom: none;
}

.history-item:active {
  background: #F2EFE8; /* surface-2 */
}

.history-item-info {
  flex: 1;
  min-width: 0;
}

.history-item-name {
  font-size: 26rpx; /* fz-cap 13px */
  font-weight: 600;
  color: #2A2722; /* ink */
}

.history-item-meta {
  font-size: 24rpx; /* fz-micro 12px */
  color: #6B645C; /* muted */
  margin-top: 4rpx;
}

.history-item-result {
  font-size: 24rpx; /* fz-micro 12px */
  font-weight: 600;
  padding: 6rpx 20rpx; /* 3px 10px */
  border-radius: 999rpx;
  flex-shrink: 0;
}

.history-item-result.mild {
  color: #B8862F; /* amber */
  background: #F0E8D4; /* amber-tint */
}

.history-item-result.normal {
  color: #3A6359; /* sage-deep */
  background: #E6EEEA; /* sage-tint */
}

.state-tip,
.history-empty {
  padding: 48rpx 0;
  text-align: center;
  font-size: 26rpx;
  color: #6B645C; /* muted */
}
</style>

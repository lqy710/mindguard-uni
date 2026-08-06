<template>
  <view class="result-page">
    <!-- 1. 顶部完成区域（渐变背景） -->
    <view class="complete-section">
      <view class="complete-icon">
        <MIcon name="check" :size="36" color="#ffffff" />
      </view>
      <text class="complete-title">测评完成</text>
      <text class="complete-subtitle">{{ result?.scaleName || '心理测评' }}</text>
    </view>

    <!-- 2. 得分卡片（距顶部 -60rpx 叠加） -->
    <view class="score-card">
      <view class="score-header">
        <text class="score-label">您的得分</text>
        <text class="score-level" :style="{ color: currentLevel.color, background: currentLevel.bgColor }">
          {{ result?.riskText || currentLevel.label }}
        </text>
      </view>

      <view class="score-display">
        <text class="score-number">{{ result?.totalScore ?? 0 }}</text>
        <text class="score-unit">分</text>
      </view>

      <!-- 分数范围条 -->
      <view class="range-bar">
        <view class="range-track">
          <view class="range-fill" :style="{ width: scorePercent + '%' }"></view>
          <view class="range-indicator" :style="{ left: scorePercent + '%', borderColor: currentLevel.color }"></view>
        </view>
        <view class="range-labels">
          <text v-for="n in [0, 5, 10, 15, 20, 27]" :key="n" class="range-label">{{ n }}</text>
        </view>
      </view>

      <!-- 等级说明 -->
      <view class="level-row">
        <view
          v-for="lvl in levels"
          :key="lvl.key"
          class="level-item"
          :class="{ active: lvl.key === currentLevel.key }"
        >
          <view class="level-dot" :style="{ background: lvl.key === currentLevel.key ? lvl.dotColor : '#E2DDD2' }"></view>
          <text class="level-text">{{ lvl.label }} ({{ lvl.range }})</text>
        </view>
      </view>
    </view>

    <!-- 3. 结果解读区域 -->
    <view class="info-card">
      <view class="info-header">
        <MIcon name="chart" :size="22" color="#2A2722" />
        <text class="info-title">结果解读</text>
      </view>
      <view class="info-body">
        <text class="info-text">
          您的得分为 <text class="strong">{{ result?.totalScore ?? 0 }} 分</text>，属于<text class="strong" :style="{ color: currentLevel.color }">{{ result?.riskText || currentLevel.label }}</text>范围。{{ interpretationText }}
        </text>
        <view class="disclaimer">
          <MIcon name="circle-help" :size="16" color="#2A2722" />
          <text class="disclaimer-text">此测评结果仅供参考，不能作为临床诊断依据。如持续感到不适，建议寻求专业心理咨询帮助。</text>
        </view>
      </view>
    </view>

    <!-- 4. 改善建议区域 -->
    <view class="info-card">
      <view class="info-header">
        <MIcon name="lightbulb" :size="22" color="#2A2722" />
        <text class="info-title">改善建议</text>
      </view>
      <view class="suggestion-list">
        <view v-for="s in suggestions" :key="s.title" class="suggestion-item">
          <view class="suggestion-icon" :style="{ background: s.color }">
            <MIcon :name="s.icon" :size="22" color="#ffffff" />
          </view>
          <view class="suggestion-content">
            <text class="suggestion-title">{{ s.title }}</text>
            <text class="suggestion-desc">{{ s.desc }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 5. 危机干预提示（中度及以上风险时显示） -->
    <view v-if="showCrisis" class="crisis-card">
      <view class="crisis-header">
        <MIcon name="circle-help" :size="22" color="#2A2722" />
        <text class="crisis-title">需要帮助？您不是一个人</text>
      </view>
      <text class="crisis-text">如果您正在经历困难时刻，请立即拨打 24 小时心理援助热线：</text>
      <view class="crisis-hotline" @tap="callHotline">
        <MIcon name="phone" :size="20" color="#2A2722" />
        <text class="hotline-number">{{ hotline }}</text>
      </view>
    </view>

    <!-- 占位：避免底部固定栏遮挡内容 -->
    <view class="bottom-spacer"></view>

    <!-- 6. 底部操作栏（固定，安全区适配） -->
    <view class="action-bar">
      <view class="action-btn btn-ghost" @tap="goHistory">
        <text>查看测评历史</text>
      </view>
      <view class="action-btn btn-primary" @tap="goHome">
        <text>返回首页</text>
      </view>
    </view>

    <!-- 加载 / 错误态 -->
    <view v-if="loading" class="loading-mask">
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getAssessmentReport, type AssessmentResult } from '@/api/assessment'
import MIcon from '@/components/MIcon.vue'

interface LevelConfig {
  key: string
  label: string
  range: string
  color: string
  bgColor: string
  dotColor: string
}

/** 风险等级配置（与后端 riskLevel 对应：low / medium / medium-high / high） */
const LEVELS: LevelConfig[] = [
  { key: 'low', label: '正常', range: '0-4', color: '#4A7C6F', bgColor: '#E6EEEA', dotColor: '#4A7C6F' },
  { key: 'medium', label: '轻度', range: '5-9', color: '#B8862F', bgColor: '#F0E8D4', dotColor: '#B8862F' },
  { key: 'medium-high', label: '中度', range: '10-14', color: '#C26B4F', bgColor: '#F4E3DB', dotColor: '#C26B4F' },
  { key: 'high', label: '重度', range: '15-27', color: '#9C5A45', bgColor: '#F4E3DB', dotColor: '#9C5A45' }
]

/** 改善建议（心理健康通用建议，非治疗建议） */
const SUGGESTIONS = [
  { icon: 'moon-star', title: '保持规律作息', desc: '保证充足睡眠，尽量固定入睡与起床时间。', color: '#3A6359' },
  { icon: 'activity', title: '适度运动', desc: '散步、慢跑等户外活动有助于释放压力。', color: '#C26B4F' },
  { icon: 'users', title: '社交互动', desc: '与亲友保持联系，分享感受，不要独自承受。', color: '#6B5B9E' },
  { icon: 'leaf', title: '正念冥想', desc: '每天几分钟呼吸练习，安顿身心。', color: '#B8862F' }
]

const HOTLINE = '400-161-9995'

const result = ref<AssessmentResult | null>(null)
const loading = ref(true)
const levels = LEVELS
const suggestions = SUGGESTIONS
const hotline = HOTLINE

const currentLevel = computed<LevelConfig>(() => {
  const key = result.value?.riskLevel || 'low'
  return LEVELS.find((l) => l.key === key) || LEVELS[0]
})

const scorePercent = computed(() => {
  const score = result.value?.totalScore || 0
  return Math.min((score / 27) * 100, 100)
})

const interpretationText = computed(() => {
  const map: Record<string, string> = {
    low: '这表明您的心理状态良好，继续保持积极的生活方式。',
    medium: '这表明您近期可能经历了一些轻微的心理困扰，如情绪低落、兴趣减退等，对日常生活影响较轻。',
    'medium-high': '这表明您可能正在经历较为明显的心理困扰，建议关注自身心理健康，适当调整生活节奏。',
    high: '这表明您可能正在经历较为严重的心理困扰，强烈建议您寻求专业心理咨询帮助。'
  }
  return map[result.value?.riskLevel || 'low'] || map.low
})

/** 中度及以上风险 -> 展示危机干预卡片 */
const showCrisis = computed(() => {
  const key = result.value?.riskLevel
  return key === 'medium-high' || key === 'high'
})

async function loadResult(id: number) {
  loading.value = true
  try {
    result.value = await getAssessmentReport(id)
  } catch (error) {
    const msg = error instanceof Error ? error.message : '加载结果失败'
    uni.showToast({ title: msg || '加载结果失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goHistory() {
  // 暂无独立历史页，回到测评列表（tabBar 页须用 switchTab）；后续可改为 navigateTo 历史页
  uni.switchTab({ url: '/pages/assessment/list' })
}

function goHome() {
  uni.switchTab({ url: '/pages/home/home' })
}

function callHotline() {
  uni.makePhoneCall({
    phoneNumber: HOTLINE,
    fail: () => uni.showToast({ title: '已取消拨打', icon: 'none' })
  })
}

onLoad((options) => {
  const id = Number(options?.id)
  if (!id || Number.isNaN(id)) {
    uni.showToast({ title: '结果参数缺失', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 800)
    return
  }
  loadResult(id)
})
</script>

<style scoped>
.result-page {
  min-height: 100vh;
  background: #EDE9E1;
}

/* 1. 顶部完成区域 */
.complete-section {
  height: 360rpx;
  background: #3A6359;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 32rpx;
}

.complete-icon {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.complete-check {
  font-size: 64rpx;
  font-weight: 700;
  color: #FBFAF6;
  line-height: 1;
}

.complete-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #FBFAF6;
  letter-spacing: 2rpx;
  margin-bottom: 12rpx;
}

.complete-subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.92);
}

/* 2. 得分卡片 */
.score-card {
  margin: -60rpx 32rpx 24rpx;
  background: #FBFAF6;
  border-radius: 24rpx;
  padding: 40rpx 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 2;
}

.score-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.score-label {
  font-size: 26rpx;
  color: #4A453E;
}

.score-level {
  font-size: 24rpx;
  font-weight: 600;
  padding: 6rpx 20rpx;
  border-radius: 999rpx;
}

.score-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 32rpx;
}

/* 基础色（MP 回退）；H5 用渐变文字 */
.score-number {
  font-size: 80rpx;
  font-weight: 800;
  color: #3A6359;
  line-height: 1;
}
/* #ifdef H5 */
.score-number {
  background: #3A6359;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
/* #endif */

.score-unit {
  font-size: 28rpx;
  color: #4A453E;
  margin-left: 8rpx;
}

/* 分数范围条 */
.range-bar {
  margin-bottom: 28rpx;
}

.range-track {
  position: relative;
  height: 12rpx;
  background: #E2DDD2;
  border-radius: 999rpx;
  margin-bottom: 12rpx;
}

.range-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #4A7C6F 0%, #B8862F 40%, #9C5A45 70%, #9C5A45 100%);
  transition: width 0.5s ease;
}

.range-indicator {
  position: absolute;
  top: 50%;
  width: 28rpx;
  height: 28rpx;
  background: #FBFAF6;
  border: 4rpx solid #3A6359;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.15);
  transition: left 0.5s ease;
}

.range-labels {
  display: flex;
  justify-content: space-between;
}

.range-label {
  font-size: 22rpx;
  color: #6B645C;
}

/* 等级说明 */
.level-row {
  display: flex;
  justify-content: space-between;
}

.level-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.level-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: #E2DDD2;
}

.level-text {
  font-size: 22rpx;
  color: #6B645C;
}

.level-item.active .level-text {
  font-size: 22rpx;
  font-weight: 700;
  color: #2A2722;
}

/* 3/4. 信息卡片（解读 / 建议） */
.info-card {
  margin: 0 32rpx 24rpx;
  background: #FBFAF6;
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
}

.info-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.info-emoji {
  font-size: 36rpx;
  margin-right: 12rpx;
  line-height: 1;
}

.info-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #2A2722;
}

.info-body {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.info-text {
  font-size: 28rpx;
  color: #4A453E;
  line-height: 1.7;
}

.strong {
  font-weight: 700;
  color: #2A2722;
}

.disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 8rpx;
  background: #F0E8D4;
  border-left: 6rpx solid #C26B4F;
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
}

.disclaimer-text {
  flex: 1;
  font-size: 24rpx;
  color: #4A453E;
  line-height: 1.6;
}

/* 改善建议列表 */
.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  padding: 24rpx;
  background: #EDE9E1;
  border-radius: 20rpx;
}

.suggestion-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 20rpx;
}

.suggestion-emoji {
  font-size: 36rpx;
  line-height: 1;
}

.suggestion-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.suggestion-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #2A2722;
  margin-bottom: 8rpx;
}

.suggestion-desc {
  font-size: 24rpx;
  color: #4A453E;
  line-height: 1.5;
}

/* 5. 危机干预卡片 */
.crisis-card {
  margin: 0 32rpx 24rpx;
  background: #F4E3DB;
  border: 2rpx solid #9C5A45;
  border-radius: 24rpx;
  padding: 32rpx;
}

.crisis-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.crisis-emoji {
  font-size: 36rpx;
  margin-right: 12rpx;
  line-height: 1;
}

.crisis-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #9C5A45;
}

.crisis-text {
  font-size: 26rpx;
  color: #4A453E;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.crisis-hotline {
  display: inline-flex;
  align-items: center;
  gap: 10rpx;
  align-self: flex-start;
  padding: 16rpx 28rpx;
  background: #FBFAF6;
  border-radius: 999rpx;
  border: 2rpx solid #9C5A45;
}

.hotline-icon {
  font-size: 30rpx;
  margin-right: 10rpx;
  line-height: 1;
}

.hotline-number {
  font-size: 34rpx;
  font-weight: 800;
  color: #9C5A45;
  letter-spacing: 2rpx;
}

/* 底部占位（避免固定栏遮挡） */
.bottom-spacer {
  height: 160rpx;
}

/* 6. 底部操作栏（固定，安全区适配） */
.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  gap: 24rpx;
  padding: 16rpx 32rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #FBFAF6;
  border-top: 1rpx solid #E2DDD2;
  z-index: 10;
}

.action-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 600;
}

.btn-ghost {
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  color: #4A453E;
}

.btn-primary {
  background: #3A6359;
  color: #FBFAF6;
  box-shadow: 0 6rpx 16rpx rgba(58, 99, 89, 0.25);
}

/* 加载态 */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(237, 233, 225, 0.7);
  z-index: 20;
}

.loading-text {
  font-size: 26rpx;
  color: #6B645C;
}
</style>



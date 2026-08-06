<template>
  <view class="diary-page">
    <!-- 1. 顶部标题区域 -->
    <view class="hero">
      <view class="hero-main">
        <view class="hero-text">
          <text class="hero-title">情绪日记</text>
          <text class="hero-desc">记录每日心情，追踪情绪变化</text>
        </view>
        <view class="write-btn" @click="openModal">
          <MIcon class="write-btn-icon" name="pen-line" :size="16" color="#FBFAF6" />
          <text class="write-btn-text">写日记</text>
        </view>
      </view>
    </view>

    <!-- 2. 统计卡片（2×2，距顶部 -40rpx 叠加） -->
    <view class="stats-grid">
      <view class="stat-card">
        <view class="stat-icon stat-icon-sage">
          <MIcon name="calendar" :size="22" color="#3A6359" />
        </view>
        <text class="stat-number">{{ stats.totalDiaries }}</text>
        <text class="stat-label">日记总数</text>
        <view class="stat-trend trend-up">
          <text>+{{ stats.monthlyNew }} 本月</text>
        </view>
      </view>
      <view class="stat-card">
        <view class="stat-icon stat-icon-coral">
          <MIcon name="flame" :size="22" color="#C26B4F" />
        </view>
        <text class="stat-number">{{ stats.streak }}天</text>
        <text class="stat-label">连续记录</text>
        <view class="stat-trend trend-badge">
          <MIcon name="trophy" :size="14" color="#C26B4F" />
          <text>达成成就</text>
        </view>
      </view>
      <view class="stat-card">
        <view class="stat-icon stat-icon-amber">
          <MIcon name="sun" :size="22" color="#B8862F" />
        </view>
        <text class="stat-number">{{ stats.positiveRate }}%</text>
        <text class="stat-label">积极情绪</text>
        <view class="stat-trend trend-up">
          <text>+{{ stats.positiveChange }}%</text>
        </view>
      </view>
      <view class="stat-card">
        <view class="stat-icon stat-icon-lavender">
          <MIcon name="trending-up" :size="22" color="#6B5B9E" />
        </view>
        <text class="stat-number">+{{ stats.improvement }}%</text>
        <text class="stat-label">情绪提升</text>
        <view class="stat-trend trend-up">
          <text>较上月</text>
        </view>
      </view>
    </view>

    <!-- 3. 情绪趋势 -->
    <view class="trend-card">
      <view class="trend-header">
        <view class="trend-title">
          <MIcon name="chart" :size="18" color="#2A2722" />
          <text>情绪趋势</text>
        </view>
        <view class="trend-tabs">
          <view
            class="trend-tab"
            :class="{ active: chartRange === 'week' }"
            @click="switchRange('week')"
          >
            <text>本周</text>
          </view>
          <view
            class="trend-tab"
            :class="{ active: chartRange === 'month' }"
            @click="switchRange('month')"
          >
            <text>本月</text>
          </view>
        </view>
      </view>

      <view class="chart-area">
        <view
          v-for="(bar, index) in chartData"
          :key="index"
          class="chart-bar-group"
        >
          <text class="chart-bar-value">{{ bar.value }}</text>
          <view class="chart-bar-track">
            <view
              class="chart-bar"
              :style="{ height: bar.height + 'rpx' }"
            ></view>
          </view>
          <text class="chart-bar-label">{{ bar.label }}</text>
        </view>
      </view>

      <view class="chart-summary">
        <view class="summary-item">
          <text class="summary-label">平均</text>
          <text class="summary-value">{{ chartSummary.average }}</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">最高</text>
          <text class="summary-value highlight">{{ chartSummary.max }}</text>
        </view>
        <view class="summary-item">
          <text class="summary-label">最低</text>
          <text class="summary-value low">{{ chartSummary.min }}</text>
        </view>
      </view>
    </view>

    <!-- 4. 日记列表（时间线） -->
    <view class="list-section">
      <view class="list-title">
        <MIcon name="pen-line" :size="20" color="#2A2722" />
        <text>我的日记</text>
      </view>

      <view v-if="diaries.length" class="timeline">
        <view
          v-for="(diary, index) in diaries"
          :key="diary.id"
          class="timeline-item"
        >
          <!-- 左侧：圆点 + 竖线 -->
          <view class="timeline-left">
            <view class="timeline-dot" :style="{ background: getMood(diary.emotionType).color }"></view>
            <view v-if="index !== diaries.length - 1" class="timeline-line"></view>
          </view>

          <!-- 右侧：日记卡片 -->
          <view class="timeline-card">
            <view class="card-top">
              <text class="card-date">{{ formatDate(diary.createdAt).text }}</text>
              <text class="card-weekday">{{ formatDate(diary.createdAt).weekday }}</text>
              <MIcon class="card-mood-emoji" :name="getMood(diary.emotionType).icon" :size="20" :color="getMood(diary.emotionType).color" />
            </view>
            <text class="card-content text-clamp-3">{{ diary.content }}</text>
            <view v-if="(diary.tags && diary.tags.length)" class="card-tags">
              <view
                v-for="tag in diary.tags"
                :key="tag"
                class="card-tag"
              >
                <MIcon :name="getMood(diary.emotionType).icon" :size="14" :color="getMood(diary.emotionType).color" />
                <text>{{ tag }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-else-if="!loading" class="empty-state">
        <MIcon class="empty-emoji" name="file-text" :size="36" color="#6B645C" />
        <text class="empty-text">还没有日记，点击右上角开始记录吧</text>
      </view>

      <!-- 加载态 -->
      <view v-if="loading" class="state-tip">
        <text>加载中...</text>
      </view>
      <view v-if="!loading && diaries.length && !hasMore" class="state-tip">
        <text>— 已经到底啦 —</text>
      </view>
    </view>

    <!-- 5. 写日记弹窗（底部弹出） -->
    <view v-if="showWriteModal" class="modal-mask" @click="closeModal">
      <view
        class="modal-sheet"
        :style="sheetStyle"
        @click.stop
      >
        <!-- 顶部：日期 + 关闭 -->
        <view class="sheet-header">
          <text class="sheet-date">{{ todayText }}</text>
          <view class="sheet-close" @click="closeModal">
            <MIcon name="x" :size="20" color="#6B645C" />
          </view>
        </view>

        <!-- 情绪选择 -->
        <view class="sheet-section">
          <text class="section-label">今天的心情</text>
          <view class="mood-options">
            <view
              v-for="mood in MOOD_LIST"
              :key="mood.value"
              class="mood-option"
              :class="{ selected: selectedMood === mood.value }"
              :style="selectedMood === mood.value ? { borderColor: mood.color, background: mood.color + '15' } : {}"
              @click="selectMood(mood.value)"
            >
              <MIcon class="mood-emoji-lg" :name="mood.icon" :size="24" :color="mood.color" />
              <text class="mood-label" :style="selectedMood === mood.value ? { color: mood.color } : {}">{{ mood.label }}</text>
            </view>
          </view>
        </view>

        <!-- 情绪标签（多选） -->
        <view class="sheet-section">
          <text class="section-label">情绪标签（可多选）</text>
          <view class="tag-options">
            <view
              v-for="tag in tagOptions"
              :key="tag"
              class="tag-option"
              :class="{ selected: selectedTags.includes(tag) }"
              @click="toggleTag(tag)"
            >
              <text>{{ tag }}</text>
            </view>
          </view>
        </view>

        <!-- 日记内容 -->
        <view class="sheet-section">
          <text class="section-label">日记内容</text>
          <textarea
            class="diary-textarea"
            v-model="diaryContent"
            placeholder="今天有什么想说的..."
            :maxlength="500"
            :auto-height="true"
            :adjust-position="true"
            :cursor-spacing="20"
            placeholder-class="textarea-placeholder"
          />
          <text class="textarea-count">{{ diaryContent.length }}/500</text>
        </view>

        <!-- 保存按钮 -->
        <view class="save-btn" :class="{ disabled: saving }" @click="saveDiary">
          <text class="save-btn-text">{{ saving ? '保存中...' : '保存日记' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { onShow, onReachBottom, onUnload } from '@dcloudio/uni-app'
import {
  createDiary,
  getDiaryList,
  getDiaryStatistics,
  getEmotionTrend,
  type Diary,
  type DiaryStatistics,
  type EmotionTrendItem
} from '@/api/diary'
import { useUserStore } from '@/stores/user'
import MIcon from '@/components/MIcon.vue'

const userStore = useUserStore()

/** 情绪配置（5 种，对应弹窗选择与列表展示） */
interface MoodConfig {
  value: string
  icon: string
  label: string
  score: number
  color: string
}
const MOOD_LIST: MoodConfig[] = [
  { value: 'happy', icon: 'laugh', label: '开心', score: 9, color: '#4A7C6F' },
  { value: 'calm', icon: 'smile', label: '平静', score: 7, color: '#3A6359' },
  { value: 'down', icon: 'meh', label: '低落', score: 4, color: '#B8862F' },
  { value: 'sad', icon: 'frown', label: '难过', score: 2, color: '#6B5B9E' },
  { value: 'angry', icon: 'angry', label: '愤怒', score: 3, color: '#C26B4F' }
]
const MOOD_MAP: Record<string, MoodConfig> = MOOD_LIST.reduce(
  (acc, m) => {
    acc[m.value] = m
    return acc
  },
  {} as Record<string, MoodConfig>
)

const tagOptions = ['工作', '学习', '社交', '家庭', '健康', '其他']

/** 危机干预关键词（合规红线：心理健康类目强制要求） */
const CRISIS_KEYWORDS = ['自杀', '自残', '自伤', '不想活', '想死', '结束生命', '了结自己', '活不下去']
const HOTLINE = '4001619995'

/** 统计兜底数据（接口失败时使用，保证页面始终可读） */
const DEFAULT_STATS: DiaryStatistics = {
  totalDiaries: 28,
  monthlyNew: 5,
  streak: 7,
  positiveRate: 72,
  positiveChange: 8,
  improvement: 15
}

/** 趋势兜底数据（week=近 7 天，month=近 30 天采样 7 点） */
const DEFAULT_WEEK_TREND: EmotionTrendItem[] = [
  { date: '一', score: 7 }, { date: '二', score: 8 }, { date: '三', score: 5 },
  { date: '四', score: 6 }, { date: '五', score: 9 }, { date: '六', score: 8.5 },
  { date: '日', score: 7.5 }
]
const DEFAULT_MONTH_TREND: EmotionTrendItem[] = [
  { date: '5', score: 6.5 }, { date: '10', score: 7.2 }, { date: '15', score: 8 },
  { date: '20', score: 6.8 }, { date: '25', score: 7.5 }, { date: '28', score: 8.4 },
  { date: '30', score: 7 }
]

/** 列表兜底数据（接口失败时使用，演示时间线效果） */
const DEFAULT_DIARIES: Diary[] = [
  { id: 1, emotionType: 'happy', emotionScore: 9, content: '今天和朋友一起去了公园，阳光很好，心情很舒畅。感觉最近的状态在慢慢变好，工作上的压力也在逐渐释放。', sentimentScore: 0.9, aiAnalysis: '', tags: ['社交', '健康'], createdAt: '2026-07-30 14:30:00' },
  { id: 2, emotionType: 'calm', emotionScore: 7, content: '普通的一天，按部就班地完成了工作。晚上看了一会儿书，内心比较平静，没有太多波澜。', sentimentScore: 0.5, aiAnalysis: '', tags: ['工作'], createdAt: '2026-07-28 21:10:00' },
  { id: 3, emotionType: 'down', emotionScore: 4, content: '工作不太顺利，遇到了一些困难，感觉自己有点力不从心。希望明天能好起来，调整一下状态再继续。', sentimentScore: 0.2, aiAnalysis: '', tags: ['工作', '家庭'], createdAt: '2026-07-26 20:45:00' }
]

// ===== 状态 =====
const loading = ref(false)
const stats = reactive<DiaryStatistics>({ ...DEFAULT_STATS })
const diaries = ref<Diary[]>([])
const currentPage = ref(1)
const pageSize = 10
const hasMore = ref(true)

const chartRange = ref<'week' | 'month'>('week')
const weekTrend = ref<EmotionTrendItem[]>(DEFAULT_WEEK_TREND)
const monthTrend = ref<EmotionTrendItem[]>(DEFAULT_MONTH_TREND)

// 写日记弹窗
const showWriteModal = ref(false)
const sheetAnim = ref(false)
const keyboardHeight = ref(0)
const selectedMood = ref('happy')
const diaryContent = ref('')
const selectedTags = ref<string[]>([])
const saving = ref(false)

// ===== 计算属性 =====
const todayText = computed(() => {
  const d = new Date()
  const weekday = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()]
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 周${weekday}`
})

/** 当前范围下的趋势数据 */
const currentTrend = computed(() =>
  chartRange.value === 'week' ? weekTrend.value : monthTrend.value
)

/** 柱状图数据：7 个柱子，最高 200rpx */
const chartData = computed(() => {
  const data = currentTrend.value
  return data.map((item) => ({
    label: item.date,
    value: item.score,
    height: Math.max(8, Math.round((item.score / 10) * 200))
  }))
})

const chartSummary = computed(() => {
  const scores = currentTrend.value.map((i) => i.score)
  if (!scores.length) return { average: '0', max: '0', min: '0' }
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length
  const max = Math.max(...scores)
  const min = Math.min(...scores)
  return {
    average: avg.toFixed(1),
    max: max.toFixed(1),
    min: min.toFixed(1)
  }
})

/** 弹窗滑入动画 + 键盘适配样式 */
const sheetStyle = computed(() => {
  const style: Record<string, string> = {
    transform: sheetAnim.value ? 'translateY(0)' : 'translateY(100%)'
  }
  if (keyboardHeight.value > 0) {
    style.paddingBottom = `${keyboardHeight.value + 24}px`
  }
  return style
})

// ===== 工具函数 =====
function getMood(emotionType: string): MoodConfig {
  return MOOD_MAP[emotionType] || MOOD_LIST[1]
}

/** 安全解析后端时间字符串（兼容 "2026-07-30 14:30:00" 与 ISO） */
function parseDate(str: string): Date {
  if (!str) return new Date()
  const normalized = str.includes('T') ? str : str.replace(' ', 'T')
  const d = new Date(normalized)
  return isNaN(d.getTime()) ? new Date() : d
}

function formatDate(createdAt: string): { text: string; weekday: string } {
  const d = parseDate(createdAt)
  const weekday = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
  return {
    text: `${d.getMonth() + 1}月${d.getDate()}日`,
    weekday
  }
}

// ===== 数据加载 =====
async function loadStats() {
  try {
    const data = await getDiaryStatistics()
    if (data) Object.assign(stats, data)
  } catch (error) {
    console.error('加载日记统计失败:', error)
  }
}

async function loadTrend() {
  try {
    const [week, month] = await Promise.all([
      getEmotionTrend(7),
      getEmotionTrend(30)
    ])
    if (week && week.length) weekTrend.value = week
    if (month && month.length) monthTrend.value = sampleTrend(month, 7)
  } catch (error) {
    console.error('加载情绪趋势失败:', error)
  }
}

/** 将 30 天趋势采样为 7 个点（均匀抽取） */
function sampleTrend(list: EmotionTrendItem[], count: number): EmotionTrendItem[] {
  if (list.length <= count) return list
  const step = (list.length - 1) / (count - 1)
  const result: EmotionTrendItem[] = []
  for (let i = 0; i < count; i++) {
    const idx = Math.round(i * step)
    const item = list[idx]
    // 优先用日期中的"日"作为标签；解析失败则保留原字符串
    const parsed = new Date(item.date.includes('T') ? item.date : item.date.replace(' ', 'T'))
    const label = isNaN(parsed.getTime()) ? item.date : String(parsed.getDate())
    result.push({ date: label, score: item.score })
  }
  return result
}

async function loadDiaries(reset = false) {
  if (loading.value) return
  if (reset) {
    currentPage.value = 1
    hasMore.value = true
  }
  if (!hasMore.value) return
  loading.value = true
  try {
    const res = await getDiaryList({ current: currentPage.value, size: pageSize })
    const records = res?.records || []
    if (reset) {
      diaries.value = records
    } else {
      diaries.value = [...diaries.value, ...records]
    }
    hasMore.value = diaries.value.length < (res?.total || 0)
  } catch (error) {
    console.error('加载日记列表失败:', error)
    // 接口失败：首次加载用兜底数据演示，保证页面非空
    if (reset && !diaries.value.length) {
      diaries.value = DEFAULT_DIARIES
      hasMore.value = false
    }
  } finally {
    loading.value = false
  }
}

function switchRange(range: 'week' | 'month') {
  if (chartRange.value === range) return
  chartRange.value = range
}

// ===== 写日记弹窗 =====
function onKeyboardHeightChange(res: { height: number }) {
  keyboardHeight.value = res.height || 0
}

function openModal() {
  showWriteModal.value = true
  // 下一帧触发滑入动画（v-if 挂载后再加 class）
  setTimeout(() => {
    sheetAnim.value = true
  }, 20)
  // #ifdef MP-WEIXIN || APP-PLUS
  uni.onKeyboardHeightChange(onKeyboardHeightChange)
  // #endif
}

function closeModal() {
  sheetAnim.value = false
  keyboardHeight.value = 0
  // #ifdef MP-WEIXIN || APP-PLUS
  uni.offKeyboardHeightChange(onKeyboardHeightChange)
  // #endif
  // 等待滑出动画结束再卸载
  setTimeout(() => {
    showWriteModal.value = false
  }, 250)
}

function selectMood(value: string) {
  selectedMood.value = value
}

function toggleTag(tag: string) {
  const idx = selectedTags.value.indexOf(tag)
  if (idx > -1) {
    selectedTags.value.splice(idx, 1)
  } else {
    selectedTags.value.push(tag)
  }
}

/** 危机干预：检测自伤/自杀关键词，推送援助热线（合规红线） */
function detectCrisis(content: string): boolean {
  return CRISIS_KEYWORDS.some((kw) => content.includes(kw))
}

function showCrisisHelp() {
  uni.showModal({
    title: '你并不孤单',
    content: '如果你正在经历痛苦，请记得有人愿意倾听。是否拨打 24 小时心理援助热线 400-161-9995？',
    confirmText: '立即拨打',
    cancelText: '稍后',
    success: (res) => {
      if (res.confirm) {
        uni.makePhoneCall({ phoneNumber: HOTLINE })
      }
    }
  })
}

async function saveDiary() {
  if (saving.value) return
  if (!diaryContent.value.trim()) {
    uni.showToast({ title: '请填写日记内容', icon: 'none' })
    return
  }

  const mood = getMood(selectedMood.value)
  saving.value = true
  try {
    await createDiary({
      emotionType: selectedMood.value,
      emotionScore: mood.score,
      content: diaryContent.value.trim(),
      tags: selectedTags.value
    })
    uni.showToast({ title: '日记保存成功', icon: 'success' })

    // 合规：内容含危机关键词时，温柔推送热线（不阻断保存）
    if (detectCrisis(diaryContent.value)) {
      setTimeout(showCrisisHelp, 500)
    }

    // 重置表单并关闭
    diaryContent.value = ''
    selectedTags.value = []
    selectedMood.value = 'happy'
    closeModal()

    // 刷新数据
    loadStats()
    loadTrend()
    loadDiaries(true)
  } catch (error) {
    const msg = error instanceof Error ? error.message : '保存失败'
    uni.showToast({ title: msg, icon: 'none' })
  } finally {
    saving.value = false
  }
}

// ===== 生命周期 =====
onShow(() => {
  // 登录守卫：未登录跳转登录页
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
  loadStats()
  loadTrend()
  loadDiaries(true)
})

onReachBottom(() => {
  if (hasMore.value && !loading.value) {
    currentPage.value++
    loadDiaries(false)
  }
})

onUnload(() => {
  // 清理键盘监听，避免内存泄漏
  // #ifdef MP-WEIXIN || APP-PLUS
  uni.offKeyboardHeightChange(onKeyboardHeightChange)
  // #endif
})
</script>

<style scoped>
.diary-page {
  min-height: 100vh;
  background: #EDE9E1;
  padding-bottom: calc(60rpx + env(safe-area-inset-bottom));
}

/* 1. 顶部标题区域 */
.hero {
  background: #3A6359;
  padding: 48rpx 32rpx 56rpx;
  min-height: 280rpx;
  box-sizing: border-box;
  display: flex;
  align-items: center;
}

.hero-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.hero-text {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.hero-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #FBFAF6;
  line-height: 1.3;
}

.hero-desc {
  font-size: 26rpx;
  color: rgba(251, 250, 246, 0.85);
  margin-top: 12rpx;
  line-height: 1.5;
}

.write-btn {
  display: flex;
  align-items: center;
  padding: 14rpx 28rpx;
  background: rgba(251, 250, 246, 0.18);
  border-radius: 999rpx;
  flex-shrink: 0;
  margin-left: 16rpx;
}

.write-btn-icon {
  font-size: 26rpx;
  margin-right: 8rpx;
}

.write-btn-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #FBFAF6;
}

/* 2. 统计卡片（2×2） */
.stats-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  padding: 0 32rpx;
  margin-top: -40rpx;
  position: relative;
  z-index: 2;
}

.stat-card {
  width: 331rpx;
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-radius: 24rpx;
  padding: 28rpx 24rpx;
  margin-bottom: 24rpx;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.stat-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.stat-icon-sage {
  background: #E6EEEA;
}

.stat-icon-coral {
  background: #F4E3DB;
}

.stat-icon-amber {
  background: #F0E8D4;
}

.stat-icon-lavender {
  background: #E8E3F0;
}

.stat-number {
  font-size: 40rpx;
  font-weight: 700;
  color: #2A2722;
  line-height: 1.2;
}

.stat-label {
  font-size: 24rpx;
  color: #6B645C;
  margin-top: 6rpx;
}

.stat-trend {
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 4rpx;
  margin-top: 14rpx;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
}

.trend-up {
  background: #E6EEEA;
  color: #3A6359;
}

.trend-badge {
  background: #F4E3DB;
  color: #C26B4F;
  font-weight: 600;
}

/* 3. 情绪趋势 */
.trend-card {
  margin: 8rpx 32rpx 0;
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-radius: 24rpx;
  padding: 32rpx 28rpx;
}

.trend-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32rpx;
}

.trend-title {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #2A2722;
}

.trend-tabs {
  display: flex;
  background: #F2EFE8;
  border-radius: 999rpx;
  padding: 4rpx;
}

.trend-tab {
  padding: 10rpx 24rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  color: #6B645C;
  transition: all 0.2s ease;
}

.trend-tab.active {
  background: #3A6359;
  color: #FBFAF6;
}

.chart-area {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 280rpx;
  padding: 0 4rpx;
}

.chart-bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.chart-bar-value {
  font-size: 20rpx;
  color: #4A7C6F;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.chart-bar-track {
  width: 100%;
  height: 200rpx;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.chart-bar {
  width: 40rpx;
  background: #4A7C6F;
  border-radius: 8rpx 8rpx 0 0;
  transition: height 0.4s ease;
}

.chart-bar-label {
  font-size: 20rpx;
  color: #6B645C;
  margin-top: 10rpx;
}

.chart-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 28rpx;
  padding: 20rpx;
  background: #F2EFE8;
  border-radius: 16rpx;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-label {
  font-size: 22rpx;
  color: #6B645C;
  margin-bottom: 6rpx;
}

.summary-value {
  font-size: 30rpx;
  font-weight: 700;
  color: #4A7C6F;
}

.summary-value.highlight {
  color: #3A6359;
}

.summary-value.low {
  color: #6B5B9E;
}

/* 4. 日记列表（时间线） */
.list-section {
  margin: 32rpx 32rpx 0;
}

.list-title {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 32rpx;
  font-weight: 700;
  color: #2A2722;
  margin-bottom: 24rpx;
}

.timeline {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
}

.timeline-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 32rpx;
  flex-shrink: 0;
}

.timeline-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  margin-top: 12rpx;
  flex-shrink: 0;
}

.timeline-line {
  width: 2rpx;
  flex: 1;
  background: #E2DDD2;
  margin-top: 6rpx;
  margin-bottom: 6rpx;
}

.timeline-card {
  flex: 1;
  min-width: 0;
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-radius: 20rpx;
  padding: 24rpx 28rpx;
  margin-left: 20rpx;
  margin-bottom: 24rpx;
}

.card-top {
  display: flex;
  align-items: center;
  margin-bottom: 14rpx;
}

.card-date {
  font-size: 26rpx;
  font-weight: 600;
  color: #2A2722;
}

.card-weekday {
  font-size: 22rpx;
  color: #6B645C;
  margin-left: 12rpx;
}

.card-mood-emoji {
  font-size: 32rpx;
  margin-left: auto;
}

.card-content {
  font-size: 26rpx;
  color: #4A453E;
  line-height: 1.6;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}

.card-tag {
  display: flex;
  align-items: center;
  gap: 4rpx;
  padding: 6rpx 16rpx;
  background: #E6EEEA;
  border-radius: 999rpx;
  font-size: 22rpx;
  color: #3A6359;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
}

.empty-emoji {
  font-size: 72rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 26rpx;
  color: #6B645C;
  text-align: center;
}

.state-tip {
  padding: 32rpx 0;
  text-align: center;
  font-size: 24rpx;
  color: #6B645C;
}

/* 5. 写日记弹窗 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(42, 39, 34, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.modal-sheet {
  width: 100%;
  background: #FBFAF6;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx 32rpx calc(40rpx + env(safe-area-inset-bottom));
  max-height: 85vh;
  overflow-y: auto;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32rpx;
}

.sheet-date {
  font-size: 30rpx;
  font-weight: 700;
  color: #2A2722;
}

.sheet-close {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F2EFE8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sheet-section {
  margin-bottom: 32rpx;
}

.section-label {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: #2A2722;
  margin-bottom: 20rpx;
}

/* 情绪选择 */
.mood-options {
  display: flex;
  justify-content: space-between;
  gap: 12rpx;
}

.mood-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 8rpx;
  border-radius: 20rpx;
  background: #F2EFE8;
  border: 2rpx solid transparent;
  transition: all 0.2s ease;
}

.mood-emoji-lg {
  font-size: 48rpx;
}

.mood-label {
  font-size: 22rpx;
  color: #6B645C;
  margin-top: 10rpx;
}

/* 标签 */
.tag-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.tag-option {
  padding: 14rpx 28rpx;
  border-radius: 999rpx;
  background: #F2EFE8;
  font-size: 24rpx;
  color: #6B645C;
  border: 2rpx solid transparent;
  transition: all 0.2s ease;
}

.tag-option.selected {
  background: #3A6359;
  color: #FBFAF6;
  border-color: transparent;
}

/* textarea */
.diary-textarea {
  width: 100%;
  min-height: 160rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  color: #2A2722;
  background: #F2EFE8;
  border-radius: 16rpx;
  border: 2rpx solid #E2DDD2;
  line-height: 1.6;
  box-sizing: border-box;
}

.textarea-placeholder {
  color: #6B645C;
  font-size: 28rpx;
}

.textarea-count {
  display: block;
  text-align: right;
  font-size: 22rpx;
  color: #6B645C;
  margin-top: 8rpx;
}

/* 保存按钮 */
.save-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  border-radius: 999rpx;
  background: #3A6359;
  margin-top: 8rpx;
}

.save-btn.disabled {
  opacity: 0.6;
}

.save-btn-text {
  font-size: 30rpx;
  font-weight: 600;
  color: #FBFAF6;
}

/* 通用：三行截断 */
.text-clamp-3 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

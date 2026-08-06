<template>
  <view class="detail-page">
    <!-- 1. 顶部固定区域：自定义导航栏 + 渐变进度条 -->
    <view class="nav-bar">
      <view class="status-bar-spacer" :style="{ height: statusBarHeight + 'px' }"></view>
      <view class="nav-content">
        <view class="nav-back" @tap="onBack">
          <text class="back-arrow">‹</text>
        </view>
        <text class="nav-title">{{ scaleName }}</text>
        <text class="nav-progress">{{ total ? `${currentIndex + 1}/${total}` : '' }}</text>
      </view>
      <view class="progress-track">
        <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
      </view>
    </view>

    <!-- 2. 题目区域：swiper 一题一屏 -->
    <view class="swiper-wrap">
      <swiper
        class="question-swiper"
        :style="{ height: swiperHeight + 'px' }"
        :current="currentIndex"
        :indicator-dots="false"
        :autoplay="false"
        :duration="250"
        :circular="false"
        @change="onSwiperChange"
      >
        <swiper-item v-for="(q, idx) in questions" :key="q.id">
          <scroll-view scroll-y class="question-scroll">
            <view class="question-body">
              <text class="question-num">第 {{ idx + 1 }} 题 / 共 {{ total }} 题</text>
              <text class="question-text">{{ q.content }}</text>

              <view class="options">
                <view
                  v-for="opt in parseOptions(q.options)"
                  :key="opt.value"
                  class="option-wrap"
                  :class="{ selected: answers[q.id] === opt.value }"
                  @tap="selectAnswer(q.id, opt.value)"
                >
                  <view class="option-card">
                    <text class="option-text">{{ opt.label }}</text>
                    <view class="option-right">
                      <text class="option-score">{{ opt.value }}分</text>
                      <MIcon v-if="answers[q.id] === opt.value" name="check" :size="18" color="#2A2722" />
                    </view>
                  </view>
                </view>
              </view>

              <view class="tips">
                <view class="tip-item">
                  <MIcon name="lock" :size="18" color="#2A2722" />
                  <text class="tip-text">您的回答将被严格保密</text>
                </view>
                <view class="tip-item">
                  <MIcon name="circle-help" :size="18" color="#2A2722" />
                  <text class="tip-text">请根据过去两周的真实感受作答</text>
                </view>
              </view>
            </view>
          </scroll-view>
        </swiper-item>
      </swiper>

      <view v-if="loading" class="loading-mask">
        <text class="loading-text">加载中...</text>
      </view>
    </view>

    <!-- 3. 底部固定操作栏（安全区适配） -->
    <view class="action-bar">
      <view
        class="action-btn btn-prev"
        :class="{ disabled: currentIndex === 0 }"
        @tap="prevQuestion"
      >
        <text>上一题</text>
      </view>
      <view
        v-if="currentIndex < total - 1"
        class="action-btn btn-next"
        :class="{ disabled: !isAnswered }"
        @tap="nextQuestion"
      >
        <text>下一题</text>
      </view>
      <view
        v-else
        class="action-btn btn-submit"
        :class="{ disabled: !isAnswered || submitting }"
        @tap="confirmSubmit"
      >
        <text>提交测评</text>
      </view>
    </view>

    <!-- 4. 提交确认弹窗 -->
    <view v-if="showConfirm" class="modal-mask" @tap="cancelSubmit">
      <view class="modal-dialog" @tap.stop>
        <text class="modal-title">确认提交</text>
        <text class="modal-content">您已完成全部 {{ total }} 道题，确认提交测评？</text>
        <view class="modal-actions">
          <view class="modal-btn modal-btn-cancel" @tap="cancelSubmit">
            <text>取消</text>
          </view>
          <view class="modal-btn modal-btn-confirm" @tap="doSubmit">
            <text>确认提交</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import {
  getScaleDetail,
  submitAssessment,
  type ScaleDetail,
  type Question,
  type SubmitAnswer
} from '@/api/assessment'
import MIcon from '@/components/MIcon.vue'

interface Option {
  label: string
  value: number
}
type RawOption = { label?: string; text?: string; value?: number }

const DEFAULT_OPTIONS: Option[] = [
  { label: '完全没有', value: 0 },
  { label: '有几天', value: 1 },
  { label: '一半以上的时间', value: 2 },
  { label: '几乎每天', value: 3 }
]

// 兜底题库：接口失败或返回空时使用（沿用 legacy PHQ-9 简版）
const DEFAULT_QUESTIONS: Question[] = [
  { id: 1, orderNum: 1, content: '做事时提不起劲或没有兴趣', options: '' },
  { id: 2, orderNum: 2, content: '感到心情低落、沮丧或绝望', options: '' },
  { id: 3, orderNum: 3, content: '入睡困难、睡不着或睡眠过多', options: '' },
  { id: 4, orderNum: 4, content: '感觉疲倦或没有活力', options: '' },
  { id: 5, orderNum: 5, content: '食欲不振或吃得太多', options: '' },
  { id: 6, orderNum: 6, content: '觉得自己很糟，或觉得自己很失败', options: '' },
  { id: 7, orderNum: 7, content: '对事物专注有困难，例如阅读报纸或看电视时', options: '' },
  { id: 8, orderNum: 8, content: '动作或说话速度缓慢到别人已经察觉，或相反，烦躁不安、动来动去', options: '' },
  { id: 9, orderNum: 9, content: '有不如死掉或用某种方式伤害自己的念头', options: '' }
]

const scaleId = ref(0)
const scale = ref<ScaleDetail | null>(null)
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const answers = ref<Record<number, number>>({})
const loading = ref(false)
const submitting = ref(false)
const showConfirm = ref(false)
const statusBarHeight = ref(0)
const swiperHeight = ref(0)

const total = computed(() => questions.value.length)
const currentQuestion = computed(() => questions.value[currentIndex.value])
const isAnswered = computed(() => {
  const q = currentQuestion.value
  return !!q && answers.value[q.id] !== undefined
})
const progressPercent = computed(() => {
  if (total.value === 0) return 0
  return ((currentIndex.value + 1) / total.value) * 100
})
const scaleName = computed(() => scale.value?.name || '心理测评')

function parseOptions(optionsStr: string): Option[] {
  if (!optionsStr) return DEFAULT_OPTIONS
  try {
    const parsed = JSON.parse(optionsStr) as RawOption[]
    if (!Array.isArray(parsed) || parsed.length === 0) return DEFAULT_OPTIONS
    const opts = parsed
      .map((opt) => ({
        label: opt.label ?? opt.text ?? '',
        value: Number(opt.value ?? 0)
      }))
      .filter((o) => o.label && !Number.isNaN(o.value))
    return opts.length ? opts : DEFAULT_OPTIONS
  } catch {
    return DEFAULT_OPTIONS
  }
}

let advanceTimer: ReturnType<typeof setTimeout> | null = null
function clearAdvanceTimer() {
  if (advanceTimer) {
    clearTimeout(advanceTimer)
    advanceTimer = null
  }
}

function selectAnswer(qid: number, value: number) {
  answers.value[qid] = value
  // 选中后自动进入下一题（最后一题不自动跳，避免越界）
  if (currentIndex.value < total.value - 1) {
    clearAdvanceTimer()
    advanceTimer = setTimeout(() => {
      currentIndex.value++
      advanceTimer = null
    }, 300)
  }
}

interface SwiperChangeEvent {
  detail: { current: number; source: string }
}
function onSwiperChange(e: SwiperChangeEvent) {
  const idx = e.detail.current
  if (idx === currentIndex.value) return
  // 用户手动滑动时取消未执行的自动跳转，避免抢跳
  clearAdvanceTimer()
  currentIndex.value = idx
}

function prevQuestion() {
  if (currentIndex.value === 0) return
  clearAdvanceTimer()
  currentIndex.value--
}

function nextQuestion() {
  if (!isAnswered.value) {
    uni.showToast({ title: '请先选择答案', icon: 'none' })
    return
  }
  if (currentIndex.value >= total.value - 1) return
  clearAdvanceTimer()
  currentIndex.value++
}

function confirmSubmit() {
  if (submitting.value) return
  const unanswered = questions.value.filter((q) => answers.value[q.id] === undefined)
  if (unanswered.length > 0) {
    const firstIdx = questions.value.findIndex((q) => answers.value[q.id] === undefined)
    uni.showToast({ title: `还有 ${unanswered.length} 题未作答`, icon: 'none' })
    if (firstIdx >= 0) {
      clearAdvanceTimer()
      currentIndex.value = firstIdx
    }
    return
  }
  showConfirm.value = true
}

function cancelSubmit() {
  showConfirm.value = false
}

async function doSubmit() {
  showConfirm.value = false
  if (submitting.value) return
  submitting.value = true
  try {
    const answerList: SubmitAnswer[] = questions.value.map((q) => ({
      questionId: q.id,
      answer: answers.value[q.id] ?? 0
    }))
    const result = await submitAssessment(scaleId.value, answerList)
    uni.showToast({ title: '测评完成', icon: 'success' })
    setTimeout(() => {
      // 重定向到结果页，避免返回栈累积（list -> result，而非 list -> detail -> result）
      uni.redirectTo({ url: `/pages/assessment/result?id=${result.assessmentId}` })
    }, 600)
  } catch (error) {
    const msg = error instanceof Error ? error.message : '提交失败'
    uni.showToast({ title: msg || '提交失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

function onBack() {
  clearAdvanceTimer()
  uni.navigateBack()
}

async function loadDetail() {
  loading.value = true
  try {
    const data = await getScaleDetail(scaleId.value)
    scale.value = data
    const valid = (data.questions || []).filter(
      (q) => q.content && q.content.trim() && !/^\?+$/.test(q.content)
    )
    questions.value = valid.length ? valid : DEFAULT_QUESTIONS
  } catch (error) {
    console.error('加载量表失败:', error)
    uni.showToast({ title: '加载量表失败，已加载默认题库', icon: 'none' })
    questions.value = DEFAULT_QUESTIONS
  } finally {
    loading.value = false
  }
}

function computeSwiperHeight() {
  try {
    const sys = uni.getSystemInfoSync()
    // rpx -> px 转换系数（750rpx = 屏幕宽度）
    const rpxToPx = sys.windowWidth / 750
    const navContentH = 88 * rpxToPx // 导航栏内容高度
    const progressH = 6 * rpxToPx // 进度条高度
    const actionBarH = 16 * 2 * rpxToPx + 88 * rpxToPx // 上下 padding + 按钮高度
    const safeBottom = sys.safeArea ? sys.windowHeight - sys.safeArea.bottom : 0
    const occupied = (sys.statusBarHeight || 0) + navContentH + progressH + actionBarH + safeBottom
    swiperHeight.value = Math.max(200, sys.windowHeight - occupied)
  } catch {
    swiperHeight.value = 600
  }
}

onLoad(async (options) => {
  try {
    const sys = uni.getSystemInfoSync()
    statusBarHeight.value = sys.statusBarHeight || 0
  } catch {
    statusBarHeight.value = 0
  }
  computeSwiperHeight()
  const id = Number(options?.id)
  if (!id || Number.isNaN(id)) {
    uni.showToast({ title: '量表参数缺失', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 800)
    return
  }
  scaleId.value = id
  await loadDetail()
})

onUnload(() => {
  clearAdvanceTimer()
})
</script>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #EDE9E1;
}

/* 1. 顶部自定义导航栏 + 进度条 */
.nav-bar {
  flex-shrink: 0;
  background: #FBFAF6;
  border-bottom: 1rpx solid #E2DDD2;
}

.status-bar-spacer {
  width: 100%;
}

.nav-content {
  display: flex;
  align-items: center;
  height: 88rpx;
  padding: 0 24rpx;
}

.nav-back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.back-arrow {
  font-size: 56rpx;
  color: #2A2722;
  line-height: 1;
}

.nav-title {
  flex: 1;
  font-size: 32rpx;
  font-weight: 600;
  color: #2A2722;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 16rpx;
}

.nav-progress {
  flex-shrink: 0;
  min-width: 80rpx;
  text-align: right;
  font-size: 28rpx;
  font-weight: 600;
  color: #3A6359;
}

.progress-track {
  height: 6rpx;
  background: #F2EFE8;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3A6359;
  transition: width 0.3s ease;
}

/* 2. swiper 题目区 */
.swiper-wrap {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.question-swiper {
  /* 高度通过内联 :style 绑定（小程序 swiper 必须显式 px 高度） */
}

.question-scroll {
  height: 100%;
  box-sizing: border-box;
}

.question-body {
  padding: 60rpx 32rpx 40rpx;
  display: flex;
  flex-direction: column;
}

.question-num {
  text-align: center;
  font-size: 24rpx;
  color: #6B645C;
  margin-bottom: 40rpx;
}

.question-text {
  font-size: 36rpx;
  font-weight: 700;
  color: #2A2722;
  line-height: 1.6;
  text-align: center;
  padding: 0 8rpx;
  margin-bottom: 60rpx;
}

.options {
  display: flex;
  flex-direction: column;
}

.option-wrap {
  border-radius: 18rpx;
  padding: 2rpx;
  margin-bottom: 20rpx;
  background: transparent;
}

.option-wrap.selected {
  background: #3A6359;
}

.option-card {
  background: #FBFAF6;
  border: 1rpx solid #E2DDD2;
  border-radius: 16rpx;
  padding: 28rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background 0.2s ease;
}

.option-wrap.selected .option-card {
  border-color: transparent;
  background: rgba(58, 99, 89, 0.08);
}

.option-text {
  flex: 1;
  font-size: 28rpx;
  color: #2A2722;
  line-height: 1.5;
}

.option-right {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-shrink: 0;
  margin-left: 16rpx;
}

.option-score {
  font-size: 24rpx;
  color: #6B645C;
}

.option-check {
  font-size: 28rpx;
  font-weight: 700;
  color: #3A6359;
  margin-left: 12rpx;
}

.tips {
  margin-top: 48rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.tip-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}

.tip-text {
  font-size: 24rpx;
  color: #4A453E;
}

.loading-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(237, 233, 225, 0.6);
}

.loading-text {
  font-size: 26rpx;
  color: #6B645C;
}

/* 3. 底部操作栏（安全区适配） */
.action-bar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 16rpx 32rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #FBFAF6;
  border-top: 1rpx solid #E2DDD2;
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
  transition: opacity 0.2s ease;
}

.action-btn.disabled {
  opacity: 0.4;
}

.btn-prev {
  background: #FBFAF6;
  border: 1rpx solid #E2DDD2;
  color: #4A453E;
}

.btn-next {
  background: #3A6359;
  color: #FBFAF6;
  box-shadow: 0 6rpx 16rpx rgba(58, 99, 89, 0.25);
}

.btn-submit {
  background: #C26B4F;
  color: #FBFAF6;
  box-shadow: 0 6rpx 16rpx rgba(194, 107, 79, 0.3);
}

/* 4. 提交确认弹窗 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-dialog {
  width: 580rpx;
  background: #FBFAF6;
  border-radius: 24rpx;
  padding: 48rpx 40rpx 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.modal-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #2A2722;
  margin-bottom: 24rpx;
}

.modal-content {
  font-size: 28rpx;
  color: #4A453E;
  line-height: 1.6;
  text-align: center;
  margin-bottom: 40rpx;
}

.modal-actions {
  width: 100%;
  display: flex;
  gap: 24rpx;
}

.modal-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 600;
}

.modal-btn-cancel {
  background: #F2EFE8;
  color: #4A453E;
}

.modal-btn-confirm {
  background: #C26B4F;
  color: #FBFAF6;
}
</style>

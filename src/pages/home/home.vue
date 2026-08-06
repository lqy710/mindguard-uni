<template>
  <view class="home-page">
    <!-- 1. 问候区 -->
    <view class="header">
      <view class="header-left">
        <view class="avatar">
          <image
            v-if="userStore.userInfo?.avatar"
            class="avatar-img"
            :src="userStore.userInfo.avatar"
            mode="aspectFill"
          />
          <view v-else class="avatar-default">
            <text class="avatar-text">{{ nickname.charAt(0) }}</text>
          </view>
        </view>
        <view class="greeting">
          <text class="hello">{{ greetingText }}，{{ nickname }}</text>
          <text class="sub">愿今天被温柔以待</text>
        </view>
      </view>
      <view class="header-actions">
        <view class="icon-btn" @click="goSearch">
          <MIcon name="search" :size="20" color="#4A453E" />
        </view>
        <view class="icon-btn" @click="goMessages">
          <MIcon name="bell" :size="20" color="#4A453E" />
          <view v-if="notificationStore.unreadCount > 0" class="badge"></view>
        </view>
      </view>
    </view>

    <!-- 2. 情绪打卡 -->
    <view class="mood-card">
      <view class="mood-card-top">
        <text class="mood-card-title">今天感觉怎么样？</text>
        <text class="mood-card-date">{{ todayDate }}</text>
      </view>
      <view class="mood-picker">
        <view
          v-for="(mood, index) in moods"
          :key="index"
          class="mood-chip"
          :class="[`m-${index + 1}`, { active: selectedMood === index }]"
          @click="selectMood(index)"
        >
          <MIcon :name="mood.icon" :size="30" :color="moodFaceColor(index)" />
          <text class="name">{{ mood.label }}</text>
        </view>
      </view>
      <view class="mood-quick-note" @click="goDiary">
        <MIcon name="pen-line" :size="15" color="#4A7C6F" />
        <text class="note-text">选好心情后，可以写几句日记记录一下</text>
        <text class="note-btn">写日记</text>
      </view>
    </view>

    <!-- 动态贴士：选消极情绪后淡入 -->
    <view v-if="moodTip" class="mood-tip-dynamic" @click="onMoodTipClick">
      <MIcon name="lightbulb" :size="16" color="#6B5B9E" />
      <text class="mood-tip-text">{{ moodTip }}</text>
    </view>

    <!-- 3. 快捷行动（并排双卡） -->
    <view class="quick-actions">
      <view class="qa-card continue" @click="goAssessment">
        <view class="qa-icon">
          <MIcon name="clipboard-check" :size="20" color="#3A6359" />
        </view>
        <text class="qa-title">继续测评</text>
        <text class="qa-desc">专业量表 · 科学评估</text>
      </view>
      <view class="qa-card chat" @click="goChat">
        <view class="qa-icon">
          <MIcon name="sparkles" :size="20" color="#FBFAF6" />
        </view>
        <text class="qa-title">想聊聊吗？</text>
        <text class="qa-desc">AI 伙伴 · 随时倾听</text>
      </view>
    </view>

    <!-- 4. 心理工具（统一容器 + 主推 + 工具行 + 测评滑动条） -->
    <view class="section-block">
      <view class="section-head">
        <text class="section-title">心理工具</text>
        <text class="section-more" @click="goAssessmentList">全部 ›</text>
      </view>
      <view class="tools-card">
        <!-- 主推区 -->
        <view class="tools-primary" @click="goAssessment">
          <view class="tools-primary-top">
            <view class="tools-primary-icon">
              <MIcon name="clipboard-check" :size="21" color="#3A6359" />
            </view>
            <text class="tools-primary-title">心理测评</text>
          </view>
          <text class="tools-primary-desc">国际标准量表，科学评估抑郁、焦虑、压力等心理状态</text>
          <text class="tools-primary-meta">{{ scales.length || 12 }} 套专业量表 · 平均 5 分钟</text>
        </view>
        <!-- 子工具列表 -->
        <view class="tools-list">
          <view
            v-for="feature in features"
            :key="feature.title"
            class="tools-row"
            @click="feature.action"
          >
            <view class="tools-row-icon" :style="{ background: feature.tint }">
              <MIcon :name="feature.icon" :size="19" :color="feature.color" />
            </view>
            <view class="tools-row-body">
              <text class="tools-row-name">{{ feature.title }}</text>
              <text class="tools-row-desc">{{ feature.desc }}</text>
            </view>
            <MIcon name="chevron" :size="14" color="#6B645C" />
          </view>
        </view>
        <!-- 推荐测评横向滑动条 -->
        <view v-if="scales.length" class="tools-scales">
          <text class="tools-scales-label">推荐测评</text>
          <scroll-view scroll-x class="scale-scroll">
            <view class="scale-track">
              <view
                v-for="(scale, index) in scales"
                :key="scale.id"
                class="scale-mini"
                @click="goScaleDetail(scale.id)"
              >
                <view class="scale-mini-top">
                  <view class="scale-mini-icon" :style="{ background: scaleColor(index).bg }">
                    <MIcon :name="getScaleIcon(index)" :size="16" :color="scaleColor(index).fg" />
                  </view>
                  <text
                    class="scale-mini-badge"
                    :style="{ background: scaleColor(index).bg, color: scaleColor(index).fg }"
                  >{{ scale.estimatedTime || 3 }}min</text>
                </view>
                <text class="scale-mini-name text-clamp-2">{{ scale.name }}</text>
                <text class="scale-mini-meta">{{ formatUsers(index) }}人已完成</text>
              </view>
            </view>
          </scroll-view>
        </view>
        <view v-else-if="loading" class="tools-scales">
          <text class="tools-scales-label">推荐测评</text>
          <view class="scale-loading">
            <text class="loading-text">加载中...</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 5. 心灵成长（2 篇文章，横向布局） -->
    <view class="section-block">
      <view class="section-head">
        <text class="section-title">心灵成长</text>
        <text class="section-more" @click="goKnowledgeList">全部 ›</text>
      </view>
      <view class="article-list">
        <view
          v-for="(article, index) in articles"
          :key="article.id"
          class="article-row"
          @click="goArticleDetail(article.id)"
        >
          <view class="article-thumb" :style="{ background: articleTheme(index).tint }">
            <image
              v-if="article.coverImage"
              class="article-img"
              :src="article.coverImage"
              mode="aspectFill"
            />
            <MIcon
              v-else
              :name="articleTheme(index).icon"
              :size="26"
              :color="articleTheme(index).color"
            />
          </view>
          <view class="article-body">
            <text class="article-cat">{{ article.categoryName || '心理成长' }}</text>
            <text class="article-title text-clamp-2">{{ article.title }}</text>
            <text class="article-meta">{{ article.readTime || 5 }} 分钟阅读</text>
          </view>
        </view>
        <view v-if="!articles.length && loading" class="article-loading">
          <text class="loading-text">加载中...</text>
        </view>
      </view>
    </view>

    <!-- 6. 危机援助浮动按钮 -->
    <view class="crisis-fab" @click="callHotline">
      <MIcon name="phone" :size="24" color="#FBFAF6" />
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import MIcon from '@/components/MIcon.vue'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { getScaleList, type Scale } from '@/api/assessment'
import { getHotArticles, type Article } from '@/api/knowledge'
import { getHomeStats, type HomeStats } from '@/api/stats'

const userStore = useUserStore()
const notificationStore = useNotificationStore()

const badgeText = computed(() => {
  const count = notificationStore.unreadCount
  return count > 99 ? '99+' : String(count)
})

const scales = ref<Scale[]>([])
const articles = ref<Article[]>([])
const homeStats = ref<HomeStats | null>(null)
const loading = ref(false)
const selectedMood = ref(-1)

const nickname = computed(() => userStore.userInfo?.nickname || '朋友')

const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早安'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const todayDate = computed(() => {
  const d = new Date()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${d.getMonth() + 1}月${d.getDate()}日 ${weekdays[d.getDay()]}`
})

const moods = [
  { icon: 'laugh', label: '很好' },
  { icon: 'smile', label: '还行' },
  { icon: 'meh', label: '一般' },
  { icon: 'frown', label: '低落' },
  { icon: 'angry', label: '糟糕' }
]

const MOOD_FACE_COLORS = ['#4A7C6F', '#7BA897', '#B8862F', '#6B5B9E', '#C26B4F']
function moodFaceColor(index: number): string {
  return MOOD_FACE_COLORS[index] || '#4A453E'
}

const MOOD_TIPS = [
  '',
  '',
  '心情一般？花 2 分钟做个正念呼吸练习',
  '情绪有些低落，试试写日记梳理一下感受',
  '今天不太好，AI 伙伴随时在这里陪你聊聊'
]

const moodTip = computed(() => {
  if (selectedMood.value < 0) return ''
  return MOOD_TIPS[selectedMood.value] || ''
})

function onMoodTipClick() {
  if (selectedMood.value === 3) {
    goDiary()
  } else {
    goChat()
  }
}

const features = [
  {
    icon: 'notebook-pen',
    title: '情绪日记',
    desc: '记录每日心情变化',
    tint: '#F4E3DB',
    color: '#C26B4F',
    action: goDiary
  },
  {
    icon: 'lightbulb',
    title: '知识库',
    desc: '心理成长指南与科普',
    tint: '#E8E3F0',
    color: '#6B5B9E',
    action: goKnowledge
  },
  {
    icon: 'chart',
    title: '情绪报告',
    desc: '趋势分析与个性化建议',
    tint: '#F0E8D4',
    color: '#B8862F',
    action: goReport
  }
]

const SCALE_ICONS = ['heart', 'wind', 'activity', 'sparkles']
const SCALE_COLORS = [
  { bg: '#E6EEEA', fg: '#3A6359' },
  { bg: '#F4E3DB', fg: '#C26B4F' },
  { bg: '#E8E3F0', fg: '#6B5B9E' },
  { bg: '#F0E8D4', fg: '#B8862F' }
]

function getScaleIcon(index: number): string {
  return SCALE_ICONS[index % SCALE_ICONS.length]
}

function scaleColor(index: number) {
  return SCALE_COLORS[index % SCALE_COLORS.length]
}

const ARTICLE_THEMES = [
  { tint: '#F4E3DB', color: '#C26B4F', icon: 'sunrise' },
  { tint: '#E8E3F0', color: '#6B5B9E', icon: 'moon-star' },
  { tint: '#E6EEEA', color: '#3A6359', icon: 'leaf' }
]

function articleTheme(index: number) {
  return ARTICLE_THEMES[index % ARTICLE_THEMES.length]
}

function formatUsers(index: number): string {
  const base = homeStats.value?.assessmentCount
  if (base) {
    return Math.floor(base * (1 - index * 0.2)).toLocaleString()
  }
  return (12345 - index * 2000).toLocaleString()
}

function selectMood(index: number) {
  selectedMood.value = selectedMood.value === index ? -1 : index
}

async function loadData() {
  loading.value = true
  try {
    const [scaleList, articleList, stats] = await Promise.all([
      getScaleList(),
      getHotArticles(3),
      getHomeStats()
    ])
    scales.value = scaleList.slice(0, 6)
    articles.value = articleList.slice(0, 2)
    homeStats.value = stats
  } catch (error) {
    console.error('加载首页数据失败:', error)
  } finally {
    loading.value = false
  }
}

function goAssessment() {
  uni.switchTab({ url: '/pages/assessment/list' })
}
function goChat() {
  uni.switchTab({ url: '/pages/chat/chat' })
}
function goDiary() {
  uni.navigateTo({ url: '/pages/diary/diary' })
}
function goKnowledge() {
  uni.navigateTo({ url: '/pages/knowledge/list' })
}
function goReport() {
  uni.showToast({ title: '报告功能即将上线', icon: 'none' })
}
function goAssessmentList() {
  uni.switchTab({ url: '/pages/assessment/list' })
}
function goKnowledgeList() {
  uni.navigateTo({ url: '/pages/knowledge/list' })
}
function goScaleDetail(id: number) {
  uni.navigateTo({ url: `/pages/assessment/detail?id=${id}` })
}
function goArticleDetail(id: number) {
  uni.navigateTo({ url: `/pages/knowledge/detail?id=${id}` })
}
function goMessages() {
  const count = notificationStore.unreadCount
  if (count > 0) {
    uni.showToast({ title: `您有 ${count} 条未读消息`, icon: 'none' })
  } else {
    uni.showToast({ title: '暂无新消息', icon: 'none' })
  }
}
function goSearch() {
  uni.navigateTo({ url: '/pages/knowledge/list' })
}
function callHotline() {
  uni.makePhoneCall({ phoneNumber: '4001619995' })
}

onShow(() => {
  // 登录守卫：未登录跳转登录页
  if (!userStore.isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return
  }
  if (userStore.token && !userStore.userInfo) {
    userStore.fetchUserInfo().catch(() => {})
  }
  loadData()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #EDE9E1;
  padding-bottom: calc(160rpx + env(safe-area-inset-bottom));
}

/* ===== 1. 问候区 ===== */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 40rpx 40rpx;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24rpx;
  flex: 1;
  min-width: 0;
}

.avatar {
  width: 88rpx;
  height: 88rpx;
  border-radius: 999rpx;
  background: #E6EEEA;
  border: 3rpx solid #4A7C6F;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.avatar-default {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 34rpx;
  font-weight: 600;
  color: #3A6359;
}

.greeting {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.hello {
  font-size: 48rpx;
  font-weight: 700;
  color: #2A2722;
  line-height: 1.25;
  letter-spacing: -0.6rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sub {
  font-size: 26rpx;
  color: #6B645C;
  margin-top: 6rpx;
}

.header-actions {
  display: flex;
  gap: 16rpx;
  flex-shrink: 0;
}

.icon-btn {
  width: 80rpx;
  height: 80rpx;
  border-radius: 999rpx;
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  width: 14rpx;
  height: 14rpx;
  background: #C26B4F;
  border-radius: 50%;
  border: 3rpx solid #FBFAF6;
}

/* ===== 2. 情绪打卡 ===== */
.mood-card {
  margin: 0 40rpx;
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-radius: 32rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 16rpx rgba(42, 39, 34, 0.04), 0 2rpx 4rpx rgba(42, 39, 34, 0.03);
}

.mood-card-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 32rpx;
}

.mood-card-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #2A2722;
}

.mood-card-date {
  font-size: 24rpx;
  color: #6B645C;
}

.mood-picker {
  display: flex;
  justify-content: space-between;
  gap: 8rpx;
}

.mood-chip {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 8rpx;
  border-radius: 24rpx;
  border: 3rpx solid transparent;
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
}

.mood-chip:active {
  transform: scale(0.94);
}

.mood-chip .name {
  font-size: 24rpx;
  color: #4A453E;
  font-weight: 500;
}

/* 五级情绪配色 */
.mood-chip.m-1.active {
  background: #E6EEEA;
  border-color: #4A7C6F;
}
.mood-chip.m-1.active .name {
  color: #3A6359;
  font-weight: 600;
}
.mood-chip.m-2.active {
  background: #EDF3F0;
  border-color: #7BA897;
}
.mood-chip.m-2.active .name {
  color: #5A8A76;
  font-weight: 600;
}
.mood-chip.m-3.active {
  background: #F0E8D4;
  border-color: #B8862F;
}
.mood-chip.m-3.active .name {
  color: #946823;
  font-weight: 600;
}
.mood-chip.m-4.active {
  background: #E8E3F0;
  border-color: #6B5B9E;
}
.mood-chip.m-4.active .name {
  color: #54477A;
  font-weight: 600;
}
.mood-chip.m-5.active {
  background: #F4E3DB;
  border-color: #C26B4F;
}
.mood-chip.m-5.active .name {
  color: #9C5A45;
  font-weight: 600;
}

.mood-quick-note {
  margin-top: 32rpx;
  padding-top: 24rpx;
  border-top: 2rpx dashed #E2DDD2;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.note-text {
  font-size: 26rpx;
  color: #4A453E;
  flex: 1;
}

.note-btn {
  font-size: 24rpx;
  color: #3A6359;
  background: #E6EEEA;
  padding: 10rpx 24rpx;
  border-radius: 999rpx;
  font-weight: 600;
  flex-shrink: 0;
}

/* 动态贴士 */
.mood-tip-dynamic {
  margin: 24rpx 40rpx 0;
  padding: 24rpx 32rpx;
  background: #E8E3F0;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.mood-tip-text {
  font-size: 24rpx;
  color: #6B5B9E;
  font-weight: 500;
  line-height: 1.4;
  flex: 1;
}

/* ===== 3. 快捷行动（并排双卡） ===== */
.quick-actions {
  display: flex;
  gap: 24rpx;
  margin: 48rpx 40rpx 0;
}

.qa-card {
  flex: 1;
  border-radius: 32rpx;
  padding: 32rpx;
  transition: transform 0.15s ease;
}

.qa-card:active {
  transform: scale(0.97);
}

.qa-card.continue {
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  box-shadow: 0 2rpx 6rpx rgba(42, 39, 34, 0.05);
}

.qa-card.chat {
  background: #3A6359;
  box-shadow: 0 8rpx 24rpx rgba(58, 99, 89, 0.15);
}

.qa-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.qa-card.continue .qa-icon {
  background: #E6EEEA;
}

.qa-card.chat .qa-icon {
  background: rgba(255, 255, 255, 0.12);
}

.qa-title {
  font-size: 28rpx;
  font-weight: 600;
  line-height: 1.3;
}

.qa-card.continue .qa-title {
  color: #2A2722;
}

.qa-card.chat .qa-title {
  color: #FBFAF6;
}

.qa-desc {
  font-size: 24rpx;
  margin-top: 4rpx;
  line-height: 1.3;
}

.qa-card.continue .qa-desc {
  color: #6B645C;
}

.qa-card.chat .qa-desc {
  color: rgba(251, 250, 246, 0.7);
}

/* ===== 通用 Section ===== */
.section-block {
  margin-top: 64rpx;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 0 40rpx 24rpx;
}

.section-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #2A2722;
}

.section-more {
  font-size: 26rpx;
  color: #3A6359;
  font-weight: 500;
}

/* ===== 4. 心理工具 ===== */
.tools-card {
  margin: 0 40rpx;
  background: #FBFAF6;
  border: 2rpx solid #E2DDD2;
  border-radius: 32rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(42, 39, 34, 0.04), 0 2rpx 4rpx rgba(42, 39, 34, 0.03);
}

.tools-primary {
  padding: 32rpx 40rpx;
  background: #E6EEEA;
}

.tools-primary-top {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-bottom: 4rpx;
}

.tools-primary-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
  background: #FBFAF6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tools-primary-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #2A2722;
}

.tools-primary-desc {
  font-size: 26rpx;
  color: #4A453E;
  margin-top: 8rpx;
  line-height: 1.4;
}

.tools-primary-meta {
  font-size: 24rpx;
  color: #3A6359;
  margin-top: 16rpx;
  font-weight: 600;
}

.tools-list {
  padding: 0 40rpx;
}

.tools-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 0;
  border-bottom: 2rpx solid #E2DDD2;
}

.tools-row:last-child {
  border-bottom: none;
}

.tools-row-icon {
  width: 76rpx;
  height: 76rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tools-row-body {
  flex: 1;
  min-width: 0;
}

.tools-row-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #2A2722;
}

.tools-row-desc {
  font-size: 24rpx;
  color: #6B645C;
  margin-top: 4rpx;
}

/* 推荐测评横向滑动条 */
.tools-scales {
  padding: 24rpx 0 32rpx;
  border-top: 2rpx solid #E2DDD2;
}

.tools-scales-label {
  font-size: 24rpx;
  color: #6B645C;
  font-weight: 600;
  letter-spacing: 1rpx;
  padding: 0 40rpx 16rpx;
  display: block;
}

.scale-scroll {
  white-space: nowrap;
  width: 100%;
}

.scale-track {
  display: inline-block;
  padding: 0 40rpx;
}

.scale-mini {
  display: inline-block;
  width: 300rpx;
  vertical-align: top;
  white-space: normal;
  margin-right: 24rpx;
  padding: 24rpx;
  background: #F2EFE8;
  border-radius: 16rpx;
  box-sizing: border-box;
}

.scale-mini-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.scale-mini-icon {
  width: 60rpx;
  height: 60rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scale-mini-badge {
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  font-weight: 600;
}

.scale-mini-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #2A2722;
  line-height: 1.3;
  min-height: 68rpx;
}

.scale-mini-meta {
  font-size: 24rpx;
  color: #6B645C;
  margin-top: 4rpx;
}

.scale-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120rpx;
}

.loading-text {
  font-size: 26rpx;
  color: #6B645C;
}

/* ===== 5. 心灵成长 ===== */
.article-list {
  padding: 0 40rpx;
}

.article-row {
  display: flex;
  gap: 32rpx;
  padding: 32rpx 0;
  border-bottom: 2rpx solid #E2DDD2;
}

.article-row:last-child {
  border-bottom: none;
}

.article-thumb {
  width: 128rpx;
  height: 128rpx;
  border-radius: 16rpx;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.article-img {
  width: 100%;
  height: 100%;
}

.article-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  justify-content: center;
}

.article-cat {
  font-size: 24rpx;
  font-weight: 600;
  color: #3A6359;
  letter-spacing: 1rpx;
}

.article-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #2A2722;
  line-height: 1.4;
}

.article-meta {
  font-size: 24rpx;
  color: #6B645C;
}

.article-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 160rpx;
}

/* ===== 6. 危机援助浮标 ===== */
.crisis-fab {
  position: fixed;
  right: 32rpx;
  bottom: calc(180rpx + env(safe-area-inset-bottom));
  z-index: 40;
  width: 96rpx;
  height: 96rpx;
  border-radius: 999rpx;
  background: #C26B4F;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(194, 107, 79, 0.25);
  transition: transform 0.15s ease;
}

.crisis-fab:active {
  transform: scale(0.92);
}

/* ===== 通用：两行截断 ===== */
.text-clamp-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

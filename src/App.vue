<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useNotificationStore } from '@/stores/notification'

onLaunch(() => {
  console.log('MindGuard App Launch')
  // 初始化全局通知：订阅 WebSocket 推送（已登录则建立连接）
  useNotificationStore().init()
})
onShow(() => {
  console.log('App Show')
})
onHide(() => {
  console.log('App Hide')
})
</script>

<style>
/* 全局样式 —— MindGuard 主题 */
page {
  background-color: #f6f8fb;
  color: #16263a;
  font-size: 28rpx;
  line-height: 1.6;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 主题色变量（uni-app 小程序不支持 CSS 变量在组件间继承，这里仅 H5 生效，小程序用 uni.scss） */
view, text {
  box-sizing: border-box;
}

/* 通用工具类 */
.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 32rpx;
  margin: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(22, 38, 58, 0.06);
}

.text-muted {
  color: #62748a;
  font-size: 24rpx;
}

.text-accent {
  color: #2c8a7a;
}
</style>

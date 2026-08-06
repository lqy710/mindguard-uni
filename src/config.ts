/**
 * 全局配置：后端服务地址
 *
 * 拆成两个变量，因后端路径前缀不一致：
 * - HTTP 接口：Controller 统一 /api 前缀（如 /api/auth/login）
 * - WebSocket：根路径 /ws（不带 /api，见后端 SecurityConfig 放行 /ws/**）
 *
 * 因此：
 * - BASE_URL      —— 后端服务根地址，仅用于 WebSocket 推导 wss 地址（utils/websocket.ts）
 * - API_BASE_URL  —— HTTP API 基础地址（= BASE_URL + '/api'），utils/request.ts 拼接业务接口
 *
 * 改这里即可全局生效，禁止在业务层再硬编码后端地址。
 */
function resolveUrls(): { baseUrl: string; apiBaseUrl: string } {
  // 非H5平台（微信小程序等）
  // ⚠️ 当前为本地联调地址，微信开发者工具需勾选
  //   「不校验合法域名、web-view、TLS 版本以及 HTTPS 证书」
  //   - 真机预览请改成本机局域网 IP，如 http://192.168.x.x:8080
  //   - 上线前必须替换为真实 HTTPS 后端地址，并在小程序后台
  //     「开发管理 → 服务器域名」配置 request/socket 合法域名
  let baseUrl = 'http://localhost:8080'
  let apiBaseUrl = baseUrl + '/api'
  // #ifdef H5
  // H5 端：VITE_API_BASE_URL 作为完整 API 地址（含 /api），便于 vite proxy 联调
  const envApi = import.meta.env.VITE_API_BASE_URL as string | undefined
  if (envApi) {
    apiBaseUrl = envApi
    baseUrl = envApi.replace(/\/api\/?$/, '')
  } else {
    baseUrl = 'http://localhost:8080'
    apiBaseUrl = baseUrl + '/api'
  }
  // #endif
  return { baseUrl, apiBaseUrl }
}

const { baseUrl, apiBaseUrl } = resolveUrls()

/** 后端服务根地址（仅 WebSocket 推导用，不含 /api 前缀） */
export const BASE_URL: string = baseUrl

/** HTTP API 基础地址（后端 Controller 统一 /api 前缀，request.ts 使用） */
export const API_BASE_URL: string = apiBaseUrl

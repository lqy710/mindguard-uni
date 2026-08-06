/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 后端接口基础地址（H5 端通过 .env 的 VITE_API_BASE_URL 注入，须以 VITE_ 前缀暴露给客户端） */
  readonly VITE_API_BASE_URL?: string
}

declare module '*.vue' {
  import { DefineComponent } from 'vue'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>
  export default component
}

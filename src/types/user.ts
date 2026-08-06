export interface UserInfo {
  id: number
  username: string
  nickname: string
  avatar: string
  gender: number
  age: number
  role: string
  status: number
  createdAt: string
  email?: string
  phone?: string
  birthday?: string
}

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  nickname?: string
  gender?: number
  age?: number
}

export interface LoginResult {
  token: string
  user: UserInfo
  expiresAt: string
}

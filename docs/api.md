> **历史文档（已迁移）**：本文档属于 MindGuard 旧版 Web 项目（`legacy/`，Vue3 Web + Spring Boot + Flask），**不再维护**。当前用户端已重构为 uni-app（微信小程序 + H5），实际实现见仓库 `src/` 目录；开发规则与当前设计系统见 `.trae/rules/mindguard-migration.md`。本文件仅作历史回溯参考。

# API接口文档

## 文档信息

| 项目名称 | 基于AI的心理健康检测与辅助系统 |
|---------|------------------------------|
| 文档版本 | V2.0 |
| 编写日期 | 2026-03-09 |
| 编写人 | [林秋颜] |

---

## 一、接口规范

### 1.1 基础信息

- **基础URL**: `http://localhost:8080/api`
- **AI服务URL**: `http://localhost:5000/api`
- **认证方式**: JWT Token
- **请求格式**: JSON
- **响应格式**: JSON

### 1.2 统一响应格式

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 1.3 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 二、AI服务接口

### 2.1 情感分析

**接口地址**: `POST http://localhost:5000/api/emotion/analyze`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| text | String | 是 | 待分析的文本内容 |

**请求示例**:
```json
{
  "text": "今天心情很好，阳光明媚"
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "sentiment_score": 0.85,
    "emotion_type": "positive",
    "keywords": ["心情", "阳光", "明媚"]
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| sentiment_score | Float | 情感分数（0-1），大于0.6为积极，小于0.4为消极 |
| emotion_type | String | 情绪类型：positive/negative/neutral |
| keywords | Array | 关键词列表（最多5个） |

### 2.2 AI对话

**接口地址**: `POST http://localhost:5000/api/chat/reply`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| message | String | 是 | 用户消息 |
| context | Array | 否 | 对话上下文（最多保留最近10条） |

**请求示例**:
```json
{
  "message": "我最近感觉很焦虑",
  "context": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！我是你的心理健康助手..."}
  ]
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "reply": "焦虑是很常见的情绪。你可以试着：1. 深呼吸几次...",
    "confidence": 0.95
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| reply | String | AI回复内容 |
| confidence | Float | 回复置信度（0-1） |

### 2.3 风险评估

**接口地址**: `POST http://localhost:5000/api/risk/assess`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| userData | Object | 是 | 用户数据 |
| userData.score | Number | 是 | 测评得分 |
| userData.history | Array | 否 | 历史记录 |

**请求示例**:
```json
{
  "userData": {
    "score": 15,
    "history": [
      {"risk_level": "medium", "score": 12},
      {"risk_level": "low", "score": 8}
    ]
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "risk_level": "medium",
    "risk_factors": ["测评得分中等"],
    "recommendation": "建议寻求专业心理咨询，与家人朋友保持沟通..."
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| risk_level | String | 风险等级：low/medium/high |
| risk_factors | Array | 风险因素列表 |
| recommendation | String | 建议内容 |

### 2.4 健康检查

**接口地址**: `GET http://localhost:5000/health`

**响应示例**:
```json
{
  "status": "ok",
  "service": "python-ai-service"
}
```

---

## 三、用户认证接口

### 3.1 用户注册

**接口地址**: `POST /api/auth/register`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 是 | 用户名（3-20字符） |
| password | String | 是 | 密码（6-20字符） |
| nickname | String | 否 | 昵称 |
| gender | Integer | 否 | 性别（0-未知，1-男，2-女） |
| age | Integer | 否 | 年龄 |

**请求示例**:
```json
{
  "username": "testuser",
  "password": "123456",
  "nickname": "测试用户",
  "gender": 1,
  "age": 25
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "nickname": "测试用户",
    "gender": 1,
    "age": 25,
    "role": "USER",
    "status": 1,
    "createdAt": "2026-03-09T10:30:00"
  }
}
```

### 3.2 用户登录

**接口地址**: `POST /api/auth/login`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | String | 是 | 用户名 |
| password | String | 是 | 密码 |

**请求示例**:
```json
{
  "username": "testuser",
  "password": "123456"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "testuser",
      "nickname": "测试用户",
      "avatar": null,
      "gender": 1,
      "age": 25,
      "role": "USER",
      "status": 1,
      "createdAt": "2026-03-09T10:30:00"
    },
    "expiresAt": "2026-03-10T10:30:00"
  }
}
```

### 3.3 获取当前用户信息

**接口地址**: `GET /api/auth/me`

**请求头**:
```
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "testuser",
    "nickname": "测试用户",
    "avatar": null,
    "gender": 1,
    "age": 25,
    "role": "USER",
    "status": 1,
    "createdAt": "2026-03-09T10:30:00"
  }
}
```

---

## 四、用户接口

### 4.1 获取用户统计数据

**接口地址**: `GET /api/user/stats`

**请求头**:
```
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "assessmentCount": 10,
    "diaryCount": 30,
    "chatSessionCount": 5
  }
}
```

### 4.2 获取用户信息

**接口地址**: `GET /api/user/{id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | 是 | 用户ID |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "testuser",
    "nickname": "测试用户",
    "avatar": null,
    "gender": 1,
    "age": 25,
    "role": "USER",
    "status": 1,
    "createdAt": "2026-03-09T10:30:00"
  }
}
```

### 4.3 更新个人信息

**接口地址**: `PUT /api/user/profile`

**请求头**:
```
Authorization: Bearer {token}
```

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| nickname | String | 否 | 昵称 |
| avatar | String | 否 | 头像URL |
| gender | Integer | 否 | 性别 |
| age | Integer | 否 | 年龄 |

**请求示例**:
```json
{
  "nickname": "新昵称",
  "gender": 1,
  "age": 26
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "testuser",
    "nickname": "新昵称",
    "avatar": null,
    "gender": 1,
    "age": 26,
    "role": "USER",
    "status": 1,
    "createdAt": "2026-03-09T10:30:00"
  }
}
```

---

## 五、心理测评接口

### 5.1 获取量表列表

**接口地址**: `GET /api/assessment/scales`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| category | String | 否 | 量表分类 |

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "PHQ-9抑郁症筛查量表",
      "description": "用于抑郁症筛查的量表",
      "questionCount": 9
    },
    {
      "id": 2,
      "name": "GAD-7焦虑症筛查量表",
      "description": "用于焦虑症筛查的量表",
      "questionCount": 7
    }
  ]
}
```

### 5.2 获取量表详情

**接口地址**: `GET /api/assessment/scales/{scaleId}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| scaleId | Long | 是 | 量表ID |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "PHQ-9抑郁症筛查量表",
    "description": "用于抑郁症筛查的量表",
    "questions": [
      {
        "id": 1,
        "content": "做事时提不起劲或没有兴趣",
        "orderNum": 1,
        "options": [
          {"id": 1, "content": "完全不会", "score": 0},
          {"id": 2, "content": "好几天", "score": 1},
          {"id": 3, "content": "一半以上的天数", "score": 2},
          {"id": 4, "content": "几乎每天", "score": 3}
        ]
      }
    ]
  }
}
```

### 5.3 提交测评答案

**接口地址**: `POST /api/assessment/submit`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| scaleId | Long | 是 | 量表ID |
| answers | Array | 是 | 答案列表 |
| answers[].questionId | Long | 是 | 题目ID |
| answers[].answer | Integer | 是 | 答案分数 |

**请求示例**:
```json
{
  "scaleId": 1,
  "answers": [
    {"questionId": 1, "answer": 1},
    {"questionId": 2, "answer": 2},
    {"questionId": 3, "answer": 0}
  ]
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "assessmentId": 1,
    "scaleId": 1,
    "scaleName": "PHQ-9抑郁症筛查量表",
    "totalScore": 5,
    "riskLevel": "low",
    "riskText": "无抑郁症状",
    "interpretation": "您的心理状态良好，继续保持积极的生活态度。",
    "suggestion": "建议保持良好的作息习惯，适当运动。",
    "createdAt": "2026-03-09T10:30:00"
  }
}
```

### 5.4 获取测评报告

**接口地址**: `GET /api/assessment/report/{assessmentId}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| assessmentId | Long | 是 | 测评ID |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "assessmentId": 1,
    "scaleId": 1,
    "scaleName": "PHQ-9抑郁症筛查量表",
    "totalScore": 5,
    "riskLevel": "low",
    "riskText": "无抑郁症状",
    "interpretation": "您的心理状态良好，继续保持积极的生活态度。",
    "suggestion": "建议保持良好的作息习惯，适当运动。",
    "createdAt": "2026-03-09T10:30:00"
  }
}
```

### 5.5 获取测评历史

**接口地址**: `GET /api/assessment/history`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current | Integer | 否 | 当前页码，默认1 |
| size | Integer | 否 | 每页条数，默认10 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "records": [
      {
        "assessmentId": 1,
        "scaleId": 1,
        "scaleName": "PHQ-9抑郁症筛查量表",
        "totalScore": 5,
        "riskLevel": "low",
        "riskText": "无抑郁症状",
        "createdAt": "2026-03-09T10:30:00"
      }
    ],
    "total": 10,
    "current": 1,
    "size": 10
  }
}
```

---

## 六、情绪日记接口

### 6.1 创建日记

**接口地址**: `POST /api/diary`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | String | 是 | 日记内容 |
| emotionType | String | 是 | 情绪类型 |
| emotionScore | Integer | 是 | 情绪分数（1-10） |

**请求示例**:
```json
{
  "content": "今天心情很好，阳光明媚，工作也很顺利。",
  "emotionType": "happy",
  "emotionScore": 8
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "emotionType": "happy",
    "emotionScore": 8,
    "content": "今天心情很好，阳光明媚，工作也很顺利。",
    "sentimentScore": 0.85,
    "aiAnalysis": "您今天的心情很不错，继续保持积极乐观的心态...",
    "createdAt": "2026-03-09T10:30:00"
  }
}
```

### 6.2 获取日记详情

**接口地址**: `GET /api/diary/{id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | 是 | 日记ID |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "emotionType": "happy",
    "emotionScore": 8,
    "content": "今天心情很好，阳光明媚，工作也很顺利。",
    "sentimentScore": 0.85,
    "aiAnalysis": "您今天的心情很不错，继续保持积极乐观的心态...",
    "createdAt": "2026-03-09T10:30:00"
  }
}
```

### 6.3 获取日记列表

**接口地址**: `GET /api/diary/page`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current | Integer | 否 | 当前页码，默认1 |
| size | Integer | 否 | 每页条数，默认10 |
| emotionType | String | 否 | 情绪类型筛选 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "records": [
      {
        "id": 1,
        "emotionType": "happy",
        "emotionScore": 8,
        "content": "今天心情很好...",
        "sentimentScore": 0.85,
        "aiAnalysis": "您今天的心情很不错...",
        "createdAt": "2026-03-09T10:30:00"
      }
    ],
    "total": 30,
    "current": 1,
    "size": 10
  }
}
```

### 6.4 删除日记

**接口地址**: `DELETE /api/diary/{id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | 是 | 日记ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功"
}
```

### 6.5 获取日记统计

**接口地址**: `GET /api/diary/statistics`

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "totalCount": 30,
    "avgEmotionScore": 6.5,
    "emotionDistribution": {
      "happy": 15,
      "neutral": 10,
      "sad": 5
    }
  }
}
```

### 6.6 获取情绪趋势

**接口地址**: `GET /api/diary/trend`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | Integer | 否 | 统计天数，默认30 |

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "date": "2026-03-01",
      "avgScore": 7.5,
      "count": 2
    },
    {
      "date": "2026-03-02",
      "avgScore": 6.0,
      "count": 1
    }
  ]
}
```

---

## 七、AI聊天接口

### 7.1 创建新会话

**接口地址**: `POST /api/chat/session`

**请求头**:
```
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "data": 1
}
```

**响应字段说明**: 返回新创建的会话ID

### 7.2 发送消息

**接口地址**: `POST /api/chat/send`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| message | String | 是 | 消息内容 |
| sessionId | Long | 否 | 会话ID（首次可不传，会自动创建） |

**请求示例**:
```json
{
  "message": "我最近感觉很焦虑",
  "sessionId": 1
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 2,
    "role": "assistant",
    "content": "焦虑是很常见的情绪。你可以试着：1. 深呼吸几次...",
    "sentimentScore": 0.75,
    "createdAt": "2026-03-09T10:30:05"
  }
}
```

### 7.3 获取会话消息列表

**接口地址**: `GET /api/chat/session/{sessionId}/messages`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sessionId | Long | 是 | 会话ID |

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "role": "user",
      "content": "我最近感觉很焦虑",
      "sentimentScore": 0.3,
      "createdAt": "2026-03-09T10:30:00"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "焦虑是很常见的情绪...",
      "sentimentScore": 0.75,
      "createdAt": "2026-03-09T10:30:05"
    }
  ]
}
```

### 7.4 获取用户会话列表

**接口地址**: `GET /api/chat/sessions`

**响应示例**:
```json
{
  "code": 200,
  "data": [1, 2, 3]
}
```

**响应字段说明**: 返回用户所有会话ID列表

### 7.5 删除会话

**接口地址**: `DELETE /api/chat/session/{sessionId}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sessionId | Long | 是 | 会话ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功"
}
```

---

## 八、知识库接口

### 8.1 获取文章列表

**接口地址**: `GET /api/knowledge/articles`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current | Integer | 否 | 当前页码，默认1 |
| size | Integer | 否 | 每页条数，默认10 |
| categoryId | Long | 否 | 分类ID |
| keyword | String | 否 | 搜索关键词 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "records": [
      {
        "id": 1,
        "categoryId": 1,
        "categoryName": "心理健康",
        "title": "如何缓解焦虑",
        "summary": "本文介绍了几种有效的缓解焦虑的方法...",
        "coverImage": "https://example.com/cover.jpg",
        "author": "心理专家",
        "viewCount": 1000,
        "createdAt": "2026-03-01T10:00:00"
      }
    ],
    "total": 50,
    "current": 1,
    "size": 10
  }
}
```

### 8.2 获取文章详情

**接口地址**: `GET /api/knowledge/article/{id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | 是 | 文章ID |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "categoryId": 1,
    "categoryName": "心理健康",
    "title": "如何缓解焦虑",
    "summary": "本文介绍了几种有效的缓解焦虑的方法...",
    "coverImage": "https://example.com/cover.jpg",
    "author": "心理专家",
    "viewCount": 1001,
    "createdAt": "2026-03-01T10:00:00"
  }
}
```

### 8.3 获取热门文章

**接口地址**: `GET /api/knowledge/hot`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| limit | Integer | 否 | 返回数量，默认5 |

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "categoryId": 1,
      "categoryName": "心理健康",
      "title": "如何缓解焦虑",
      "summary": "本文介绍了几种有效的缓解焦虑的方法...",
      "coverImage": "https://example.com/cover.jpg",
      "author": "心理专家",
      "viewCount": 1000,
      "createdAt": "2026-03-01T10:00:00"
    }
  ]
}
```

---

## 九、统计接口

### 9.1 获取首页统计数据

**接口地址**: `GET /api/stats/home`

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "userCount": 1000,
    "assessmentCount": 5000,
    "diaryCount": 10000,
    "articleCount": 200,
    "scaleCount": 10
  }
}
```

---

## 十、管理端接口

### 10.1 获取用户列表

**接口地址**: `GET /api/user/admin/page`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current | Integer | 否 | 当前页码，默认1 |
| size | Integer | 否 | 每页条数，默认10 |
| keyword | String | 否 | 搜索关键词（用户名/昵称） |
| status | Integer | 否 | 状态筛选（1-正常，0-禁用） |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "records": [
      {
        "id": 1,
        "username": "testuser",
        "nickname": "测试用户",
        "avatar": null,
        "gender": 1,
        "age": 25,
        "role": "USER",
        "status": 1,
        "createdAt": "2026-03-01T10:00:00"
      }
    ],
    "total": 100,
    "current": 1,
    "size": 10
  }
}
```

### 10.2 更新用户状态

**接口地址**: `PUT /api/user/admin/{id}/status`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | 是 | 用户ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | Integer | 是 | 状态（1-正常，0-禁用） |

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功"
}
```

### 10.3 获取预警列表

**接口地址**: `GET /api/admin/warnings`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| current | Integer | 否 | 当前页码，默认1 |
| size | Integer | 否 | 每页条数，默认10 |
| status | String | 否 | 处理状态：PENDING/HANDLED |
| riskLevel | String | 否 | 风险等级：low/medium/high |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "records": [
      {
        "id": 1,
        "userId": 1,
        "username": "testuser",
        "riskLevel": "high",
        "triggerSource": "ASSESSMENT",
        "triggerContent": "PHQ-9测评得分：25分",
        "status": "PENDING",
        "handlerName": null,
        "handleNote": null,
        "createdAt": "2026-03-09T10:00:00",
        "handledAt": null
      }
    ],
    "total": 20,
    "current": 1,
    "size": 10
  }
}
```

### 10.4 获取预警详情

**接口地址**: `GET /api/admin/warning/{id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | 是 | 预警ID |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "userId": 1,
    "username": "testuser",
    "riskLevel": "high",
    "triggerSource": "ASSESSMENT",
    "triggerContent": "PHQ-9测评得分：25分",
    "status": "PENDING",
    "handlerName": null,
    "handleNote": null,
    "createdAt": "2026-03-09T10:00:00",
    "handledAt": null
  }
}
```

### 10.5 处理预警

**接口地址**: `PUT /api/admin/warning/{id}/handle`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | 是 | 预警ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| handleNote | String | 是 | 处理备注 |

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功"
}
```

### 10.6 获取仪表盘统计数据

**接口地址**: `GET /api/admin/dashboard`

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "totalUsers": 1000,
    "todayNewUsers": 50,
    "totalAssessments": 5000,
    "todayAssessments": 100,
    "totalDiaries": 10000,
    "todayDiaries": 200,
    "pendingWarnings": 20,
    "highRiskUsers": 10,
    "assessmentTrend": [
      {"label": "2026-03-01", "value": 80},
      {"label": "2026-03-02", "value": 95}
    ],
    "emotionDistribution": [
      {"label": "happy", "value": 500},
      {"label": "neutral", "value": 300},
      {"label": "sad", "value": 200}
    ]
  }
}
```

---

## 十一、WebSocket接口

### 11.1 实时通知

**连接地址**: `ws://localhost:8080/ws`

**认证**: 在连接URL中携带token
```
ws://localhost:8080/ws?token={jwt_token}
```

**消息格式**:
```json
{
  "type": "NOTIFICATION",
  "data": {
    "title": "新消息",
    "content": "您有一条新的测评结果",
    "timestamp": "2026-03-09T10:30:00"
  }
}
```

**消息类型说明**:

| 类型 | 说明 |
|------|------|
| CHAT | 聊天消息通知 |
| WARNING | 预警通知 |
| DATA_UPDATE | 数据更新通知 |

---

## 文档修订记录

| 版本 | 日期 | 修订内容 | 修订人 |
|------|------|---------|--------|
| V1.0 | 2026-02-26 | 初始版本 | 林秋颜 |
| V1.1 | 2026-03-09 | 新增AI服务接口文档，更新智谱AI相关接口 | 林秋颜 |
| V2.0 | 2026-03-09 | 全面更新接口文档，同步实际代码实现：<br>- 更新用户认证接口（注册字段、登录响应、用户信息路径）<br>- 新增用户接口模块<br>- 更新测评接口（新增量表列表、报告详情、答案格式）<br>- 更新日记接口（新增详情、删除、统计、趋势接口）<br>- 更新聊天接口（新增会话管理相关接口）<br>- 新增知识库接口模块<br>- 更新管理端接口（预警详情、处理预警、仪表盘统计）<br>- 更新所有响应字段与实际代码保持一致 | 林秋颜 |

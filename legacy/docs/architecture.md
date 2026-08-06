> **历史文档（已迁移）**：本文档属于 MindGuard 旧版 Web 项目（`legacy/`，Vue3 Web + Spring Boot + Flask），**不再维护**。当前用户端已重构为 uni-app（微信小程序 + H5），实际实现见仓库 `src/` 目录；开发规则与当前设计系统见 `.trae/rules/mindguard-migration.md`。本文件仅作历史回溯参考。

# 技术架构文档

## 文档信息

| 项目名称 | 基于AI的心理健康检测与辅助系统 |
|---------|------------------------------|
| 文档版本 | V1.1 |
| 编写日期 | 2026-03-09 |
| 编写人 | [林秋颜] |

---

## 一、架构概述

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              客户端层                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │     PC浏览器     │  │    移动浏览器    │  │     平板设备     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              前端层                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Vue 3 + TypeScript                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ 用户端UI  │ │ 管理端UI │ │ 公共组件  │ │ 状态管理  │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTPS
┌─────────────────────────────────────────────────────────────────────────┐
│                              网关层                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Nginx 反向代理                               │   │
│  │            - 静态资源服务  - 负载均衡  - SSL终止                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              后端层                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Spring Boot 3.2                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │Controller│ │ Service  │ │  Mapper  │ │  Entity  │           │   │
│  │  │   层     │ │    层    │ │    层    │ │    层    │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │
│  │                                                                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ Security │ │   JWT    │ │ MyBatis  │ │  Redis   │           │   │
│  │  │  安全框架 │ │  认证    │ │  Plus    │ │  缓存    │           │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│      数据层         │  │      缓存层         │  │      AI服务层       │
│  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │
│  │   MySQL 8.0   │  │  │  │   Redis 7.x   │  │  │  │ Python Flask  │  │
│  │   数据持久化   │  │  │  │   会话/缓存   │  │  │  │   AI模型服务   │  │
│  └───────────────┘  │  │  └───────────────┘  │  │  └───────────────┘  │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

### 1.2 技术选型总览

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **前端** | Vue | 3.4+ | 渐进式JavaScript框架 |
| | TypeScript | 5.x | 类型安全的JavaScript超集 |
| | Element Plus | 2.x | Vue 3 UI组件库 |
| | Pinia | 2.x | Vue 3 状态管理 |
| | Vue Router | 4.x | Vue 3 路由管理 |
| | Axios | 1.x | HTTP客户端 |
| | ECharts | 5.x | 数据可视化库 |
| | Vite | 5.x | 前端构建工具 |
| **后端** | Java | 17 | 编程语言 |
| | Spring Boot | 3.2 | 应用框架 |
| | Spring Security | 6.x | 安全框架 |
| | JWT | - | 身份认证 |
| | MyBatis-Plus | 3.5 | ORM框架 |
| | MySQL | 8.0 | 关系数据库 |
| | Redis | 7.x | 缓存数据库 |
| | Maven | 3.8+ | 项目管理工具 |
| **AI服务** | Python | 3.9+ | 编程语言 |
| | Flask | 3.x | Web框架 |
| | SnowNLP | - | 中文情感分析 |
| | 智谱AI GLM-4-Flash | - | AI对话服务（免费） |
| | Requests | 2.28+ | HTTP客户端 |
| **部署** | Nginx | 1.24+ | 反向代理服务器 |
| | Docker | 24+ | 容器化部署 |

---

## 二、AI服务架构

### 2.1 AI服务目录结构

```
ai-service/
├── services/                    # AI服务
│   ├── __init__.py
│   ├── emotion_analysis.py      # 情感分析服务
│   ├── chat_service.py          # 对话服务
│   └── risk_assessment.py       # 风险评估服务
│
├── config.py                    # 配置文件
├── app.py                       # Flask入口
├── requirements.txt             # 依赖配置
└── README.md                    # 服务说明
```

### 2.2 AI服务架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Flask 应用 (端口5000)                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                   路由层                          │   │
│  │  /api/emotion/analyze    情感分析                 │   │
│  │  /api/chat/reply         AI对话                   │   │
│  │  /api/risk/assess        风险评估                 │   │
│  │  /health                 健康检查                 │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                              │
│                         ▼                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │                   服务层                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │   │
│  │  │EmotionService│ │ ChatService │ │RiskService│ │   │
│  │  └─────────────┘ └─────────────┘ └───────────┘ │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                              │
│                         ▼                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │                   模型层                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │   │
│  │  │  SnowNLP    │ │ 智谱AI API  │ │ 规则引擎   │ │   │
│  │  └─────────────┘ └─────────────┘ └───────────┘ │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.3 智谱AI GLM-4-Flash

本系统使用智谱AI的GLM-4-Flash模型作为AI对话服务，具有以下优势：

**免费使用**：
- GLM-4-Flash模型完全免费，无需付费
- 新用户注册即送2000万-2500万Tokens免费额度

**技术特点**：
- 支持中文对话，理解能力强
- 响应速度快，适合实时对话场景
- 支持多轮对话上下文
- API调用简单，易于集成

**API调用示例**：
```python
import requests

url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "model": "glm-4-flash",
    "messages": [
        {"role": "system", "content": "你是一位专业的心理健康助手..."},
        {"role": "user", "content": "我最近感觉很焦虑"}
    ]
}
response = requests.post(url, headers=headers, json=data)
```

### 2.4 情感分析服务

使用SnowNLP进行中文情感分析：

```python
from snownlp import SnowNLP

class EmotionService:
    def analyze(self, text):
        s = SnowNLP(text)
        sentiment_score = s.sentiments
        keywords = s.keywords(5)
        
        if sentiment_score > 0.6:
            emotion_type = 'positive'
        elif sentiment_score < 0.4:
            emotion_type = 'negative'
        else:
            emotion_type = 'neutral'
        
        return {
            'sentiment_score': round(sentiment_score, 2),
            'emotion_type': emotion_type,
            'keywords': list(keywords)[:5]
        }
```

### 2.5 风险评估服务

基于规则引擎的风险评估：

```python
class RiskService:
    def assess(self, user_data):
        score = user_data.get('score', 0)
        history = user_data.get('history', [])
        
        risk_level = 'low'
        risk_factors = []
        
        if score >= 20:
            risk_level = 'high'
            risk_factors.append('测评得分较高')
        elif score >= 10:
            risk_level = 'medium'
            risk_factors.append('测评得分中等')
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendation': self._get_recommendation(risk_level)
        }
```

---

## 三、系统启动顺序

系统需要按以下顺序启动：

1. **MySQL + Redis**（数据库和缓存）
2. **Python AI服务**（端口5000）
   ```bash
   cd ai-service
   pip install -r requirements.txt
   python app.py
   ```
3. **Java后端**（端口8080）
   ```bash
   cd backend
   mvn spring-boot:run
   ```
4. **Vue前端**（端口5173）
   ```bash
   cd frontend
   npm run dev
   ```

---

## 四、核心配置

### 4.1 后端配置 (application.yml)

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mental_health
    username: root
    password: 1234
  
  redis:
    host: localhost
    port: 6379

ai:
  python:
    url: http://localhost:5000
  zhipu:
    api-key: your-api-key
    model: glm-4-flash
    base-url: https://open.bigmodel.cn/api/paas/v4
```

### 4.2 AI服务配置 (config.py)

```python
import os

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', 'your-api-key')
ZHIPU_MODEL = os.getenv('ZHIPU_MODEL', 'glm-4-flash')
ZHIPU_BASE_URL = os.getenv('ZHIPU_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
```

---

## 五、技术架构总结

本系统采用前后端分离架构，主要技术特点：

1. **前端**：Vue 3 + TypeScript + Element Plus，响应式设计
2. **后端**：Spring Boot 3 + MyBatis-Plus + JWT认证
3. **AI服务**：Python Flask + 智谱AI GLM-4-Flash + SnowNLP
4. **数据库**：MySQL 8.0 + Redis 7.x
5. **部署**：Nginx反向代理 + Docker容器化

系统架构清晰，模块职责分明，易于维护和扩展。AI服务独立部署，便于模型更新和扩展。使用智谱AI免费模型，降低运营成本。

---

## 文档修订记录

| 版本 | 日期 | 修订内容 | 修订人 |
|------|------|---------|--------|
| V1.0 | 2026-02-26 | 初始版本 | 林秋颜 |
| V1.1 | 2026-03-09 | 更新AI服务为智谱AI GLM-4-Flash | 林秋颜 |

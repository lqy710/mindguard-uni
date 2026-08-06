# MindGuard - 基于 AI 的心理健康检测与辅助系统

基于 AI 的心理健康检测与辅助系统，提供心理测评、情绪日记、AI 对话与风险评估等功能。用户端为 uni-app（微信小程序 + H5），服务端包含 Spring Boot 后端与 Python AI 服务。

## 项目结构

```
mindguard-uni/
├── src/            # 用户端（uni-app 小程序 + H5）：Vue3 + TypeScript + Pinia
├── server/         # 后端服务（Spring Boot 3.2 / Java 17 + MyBatis-Plus + Redis）
├── ai-service/     # AI 服务（Python / Flask + 智谱 AI GLM-4-Flash）
├── database/       # 数据库初始化 SQL
├── docs/           # 架构、API、需求等文档
├── docker-compose.yml  # MySQL / Redis / backend / ai-service 编排
├── index.html
├── vite.config.ts
└── package.json
```

## 技术栈

- 前端：Vue 3.4 / TypeScript / Pinia / wot-design-uni / Vite 5
- 后端：Java 17 / Spring Boot 3.2 / Spring Security + JWT / MyBatis-Plus / MySQL 8 / Redis 7
- AI 服务：Python 3.9+ / Flask / 智谱 AI GLM-4-Flash / SnowNLP

## 本地开发

### 前端（小程序 / H5）

```bash
npm install
npm run dev:h5        # H5 开发
npm run dev:mp-weixin # 微信小程序（需微信开发者工具）
```

> 微信小程序 AppID 在 `src/manifest.json` 的 `mp-weixin.appid` 中本地填写，请勿提交到仓库。

### 后端

```bash
cd server
# 复制 src/main/resources/application.yml 并按需配置数据库 / Redis / 智谱 AI
mvn spring-boot:run   # 默认端口 8080
```

### AI 服务

```bash
cd ai-service
pip install -r requirements.txt
cp .env.example .env  # 填写 ZHIPU_API_KEY 等
python app.py         # 默认端口 5000
```

### 一键编排（Docker）

```bash
cp server/.env.example server/.env   # 与 ai-service/.env 填写密钥
docker compose up -d
```

## 说明

本系统仅供辅助参考，不能替代专业心理医生的诊断和治疗。如有严重心理问题，请及时寻求专业帮助。

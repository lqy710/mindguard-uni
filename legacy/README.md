> **历史文档（已迁移）**：本文档属于 MindGuard 旧版 Web 项目（`legacy/`，Vue3 Web + Spring Boot + Flask），**不再维护**。当前用户端已重构为 uni-app（微信小程序 + H5），实际实现见仓库 `src/` 目录；开发规则与当前设计系统见 `.trae/rules/mindguard-migration.md`。本文件仅作历史回溯参考。

# MindGuard - 基于AI的心理健康检测与辅助系统

## 项目简介

MindGuard是一个基于AI的心理健康检测与辅助系统，旨在为用户提供专业的心理健康评估、情感支持和咨询服务。系统采用前后端分离架构，集成智谱AI GLM-4-Flash大模型，提供智能对话、情感分析和风险评估功能。

## 主要功能

### 用户端功能

- 🔐 **用户认证**：注册、登录、个人信息管理
- 📊 **心理测评**：多种专业心理量表（PHQ-9、GAD-7等）
- 📔 **情绪日记**：记录每日情绪，AI自动情感分析
- 💬 **AI对话**：智能心理健康助手，提供情感支持
- 📈 **数据统计**：个人心理健康趋势分析

### 管理端功能

- 👥 **用户管理**：用户信息查看、状态管理
- ⚠️ **预警系统**：高风险用户自动预警
- 📋 **量表管理**：心理量表增删改查
- 📊 **数据统计**：系统运营数据可视化

## 技术栈

### 前端
- Vue 3.4+ / TypeScript 5.x
- Element Plus 2.x
- Pinia 2.x / Vue Router 4.x
- Axios / ECharts 5.x
- Vite 5.x

### 后端
- Java 17 / Spring Boot 3.2
- Spring Security 6.x / JWT
- MyBatis-Plus 3.5
- MySQL 8.0 / Redis 7.x

### AI服务
- Python 3.9+ / Flask 3.x
- 智谱AI GLM-4-Flash（免费）
- SnowNLP 中文情感分析

## 项目结构

```
MindGuard/
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 公共组件
│   │   ├── api/            # API接口
│   │   ├── stores/         # 状态管理
│   │   └── router/         # 路由配置
│   └── package.json
│
├── backend/                 # 后端项目
│   ├── src/main/java/com/mental/
│   │   ├── controller/     # 控制器
│   │   ├── service/        # 服务层
│   │   ├── mapper/         # 数据访问层
│   │   ├── entity/         # 实体类
│   │   └── config/         # 配置类
│   └── pom.xml
│
├── ai-service/              # AI服务
│   ├── services/           # AI服务模块
│   │   ├── emotion_analysis.py    # 情感分析
│   │   ├── chat_service.py        # AI对话
│   │   └── risk_assessment.py     # 风险评估
│   ├── app.py              # Flask入口
│   ├── config.py           # 配置文件
│   └── requirements.txt    # Python依赖
│
└── docs/                    # 文档
    ├── architecture.md      # 架构文档
    ├── api.md              # API文档
    └── requirements.md     # 需求文档
```

## 快速开始

### 环境要求

- Node.js 18+
- Java 17+
- Python 3.9+
- MySQL 8.0+
- Redis 7.x

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/MindGuard.git
cd MindGuard
```

2. **安装前端依赖**
```bash
cd frontend
npm install
```

3. **安装后端依赖**
```bash
cd ../backend
mvn install
```

4. **安装AI服务依赖**
```bash
cd ../ai-service
pip install -r requirements.txt
```

5. **配置数据库**
```sql
CREATE DATABASE mental_health;
```

修改 `backend/src/main/resources/application.yml` 中的数据库配置。

6. **配置智谱AI**

在 `ai-service/config.py` 中配置智谱AI API Key：
```python
ZHIPU_API_KEY = 'your-api-key'
```

### 启动服务

按以下顺序启动：

1. **启动MySQL和Redis**

2. **启动AI服务**（端口5000）
```bash
cd ai-service
python app.py
```

3. **启动后端服务**（端口8080）
```bash
cd backend
mvn spring-boot:run
```

4. **启动前端服务**（端口5173）
```bash
cd frontend
npm run dev
```

### 访问系统

- 前端地址：http://localhost:5173
- 后端地址：http://localhost:8080
- AI服务地址：http://localhost:5000

## AI服务说明

### 智谱AI GLM-4-Flash

本系统使用智谱AI的GLM-4-Flash模型，具有以下优势：

- ✅ **完全免费**：GLM-4-Flash模型永久免费
- ✅ **中文优化**：专为中文对话优化
- ✅ **响应快速**：适合实时对话场景
- ✅ **易于集成**：API调用简单

### API接口

AI服务提供以下接口：

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/emotion/analyze | POST | 情感分析 |
| /api/chat/reply | POST | AI对话 |
| /api/risk/assess | POST | 风险评估 |
| /health | GET | 健康检查 |

详细接口文档请查看 [API文档](docs/api.md)。

## 项目文档

- [架构文档](docs/architecture.md)
- [API文档](docs/api.md)
- [需求文档](docs/requirements.md)

## 开发团队

- 开发者：林秋颜
- 指导老师：[指导老师姓名]

## 许可证

本项目仅供学习和研究使用。

---

**注意**：本系统仅供辅助参考，不能替代专业心理医生的诊断和治疗。如有严重心理问题，请及时寻求专业帮助。

## 更新日志

### V1.1 (2026-03-09)
- 更新AI服务为智谱AI GLM-4-Flash
- 新增情感分析功能
- 新增风险评估功能
- 优化系统架构

### V1.0 (2026-02-26)
- 初始版本发布
- 实现基础功能模块

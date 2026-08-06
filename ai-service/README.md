> **历史文档（已迁移）**：本文档属于 MindGuard 旧版 Web 项目（`legacy/`，Vue3 Web + Spring Boot + Flask），**不再维护**。当前用户端已重构为 uni-app（微信小程序 + H5），实际实现见仓库 `src/` 目录；开发规则与当前设计系统见 `.trae/rules/mindguard-migration.md`。本文件仅作历史回溯参考。

# AI服务

AI服务提供情感分析、对话生成和风险评估功能。

## 技术栈

- Python 3.9+
- Flask
- SnowNLP (中文情感分析)
- 智谱AI GLM-4-Flash (AI对话)

## 安装依赖

```bash
cd ai-service
pip install -r requirements.txt
```

## 运行服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动

## API接口

### 情感分析
POST /api/emotion/analyze

请求:
```json
{
    "text": "今天心情很好"
}
```

响应:
```json
{
    "code": 200,
    "data": {
        "sentiment_score": 0.85,
        "emotion_type": "positive",
        "keywords": ["心情", "好"]
    }
}
```

### AI对话
POST /api/chat/reply

请求:
```json
{
    "message": "你好",
    "context": []
}
```

响应:
```json
{
    "code": 200,
    "data": {
        "reply": "你好！我是你的心理健康助手...",
        "confidence": 0.95
    }
}
```

### 风险评估
POST /api/risk/assess

请求:
```json
{
    "userData": {
        "score": 15,
        "history": [{"risk_level": "medium", "score": 12}]
    }
}
```

响应:
```json
{
    "code": 200,
    "data": {
        "risk_level": "medium",
        "risk_factors": ["测评得分中等"],
        "recommendation": "建议寻求专业心理咨询..."
    }
}
```

## 配置

在 `config.py` 中设置环境变量:
- ZHIPU_API_KEY: 智谱AI API Key
- ZHIPU_MODEL: 模型名称 (默认: glm-4-flash)
- ZHIPU_BASE_URL: API地址 (默认: https://open.bigmodel.cn/api/paas/v4)

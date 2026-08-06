> **历史文档（已迁移）**：本文档属于 MindGuard 旧版 Web 项目（`legacy/`，Vue3 Web + Spring Boot + Flask），**不再维护**。当前用户端已重构为 uni-app（微信小程序 + H5），实际实现见仓库 `src/` 目录；开发规则与当前设计系统见 `.trae/rules/mindguard-migration.md`。本文件仅作历史回溯参考。

# MindGuard 项目完善待办清单

> 本文档列出了 MindGuard 项目需要完善的所有问题，建议每个问题在新会话中单独解决。
> 
> 创建时间：2026-03-24

---

## 📋 待办事项概览

| 序号 | 问题 | 优先级 | 预计耗时 | 状态 |
|------|------|--------|----------|------|
| 1 | 敏感信息脱敏（后端） | 🔴 高 | 15分钟 | ✅ 已完成 |
| 2 | 敏感信息脱敏（AI服务） | 🔴 高 | 10分钟 | ✅ 已完成 |
| 3 | 添加 .gitignore 排除敏感文件 | 🔴 高 | 5分钟 | ✅ 已完成 |
| 4 | 后端单元测试 | 🔴 高 | 60分钟 | ✅ 已完成 |
| 5 | AI服务单元测试 | 🔴 高 | 30分钟 | ✅ 已完成 |
| 6 | 前端单元测试 | 🟡 中 | 45分钟 | ✅ 已完成 |
| 7 | Docker 后端容器化 | 🟡 中 | 20分钟 | ✅ 已完成 |
| 8 | Docker AI服务容器化 | 🟡 中 | 15分钟 | ✅ 已完成 |
| 9 | Docker 前端容器化 | 🟡 中 | 15分钟 | ✅ 已完成 |
| 10 | Docker Compose 编排 | 🟡 中 | 20分钟 | ✅ 已完成 |
| 11 | 生产环境配置分离 | 🟡 中 | 15分钟 | ✅ 已完成 |
| 12 | 数据库备份脚本 | 🟢 低 | 10分钟 | ✅ 已完成 |
| 13 | 日志配置优化 | 🟢 低 | 10分钟 | ✅ 已完成 |
| 14 | API 文档完善 | 🟢 低 | 15分钟 | ✅ 已完成 |

---

## 🔴 高优先级问题

---

### 问题 1：敏感信息脱敏（后端）

#### 问题描述

`backend/src/main/resources/application.yml` 文件中存在以下敏感信息明文存储：

```yaml
# 问题1: 数据库密码明文
spring:
  datasource:
    password: 1234

# 问题2: JWT Secret 明文
jwt:
  secret: mental-health-jwt-secret-key-2026-very-long-secret

# 问题3: 智谱AI API Key 明文
ai:
  zhipu:
    api-key: 778896d1ef454800aa81bb26db51381e.SFrw6mkeWdQj7a0D
```

#### 解决方案

**步骤1：创建环境变量配置文件**

在 `backend/` 目录下创建 `.env.example` 文件（示例文件，可提交到 Git）：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mental_health
DB_USERNAME=root
DB_PASSWORD=your_password_here

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT配置
JWT_SECRET=your-jwt-secret-key-here
JWT_EXPIRATION=604800000

# 智谱AI配置
ZHIPU_API_KEY=your-zhipu-api-key-here
ZHIPU_MODEL=glm-4-flash
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# AI服务地址
AI_PYTHON_URL=http://localhost:5000
```

**步骤2：创建实际使用的 .env 文件**

在 `backend/` 目录下创建 `.env` 文件（不要提交到 Git）：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mental_health
DB_USERNAME=root
DB_PASSWORD=1234

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT配置
JWT_SECRET=mental-health-jwt-secret-key-2026-very-long-secret
JWT_EXPIRATION=604800000

# 智谱AI配置
ZHIPU_API_KEY=778896d1ef454800aa81bb26db51381e.SFrw6mkeWdQj7a0D
ZHIPU_MODEL=glm-4-flash
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# AI服务地址
AI_PYTHON_URL=http://localhost:5000
```

**步骤3：修改 application.yml 使用环境变量**

```yaml
server:
  port: 8080

spring:
  application:
    name: mental-health
  
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://${DB_HOST:localhost}:${DB_PORT:3306}/${DB_NAME:mental_health}?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&useSSL=false
    username: ${DB_USERNAME:root}
    password: ${DB_PASSWORD:}
    type: com.zaxxer.hikari.HikariDataSource
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20
      idle-timeout: 30000
      pool-name: MentalHealthHikariPool
      max-lifetime: 1800000
      connection-timeout: 30000
  
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: ${REDIS_PORT:6379}
      database: 0
      timeout: 10000ms
  
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: GMT+8
    default-property-inclusion: non_null

mybatis-plus:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.mental.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    db-config:
      id-type: auto
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0

jwt:
  secret: ${JWT_SECRET:default-secret-key}
  expiration: ${JWT_EXPIRATION:604800000}

ai:
  python:
    url: ${AI_PYTHON_URL:http://localhost:5000}
  zhipu:
    api-key: ${ZHIPU_API_KEY:}
    model: ${ZHIPU_MODEL:glm-4-flash}
    base-url: ${ZHIPU_BASE_URL:https://open.bigmodel.cn/api/paas/v4}

springdoc:
  swagger-ui:
    path: /swagger-ui.html
  api-docs:
    path: /v3/api-docs

logging:
  level:
    com.mental: debug
    org.springframework.security: info
```

**步骤4：添加依赖读取 .env 文件**

在 `backend/pom.xml` 中添加依赖：

```xml
<!-- 读取 .env 文件 -->
<dependency>
    <groupId>io.github.cdimascio</groupId>
    <artifactId>dotenv-java</artifactId>
    <version>3.0.0</version>
</dependency>
```

**步骤5：在启动类中加载 .env**

修改 `backend/src/main/java/com/mental/MentalHealthApplication.java`：

```java
package com.mental;

import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class MentalHealthApplication {

    public static void main(String[] args) {
        // 加载 .env 文件
        Dotenv dotenv = Dotenv.configure()
                .directory("./")
                .ignoreIfMissing()
                .load();
        
        // 设置系统属性
        dotenv.entries().forEach(entry -> {
            System.setProperty(entry.getKey(), entry.getValue());
        });
        
        SpringApplication.run(MentalHealthApplication.class, args);
    }
}
```

#### 验证方法

1. 创建 `.env` 文件后启动项目
2. 检查是否能正常连接数据库
3. 检查 AI 服务是否正常调用
4. 确认 `.env` 文件不会被提交到 Git

---

### 问题 2：敏感信息脱敏（AI服务）

#### 问题描述

`ai-service/config.py` 文件中 API Key 明文存储：

```python
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '778896d1ef454800aa81bb26db51381e.SFrw6mkeWdQj7a0D')
```

#### 解决方案

**步骤1：创建 .env.example 文件**

在 `ai-service/` 目录下创建 `.env.example`：

```env
# Flask配置
DEBUG=True
SECRET_KEY=your-secret-key-here

# 智谱AI配置
ZHIPU_API_KEY=your-zhipu-api-key-here
ZHIPU_MODEL=glm-4-flash
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

**步骤2：创建实际使用的 .env 文件**

在 `ai-service/` 目录下创建 `.env`：

```env
# Flask配置
DEBUG=True
SECRET_KEY=mental-health-ai-secret-key

# 智谱AI配置
ZHIPU_API_KEY=778896d1ef454800aa81bb26db51381e.SFrw6mkeWdQj7a0D
ZHIPU_MODEL=glm-4-flash
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

**步骤3：修改 config.py**

```python
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')
ZHIPU_MODEL = os.getenv('ZHIPU_MODEL', 'glm-4-flash')
ZHIPU_BASE_URL = os.getenv('ZHIPU_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
```

**步骤4：添加依赖**

在 `ai-service/requirements.txt` 中添加：

```
python-dotenv>=1.0.0
```

#### 验证方法

1. 运行 `pip install python-dotenv`
2. 启动 AI 服务
3. 测试 AI 对话接口是否正常

---

### 问题 3：添加 .gitignore 排除敏感文件

#### 问题描述

需要确保 `.env` 等敏感文件不会被提交到 Git 仓库。

#### 解决方案

**检查并更新项目根目录的 .gitignore 文件**

确保包含以下内容：

```gitignore
# 环境变量文件
.env
.env.local
.env.*.local
backend/.env
ai-service/.env

# IDE配置
.idea/
.vscode/
*.iml

# 编译输出
backend/target/
frontend/dist/
frontend/node_modules/

# 日志文件
*.log
logs/

# 系统文件
.DS_Store
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Java
*.class
*.jar
*.war
*.ear
```

#### 验证方法

1. 运行 `git status` 确认 `.env` 文件未被跟踪
2. 如果已被跟踪，运行 `git rm --cached backend/.env` 移除

---

### 问题 4：后端单元测试

#### 问题描述

`backend/src/test/` 目录为空，没有任何测试代码。

#### 解决方案

**步骤1：添加测试依赖**

确保 `pom.xml` 中包含测试依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <scope>test</scope>
</dependency>
```

**步骤2：创建测试目录结构**

```
backend/src/test/java/com/mental/
├── service/
│   ├── AuthServiceTest.java
│   ├── AssessmentServiceTest.java
│   ├── ChatServiceTest.java
│   ├── DiaryServiceTest.java
│   └── WarningServiceTest.java
├── controller/
│   ├── AuthControllerTest.java
│   └── AssessmentControllerTest.java
└── util/
    └── PasswordGeneratorTest.java
```

**步骤3：编写核心服务测试示例**

创建 `backend/src/test/java/com/mental/service/WarningServiceTest.java`：

```java
package com.mental.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mental.entity.Assessment;
import com.mental.entity.Warning;
import com.mental.mapper.AssessmentMapper;
import com.mental.mapper.WarningMapper;
import com.mental.service.impl.WarningServiceImpl;
import com.mental.service.PythonAiService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WarningServiceTest {

    @Mock
    private WarningMapper warningMapper;

    @Mock
    private AssessmentMapper assessmentMapper;

    @Mock
    private PythonAiService pythonAiService;

    @InjectMocks
    private WarningServiceImpl warningService;

    @Test
    @DisplayName("测试风险评估 - 高风险用户")
    void testAssessUserRisk_HighRisk() {
        // 准备数据
        Long userId = 1L;
        Assessment assessment = new Assessment();
        assessment.setUserId(userId);
        assessment.setTotalScore(25.0);
        assessment.setRiskLevel("high");

        // Mock 行为
        when(assessmentMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(assessment);
        when(assessmentMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(Arrays.asList(assessment));
        
        Map<String, Object> riskResult = new HashMap<>();
        riskResult.put("risk_level", "high");
        riskResult.put("risk_factors", Arrays.asList("测评得分较高"));
        when(pythonAiService.assessRisk(any())).thenReturn(riskResult);

        // 执行测试
        Map<String, Object> result = warningService.assessUserRisk(userId);

        // 验证结果
        assertEquals("high", result.get("risk_level"));
        verify(pythonAiService, times(1)).assessRisk(any());
    }

    @Test
    @DisplayName("测试风险评估 - 低风险用户")
    void testAssessUserRisk_LowRisk() {
        Long userId = 2L;
        Assessment assessment = new Assessment();
        assessment.setUserId(userId);
        assessment.setTotalScore(5.0);
        assessment.setRiskLevel("low");

        when(assessmentMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(assessment);
        when(assessmentMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(Arrays.asList(assessment));
        
        Map<String, Object> riskResult = new HashMap<>();
        riskResult.put("risk_level", "low");
        riskResult.put("risk_factors", new ArrayList<>());
        when(pythonAiService.assessRisk(any())).thenReturn(riskResult);

        Map<String, Object> result = warningService.assessUserRisk(userId);

        assertEquals("low", result.get("risk_level"));
    }
}
```

**步骤4：编写 Controller 测试示例**

创建 `backend/src/test/java/com/mental/controller/AuthControllerTest.java`：

```java
package com.mental.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mental.dto.LoginDTO;
import com.mental.dto.RegisterDTO;
import com.mental.service.AuthService;
import com.mental.vo.LoginVO;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private AuthService authService;

    @Test
    @DisplayName("测试用户登录 - 成功")
    void testLogin_Success() throws Exception {
        LoginDTO loginDTO = new LoginDTO();
        loginDTO.setUsername("testuser");
        loginDTO.setPassword("password123");

        LoginVO loginVO = new LoginVO();
        loginVO.setToken("test-token");
        loginVO.setUsername("testuser");

        when(authService.login(any(LoginDTO.class))).thenReturn(loginVO);

        mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(loginDTO)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.token").value("test-token"));
    }

    @Test
    @DisplayName("测试用户注册 - 成功")
    void testRegister_Success() throws Exception {
        RegisterDTO registerDTO = new RegisterDTO();
        registerDTO.setUsername("newuser");
        registerDTO.setPassword("password123");

        when(authService.register(any(RegisterDTO.class))).thenReturn(1L);

        mockMvc.perform(post("/api/auth/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(registerDTO)))
                .andExpect(status().isOk());
    }
}
```

#### 验证方法

1. 运行 `mvn test` 执行所有测试
2. 检查测试覆盖率报告
3. 确保核心业务逻辑测试通过

---

### 问题 5：AI服务单元测试

#### 问题描述

AI 服务没有任何测试代码。

#### 解决方案

**步骤1：创建测试目录结构**

```
ai-service/tests/
├── __init__.py
├── test_emotion_analysis.py
├── test_chat_service.py
├── test_risk_assessment.py
└── test_app.py
```

**步骤2：编写情感分析测试**

创建 `ai-service/tests/test_emotion_analysis.py`：

```python
import sys
sys.path.insert(0, '..')

from services.emotion_analysis import EmotionService
import pytest

class TestEmotionService:
    
    def setup_method(self):
        self.service = EmotionService()
    
    def test_analyze_positive_text(self):
        """测试正面情感文本"""
        result = self.service.analyze("今天天气真好，心情很愉快！")
        
        assert result['emotion_type'] == 'positive'
        assert result['sentiment_score'] > 0.6
        assert len(result['keywords']) > 0
    
    def test_analyze_negative_text(self):
        """测试负面情感文本"""
        result = self.service.analyze("今天很糟糕，什么都不想做")
        
        assert result['emotion_type'] == 'negative'
        assert result['sentiment_score'] < 0.4
    
    def test_analyze_neutral_text(self):
        """测试中性情感文本"""
        result = self.service.analyze("今天去上班了")
        
        assert result['emotion_type'] in ['positive', 'neutral', 'negative']
        assert 0 <= result['sentiment_score'] <= 1
```

**步骤3：编写风险评估测试**

创建 `ai-service/tests/test_risk_assessment.py`：

```python
import sys
sys.path.insert(0, '..')

from services.risk_assessment import RiskService
import pytest

class TestRiskService:
    
    def setup_method(self):
        self.service = RiskService()
    
    def test_assess_high_risk_score(self):
        """测试高风险评分"""
        user_data = {
            'score': 25,
            'history': [{'risk_level': 'high', 'score': 22}]
        }
        
        result = self.service.assess(user_data)
        
        assert result['risk_level'] == 'high'
        assert result['need_immediate_attention'] == True
    
    def test_assess_low_risk_score(self):
        """测试低风险评分"""
        user_data = {
            'score': 3,
            'history': [{'risk_level': 'low', 'score': 2}]
        }
        
        result = self.service.assess(user_data)
        
        assert result['risk_level'] == 'low'
        assert result['need_immediate_attention'] == False
    
    def test_quick_assess_crisis_keyword(self):
        """测试危机关键词检测"""
        result = self.service.quick_assess("我不想活了，想自杀")
        
        assert result['risk_level'] == 'high'
        assert result['need_immediate_attention'] == True
    
    def test_quick_assess_normal_text(self):
        """测试正常文本"""
        result = self.service.quick_assess("今天天气不错")
        
        assert result['risk_level'] == 'low'
        assert result['need_immediate_attention'] == False
```

**步骤4：编写 API 测试**

创建 `ai-service/tests/test_app.py`：

```python
import sys
sys.path.insert(0, '..')

from app import app
import pytest
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestApp:
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_emotion_analyze(self, client):
        """测试情感分析接口"""
        response = client.post('/api/emotion/analyze',
            json={'text': '今天心情很好'},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'emotion_type' in data
        assert 'sentiment_score' in data
    
    def test_risk_assess(self, client):
        """测试风险评估接口"""
        response = client.post('/api/risk/assess',
            json={'score': 15, 'history': []},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'risk_level' in data
```

**步骤5：添加测试依赖**

在 `ai-service/requirements.txt` 中添加：

```
pytest>=7.0.0
pytest-cov>=4.0.0
```

#### 验证方法

1. 运行 `cd ai-service && pytest tests/ -v`
2. 检查测试覆盖率：`pytest tests/ --cov=services`

---

## 🟡 中优先级问题

---

### 问题 6：前端单元测试

#### 问题描述

前端项目没有单元测试。

#### 解决方案

**步骤1：安装测试依赖**

```bash
cd frontend
npm install -D vitest @vue/test-utils jsdom
```

**步骤2：配置 Vitest**

修改 `frontend/vite.config.ts`：

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html']
    }
  }
})
```

**步骤3：创建测试文件示例**

创建 `frontend/src/stores/__tests__/user.test.ts`：

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '../user'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('初始状态为未登录', () => {
    const store = useUserStore()
    expect(store.isLoggedIn).toBe(false)
    expect(store.token).toBe('')
  })

  it('登录后更新状态', () => {
    const store = useUserStore()
    store.setToken('test-token')
    store.setUser({ id: 1, username: 'test' } as any)
    
    expect(store.isLoggedIn).toBe(true)
    expect(store.token).toBe('test-token')
  })

  it('登出后清除状态', () => {
    const store = useUserStore()
    store.setToken('test-token')
    store.logout()
    
    expect(store.isLoggedIn).toBe(false)
    expect(store.token).toBe('')
  })
})
```

**步骤4：添加测试脚本**

在 `frontend/package.json` 中添加：

```json
{
  "scripts": {
    "test": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

#### 验证方法

1. 运行 `npm run test`
2. 检查测试覆盖率报告

---

### 问题 7：Docker 后端容器化

#### 问题描述

项目没有 Docker 配置，不便于部署。

#### 解决方案

**创建 `backend/Dockerfile`：**

```dockerfile
# 构建阶段
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app

# 复制 pom.xml 并下载依赖
COPY pom.xml .
RUN mvn dependency:go-offline -B

# 复制源码并构建
COPY src ./src
RUN mvn package -DskipTests

# 运行阶段
FROM eclipse-temurin:17-jre
WORKDIR /app

# 创建非 root 用户
RUN groupadd -r mental && useradd -r -g mental mental

# 复制构建产物
COPY --from=build /app/target/*.jar app.jar

# 复制 .env 文件（运行时挂载）
# COPY .env .env

# 设置权限
RUN chown -R mental:mental /app

USER mental

EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
```

**创建 `backend/.dockerignore`：**

```
target/
!.mvn/wrapper/maven-wrapper.jar
.env
*.log
.idea/
*.iml
```

#### 验证方法

```bash
cd backend
docker build -t mindguard-backend:latest .
docker run -p 8080:8080 --env-file .env mindguard-backend:latest
```

---

### 问题 8：Docker AI服务容器化

#### 解决方案

**创建 `ai-service/Dockerfile`：**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 创建非 root 用户
RUN useradd -m -r aiuser && chown -R aiuser:aiuser /app
USER aiuser

EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
```

**创建 `ai-service/.dockerignore`：**

```
__pycache__/
*.py[cod]
.env
*.log
.pytest_cache/
tests/
```

#### 验证方法

```bash
cd ai-service
docker build -t mindguard-ai:latest .
docker run -p 5000:5000 --env-file .env mindguard-ai:latest
```

---

### 问题 9：Docker 前端容器化

#### 解决方案

**创建 `frontend/Dockerfile`：**

```dockerfile
# 构建阶段
FROM node:18-alpine AS build
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源码
COPY . .

# 构建
RUN npm run build

# 生产阶段
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# 复制构建产物
COPY --from=build /app/dist .
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

**创建 `frontend/nginx.conf`：**

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # 静态资源缓存
    location /assets {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location /api {
        proxy_pass http://backend:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket 代理
    location /ws {
        proxy_pass http://backend:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

#### 验证方法

```bash
cd frontend
docker build -t mindguard-frontend:latest .
docker run -p 80:80 mindguard-frontend:latest
```

---

### 问题 10：Docker Compose 编排

#### 解决方案

**创建项目根目录 `docker-compose.yml`：**

```yaml
version: '3.8'

services:
  # MySQL 数据库
  mysql:
    image: mysql:8.0
    container_name: mindguard-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-1234}
      MYSQL_DATABASE: mental_health
      TZ: Asia/Shanghai
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: mindguard-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # AI 服务
  ai-service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile
    container_name: mindguard-ai
    restart: unless-stopped
    environment:
      - ZHIPU_API_KEY=${ZHIPU_API_KEY}
      - ZHIPU_MODEL=glm-4-flash
      - DEBUG=False
    ports:
      - "5000:5000"
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 后端服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: mindguard-backend
    restart: unless-stopped
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_NAME=mental_health
      - DB_USERNAME=root
      - DB_PASSWORD=${DB_PASSWORD:-1234}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET=${JWT_SECRET:-mental-health-jwt-secret}
      - ZHIPU_API_KEY=${ZHIPU_API_KEY}
      - AI_PYTHON_URL=http://ai-service:5000
    ports:
      - "8080:8080"
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
      ai-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: mindguard-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
  redis_data:
```

**创建 `docker-compose.dev.yml`（开发环境）：**

```yaml
version: '3.8'

services:
  mysql:
    extends:
      file: docker-compose.yml
      service: mysql
    ports:
      - "3306:3306"

  redis:
    extends:
      file: docker-compose.yml
      service: redis
    ports:
      - "6379:6379"
```

#### 验证方法

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

### 问题 11：生产环境配置分离

#### 解决方案

**创建多环境配置文件：**

1. `backend/src/main/resources/application-dev.yml`（开发环境）
2. `backend/src/main/resources/application-prod.yml`（生产环境）

**application-dev.yml：**

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://${DB_HOST:localhost}:3306/mental_health?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
    username: ${DB_USERNAME:root}
    password: ${DB_PASSWORD:1234}

logging:
  level:
    com.mental: debug
    org.springframework.security: debug
```

**application-prod.yml：**

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://${DB_HOST}:${DB_PORT}/${DB_NAME}?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai&useSSL=true
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 30
      minimum-idle: 10

logging:
  level:
    com.mental: info
    root: warn
  file:
    name: /var/log/mental-health/app.log
```

**修改 application.yml：**

```yaml
spring:
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
```

#### 验证方法

```bash
# 开发环境启动
java -jar app.jar

# 生产环境启动
java -jar app.jar --spring.profiles.active=prod
```

---

## 🟢 低优先级问题

---

### 问题 12：数据库备份脚本

#### 解决方案

**创建 `scripts/backup.sh`：**

```bash
#!/bin/bash

# 配置
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASS="your_password"
DB_NAME="mental_health"
BACKUP_DIR="/var/backups/mental-health"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/mental_health_${DATE}.sql.gz"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
mysqldump -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} ${DB_NAME} | gzip > ${BACKUP_FILE}

# 删除7天前的备份
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

**设置定时任务（crontab）：**

```bash
# 每天凌晨2点执行备份
0 2 * * * /path/to/scripts/backup.sh >> /var/log/mental-health/backup.log 2>&1
```

---

### 问题 13：日志配置优化

#### 解决方案

**修改 `backend/src/main/resources/logback-spring.xml`：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property name="LOG_PATH" value="${LOG_PATH:-./logs}"/>
    <property name="APP_NAME" value="mental-health"/>

    <!-- 控制台输出 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 文件输出 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/${APP_NAME}.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH}/${APP_NAME}.%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
            <maxHistory>30</maxHistory>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 错误日志单独输出 -->
    <appender name="ERROR_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/${APP_NAME}-error.log</file>
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>ERROR</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH}/${APP_NAME}-error.%d{yyyy-MM-dd}.log.gz</fileNamePattern>
            <maxHistory>90</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 开发环境 -->
    <springProfile name="dev">
        <root level="DEBUG">
            <appender-ref ref="CONSOLE"/>
        </root>
    </springProfile>

    <!-- 生产环境 -->
    <springProfile name="prod">
        <root level="INFO">
            <appender-ref ref="FILE"/>
            <appender-ref ref="ERROR_FILE"/>
        </root>
    </springProfile>
</configuration>
```

---

### 问题 14：API 文档完善

#### 解决方案

**确保 Swagger 配置完整：**

检查 `backend/src/main/java/com/mental/config/SwaggerConfig.java`：

```java
package com.mental.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class SwaggerConfig {

    @Value("${server.port:8080}")
    private String port;

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("MindGuard API")
                        .version("1.1.0")
                        .description("基于AI的心理健康检测与辅助系统 API 文档")
                        .contact(new Contact()
                                .name("林秋颜")
                                .email("developer@example.com"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")))
                .servers(List.of(
                        new Server().url("http://localhost:" + port).description("开发环境"),
                        new Server().url("https://api.mindguard.com").description("生产环境")
                ));
    }
}
```

**为 Controller 添加文档注解示例：**

```java
@Tag(name = "认证管理", description = "用户登录、注册相关接口")
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Operation(summary = "用户登录", description = "通过用户名密码登录系统")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "登录成功"),
        @ApiResponse(responseCode = "401", description = "用户名或密码错误")
    })
    @PostMapping("/login")
    public Result<LoginVO> login(@RequestBody LoginDTO loginDTO) {
        // ...
    }
}
```

---

## 📝 使用说明

### 如何使用本文档

1. **每个问题单独处理**：建议在新会话中一次只处理一个问题
2. **复制问题描述**：将问题描述和解决方案复制到新会话
3. **逐步验证**：完成一个问题后，验证通过再处理下一个

### 会话提示词模板

```
请帮我完善 MindGuard 项目的【问题X】。

问题描述：
【粘贴问题描述】

解决方案：
【粘贴解决方案】

请按照上述方案帮我实现。
```

---

## ✅ 完成记录

| 序号 | 问题 | 完成日期 | 备注 |
|------|------|----------|------|
| 1 | 敏感信息脱敏（后端） | 2026-03-24 | 已创建.env文件，修改application.yml使用环境变量 |
| 2 | 敏感信息脱敏（AI服务） | 2026-03-24 | 已创建.env文件，修改config.py使用环境变量 |
| 3 | 添加 .gitignore 排除敏感文件 | 2026-03-24 | 已创建.gitignore文件，排除.env等敏感文件 |
| 4 | 后端单元测试 | 2026-03-24 | 已创建WarningServiceTest和AuthControllerTest测试类 |
| 5 | AI服务单元测试 | 2026-03-24 | 已创建28个测试用例，覆盖情感分析、风险评估和API |
| 6 | 前端单元测试 | 2026-03-24 | 已配置Vitest，创建用户Store测试用例 |
| 7 | Docker 后端容器化 | 2026-03-24 | 已创建Dockerfile和 .dockerignore |
| 8 | Docker AI服务容器化 | 2026-03-24 | 已创建Dockerfile和 .dockerignore |
| 9 | Docker 前端容器化 | 2026-03-24 | 已创建Dockerfile和 nginx.conf |
| 10 | Docker Compose 编排 | 2026-03-24 | 已创建docker-compose.yml编排文件 |
| 11 | 生产环境配置分离 | 2026-03-24 | 已创建application-dev.yml和application-prod.yml |
| 12 | 数据库备份脚本 | 2026-03-24 | 已创建scripts/backup.sh |
| 13 | 日志配置优化 | 2026-03-24 | 已创建logback-spring.xml |
| 14 | API 文档完善 | 2026-03-24 | SwaggerConfig已配置JWT认证 |

---

*文档创建时间：2026-03-24*
*最后更新时间：2026-03-24*

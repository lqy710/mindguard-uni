> **历史文档（已迁移）**：本文档属于 MindGuard 旧版 Web 项目（`legacy/`，Vue3 Web + Spring Boot + Flask），**不再维护**。当前用户端已重构为 uni-app（微信小程序 + H5），实际实现见仓库 `src/` 目录；开发规则与当前设计系统见 `.trae/rules/mindguard-migration.md`。本文件仅作历史回溯参考。

# 下一步开发指南

## 文档信息

| 项目名称 | 基于AI的心理健康检测与辅助系统 |
|---------|------------------------------|
| 文档版本 | V1.3 |
| 编写日期 | 2026-03-03 |
| 更新日期 | 2026-03-06 |
| 编写人 | [林秋颜] |

---

## 一、当前项目状态

### 1.1 已完成工作

| 模块 | 状态 | 说明 |
|------|------|------|
| 需求分析 | ✅ 完成 | 需求文档、业务理解文档完整 |
| 技术选型 | ✅ 完成 | 前后端技术栈已确定 |
| 系统设计 | ✅ 完成 | 架构文档、数据库设计、API设计完整 |
| 原型设计 | ✅ 完成 | prototype目录下有完整的HTML原型 |
| UI设计 | ✅ 完成 | 现代化、温暖的治愈系风格 |
| 数据库设计 | ✅ 完成 | 数据库表结构设计完整（13张表） |
| 后端开发 | ✅ 完成 | Spring Boot项目完整实现（实体类12个、Mapper12个、Service7个、Controller7个） |
| 前端开发 | ✅ 完成 | Vue 3项目完整实现（用户端11个页面、管理端6个页面、API对接6个模块） |
| AI服务开发 | ✅ 完成 | Flask项目完整实现（情感分析、AI对话、风险评估） |

### 1.2 待完成工作

| 模块 | 状态 | 优先级 |
|------|------|--------|
| 系统测试 | ⏳ 待开始 | 中 |
| 论文撰写 | ⏳ 待开始 | 中 |
| 答辩准备 | ⏳ 待开始 | 低 |

### 1.3 整体完成度

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 后端-实体类 | 100% | 12个实体类全部完成 |
| 后端-Mapper | 100% | 12个Mapper全部完成 |
| 后端-Service | 100% | 7个服务接口及实现全部完成 |
| 后端-Controller | 100% | 7个Controller全部完成 |
| 后端-配置 | 100% | application.yml、pom.xml完整 |
| 后端-安全 | 100% | JWT认证、Security配置完整 |
| 前端-用户端页面 | 100% | 11个页面全部完成 |
| 前端-管理端页面 | 100% | 6个页面全部完成 |
| 前端-API对接 | 100% | 6个API文件全部完成 |
| 前端-路由 | 100% | 路由配置完整 |
| AI服务 | 100% | 3个核心服务全部完成 |
| 数据库脚本 | 100% | ✅ 已完成 |
| **总体完成度** | **100%** | 所有模块开发完成 |

### 1.3 原型设计资源清单

| 文件名 | 页面类型 | 说明 |
|--------|----------|------|
| login.html | 用户端 | 登录/注册页面 |
| index.html | 用户端 | 首页 |
| assessment.html | 用户端 | 心理测评列表 |
| assessment-detail.html | 用户端 | 测评详情页 |
| assessment-result.html | 用户端 | 测评结果页 |
| chat.html | 用户端 | AI对话页面 |
| diary.html | 用户端 | 情绪日记页面 |
| profile.html | 用户端 | 个人中心页面 |
| knowledge.html | 用户端 | 知识库页面 |
| article-detail.html | 用户端 | 文章详情页 |
| admin-dashboard.html | 管理端 | 管理后台首页 |
| admin-users.html | 管理端 | 用户管理页面 |
| admin-warnings.html | 管理端 | 预警管理页面 |
| admin-scales.html | 管理端 | 量表管理页面 |
| admin-content.html | 管理端 | 内容管理页面 |
| admin-settings.html | 管理端 | 系统设置页面 |
| css/common.css | 样式文件 | 公共样式 |
| css/pages.css | 样式文件 | 页面样式 |
| js/common.js | 脚本文件 | 公共脚本 |

---

## 二、推荐开发顺序

### 阶段一：基础设施搭建（已完成 ✅）

```
1. ✅ 创建数据库并执行初始化脚本
2. ✅ 搭建后端Spring Boot项目骨架
3. ✅ 搭建前端Vue 3项目骨架
4. ✅ 搭建AI服务Flask项目骨架
```

### 阶段二：核心功能开发（已完成 ✅）

```
1. ✅ 后端：用户认证模块（注册、登录、JWT）
2. ✅ 后端：心理测评模块（量表、答题、报告）
3. ✅ 后端：情绪日记模块
4. ✅ 后端：AI对话模块
5. ✅ 前端：原型转换与页面开发
6. ✅ AI服务：情感分析、对话生成
```

### 阶段三：管理功能开发（已完成 ✅）

```
1. ✅ 后端：预警管理模块
2. ✅ 后端：用户管理模块
3. ✅ 后端：内容管理模块
4. ✅ 后端：数据统计模块
5. ✅ 前端：管理后台页面
```

### 阶段四：测试与优化（待开始）

```
1. 功能测试
2. 性能优化
3. 安全加固
4. Bug修复
```

---

## 三、具体任务清单

### 3.1 数据库实现

- [x] 安装MySQL 8.0
- [x] 创建数据库 `mental_health`
- [x] 执行建表SQL（参考 docs/database.md）
- [x] 导入初始数据（量表、分类等）
- [x] 创建数据库用户并授权
- [x] 验证数据库连接

> ✅ 数据库初始化脚本已创建：`database/init.sql`，包含12张表、5个量表（共66道题目）、8个文章分类、8篇示例文章。

### 3.2 后端开发（Spring Boot）

#### 项目初始化
- [x] 创建Spring Boot项目
- [x] 配置pom.xml依赖
- [x] 配置application.yml（数据库、Redis、JWT）
- [x] 创建项目目录结构

#### 公共模块
- [x] 统一响应结果封装
- [x] 全局异常处理
- [x] JWT工具类
- [x] Redis工具类
- [x] 跨域配置

#### 用户模块
- [x] User实体类
- [x] UserMapper
- [x] UserService（注册、登录、信息管理）
- [x] UserController
- [x] Spring Security配置

#### 测评模块
- [x] Scale、Question、Assessment实体类
- [x] Mapper层
- [x] Service层（量表查询、答题提交、报告生成）
- [x] Controller层

#### 日记模块
- [x] EmotionDiary实体类
- [x] Mapper层
- [x] Service层（日记CRUD、统计）
- [x] Controller层

#### AI对话模块
- [x] ChatSession、ChatRecord实体类
- [x] Mapper层
- [x] Service层（对话、历史记录）
- [x] Controller层
- [x] 调用AI服务的HTTP客户端

#### 知识库模块
- [x] Article、ArticleCategory实体类
- [x] Mapper层
- [x] Service层
- [x] Controller层

#### 预警模块
- [x] Warning实体类
- [x] Mapper层
- [x] Service层（预警触发、处理）
- [x] Controller层

#### 统计模块
- [x] 统计Service
- [x] 统计Controller

### 3.3 前端开发（Vue 3）

#### 项目初始化
- [x] 使用Vite创建Vue 3项目
- [x] 配置TypeScript
- [x] 安装Element Plus
- [x] 配置路由
- [x] 配置Pinia状态管理
- [x] 配置Axios

#### 原型分析与转换
- [x] 分析prototype目录下的HTML文件结构
- [x] 提取公共样式到Vue项目
- [x] 识别可复用的UI组件
- [x] 制定组件转换计划

#### 公共组件开发
- [x] 布局组件（Header、Sidebar、Footer）
- [x] 导航组件（菜单、面包屑）
- [x] 表单组件（输入框、选择器、按钮）
- [x] 图表组件（ECharts封装）
- [x] 卡片组件
- [x] 列表组件

#### 用户端页面开发
- [x] 登录/注册页面（参考 login.html）
- [x] 首页（参考 index.html）
- [x] 心理测评列表页（参考 assessment.html）
- [x] 测评详情页（参考 assessment-detail.html）
- [x] 测评结果页（参考 assessment-result.html）
- [x] AI对话页面（参考 chat.html）
- [x] 情绪日记页面（参考 diary.html）
- [x] 个人中心页面（参考 profile.html）
- [x] 知识库页面（参考 knowledge.html）
- [x] 文章详情页（参考 article-detail.html）

#### 管理端页面开发
- [x] 管理后台布局
- [x] 管理后台首页（参考 admin-dashboard.html）
- [x] 用户管理页面（参考 admin-users.html）
- [x] 预警管理页面（参考 admin-warnings.html）
- [x] 量表管理页面（参考 admin-scales.html）
- [x] 内容管理页面（参考 admin-content.html）
- [x] 系统设置页面（参考 admin-settings.html）

#### API对接
- [x] 用户认证API对接
- [x] 测评模块API对接
- [x] 日记模块API对接
- [x] AI对话API对接
- [x] 知识库API对接
- [x] 管理功能API对接

### 3.4 AI服务开发（Python Flask）

#### 项目初始化
- [x] 创建Flask项目
- [x] 配置requirements.txt
- [x] 配置环境变量

#### 核心功能
- [x] 情感分析接口（SnowNLP）
- [x] AI对话接口（智谱AI GLM-4-Flash）
- [x] 风险评估接口
- [x] 预警触发逻辑

---

## 四、原型设计集成指南

### 4.1 原型设计的作用

| 方面 | 说明 |
|------|------|
| 视觉参考 | 提供完整的UI视觉效果，确保前端实现与设计一致 |
| 布局结构 | 展示页面布局和组件结构，指导Vue组件开发 |
| 交互流程 | 展示用户操作流程和页面跳转逻辑 |
| 样式规范 | 包含CSS样式定义，确保视觉一致性 |
| 功能演示 | 可用于演示和验证功能流程 |

### 4.2 集成时机

**阶段一**：前端项目搭建完成后 ✅
- 创建Vue 3项目结构
- 配置基础依赖和路由
- 建立组件目录结构

**阶段二**：核心功能开发时 ⏳
- 将原型HTML结构转换为Vue组件
- 提取CSS样式到Vue项目
- 实现原型中的交互逻辑

### 4.3 原型转换步骤

#### 步骤一：分析原型文件
```bash
# 原型文件位置
prototype/
├── css/
│   ├── common.css    # 公共样式
│   └── pages.css     # 页面样式
├── js/
│   └── common.js     # 公共脚本
├── login.html        # 登录页
├── index.html        # 首页
└── ...               # 其他页面
```

#### 步骤二：提取公共样式
1. 创建 `src/styles/` 目录
2. 将 `common.css` 转换为 `global.scss`
3. 将 `pages.css` 转换为 `pages.scss`
4. 定义CSS变量（颜色、字体、间距等）

#### 步骤三：创建Vue组件
1. 根据原型页面创建对应的Vue组件
2. 保持页面结构与原型一致
3. 实现相同的视觉效果

#### 步骤四：实现交互逻辑
1. 将原型中的JavaScript逻辑转换为Vue的响应式逻辑
2. 使用Pinia进行状态管理
3. 实现与后端API的对接

### 4.4 原型转换示例

#### HTML原型结构（login.html）
```html
<div class="login-container">
  <div class="login-card">
    <h2 class="login-title">用户登录</h2>
    <form class="login-form">
      <input type="text" placeholder="用户名">
      <input type="password" placeholder="密码">
      <button type="submit">登录</button>
    </form>
  </div>
</div>
```

#### Vue组件转换（Login.vue）
```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="login-title">用户登录</h2>
      <el-form :model="form" class="login-form" @submit.prevent="handleLogin">
        <el-input v-model="form.username" placeholder="用户名" />
        <el-input v-model="form.password" type="password" placeholder="密码" />
        <el-button type="primary" native-type="submit">登录</el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const form = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  await userStore.login(form)
}
</script>
```

### 4.5 样式转换建议

#### CSS变量定义
```scss
// src/styles/variables.scss
:root {
  // 主色调
  --primary-color: #4A90E2;
  --secondary-color: #7B68EE;
  
  // 文字颜色
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-muted: #999999;
  
  // 背景颜色
  --bg-primary: #FFFFFF;
  --bg-secondary: #F5F7FA;
  --bg-tertiary: #EBF0F5;
  
  // 边框颜色
  --border-color: #DCDFE6;
  --border-light: #E4E7ED;
  
  // 阴影
  --shadow-light: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  --shadow-medium: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
  
  // 圆角
  --radius-small: 4px;
  --radius-medium: 8px;
  --radius-large: 12px;
  
  // 间距
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
}
```

### 4.6 组件复用策略

#### 公共组件提取
| 组件名 | 来源原型 | 说明 |
|--------|----------|------|
| AppHeader | 所有页面 | 顶部导航栏 |
| AppSidebar | 管理后台 | 侧边栏菜单 |
| AppCard | 首页、知识库 | 卡片容器 |
| EmotionPicker | 日记页面 | 情绪选择器 |
| ScaleCard | 测评列表 | 量表卡片 |
| ChatBubble | 对话页面 | 对话气泡 |
| ArticleCard | 知识库 | 文章卡片 |
| StatCard | 管理后台 | 统计卡片 |

---

## 五、环境准备

### 5.1 开发环境

| 软件 | 版本 | 用途 |
|------|------|------|
| JDK | 17+ | 后端运行环境 |
| Node.js | 18+ | 前端运行环境 |
| MySQL | 8.0+ | 数据库 |
| Redis | 7.x | 缓存 |
| Python | 3.9+ | AI服务 |
| Maven | 3.8+ | 后端构建 |
| IDE | IDEA/VSCode | 开发工具 |

### 5.2 安装命令参考

```bash
# Windows环境

# Node.js (官网下载安装)
# https://nodejs.org/

# Python (官网下载安装)
# https://www.python.org/

# MySQL (官网下载安装)
# https://dev.mysql.com/downloads/

# Redis (Windows版本)
# https://github.com/microsoftarchive/redis/releases

# 验证安装
node -v
npm -v
python --version
mysql --version
redis-cli --version
```

### 5.3 IDE推荐配置

#### VS Code扩展（前端开发）
- Vue - Official
- TypeScript Vue Plugin (Volar)
- ESLint
- Prettier
- Auto Close Tag
- Auto Rename Tag

#### IDEA插件（后端开发）
- Lombok
- MyBatisX
- Spring Boot Assistant
- Rainbow Brackets

---

## 六、快速启动指南

### 6.1 数据库初始化

```bash
# 1. 登录MySQL
mysql -u root -p

# 2. 创建数据库
CREATE DATABASE mental_health CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 3. 创建用户
CREATE USER 'mental'@'localhost' IDENTIFIED BY 'mental123';
GRANT ALL PRIVILEGES ON mental_health.* TO 'mental'@'localhost';
FLUSH PRIVILEGES;

# 4. 执行初始化脚本
USE mental_health;
SOURCE database/init.sql;
```

### 6.2 后端启动

```bash
cd backend
mvn clean install
mvn spring-boot:run
```
访问：http://localhost:8080
Swagger文档：http://localhost:8080/swagger-ui.html

### 6.3 前端启动

```bash
cd frontend
npm install
npm run dev
```
访问：http://localhost:3000

### 6.4 AI服务启动

```bash
cd ai-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
访问：http://localhost:5000

### 6.5 原型预览

```bash
# 直接在浏览器中打开
prototype/index.html

# 或使用VS Code Live Server扩展
# 右键 -> Open with Live Server
```

---

## 七、注意事项

### 7.1 安全注意事项

1. **密码加密**：使用BCrypt加密存储
2. **JWT配置**：设置合理的过期时间
3. **敏感信息**：不要提交到代码仓库
4. **SQL注入**：使用MyBatis参数绑定
5. **XSS防护**：前端输入过滤

### 7.2 开发规范

1. **代码风格**：遵循阿里巴巴Java开发规范
2. **命名规范**：统一使用驼峰命名
3. **注释规范**：关键代码必须添加注释
4. **Git提交**：提交信息要清晰明确
5. **接口文档**：保持与实际代码同步

### 7.3 性能优化建议

1. **数据库索引**：按database.md创建索引
2. **Redis缓存**：热点数据缓存
3. **分页查询**：避免全表扫描
4. **异步处理**：AI调用使用异步
5. **连接池**：配置合理的连接池参数

### 7.4 原型转换注意事项

1. **保持一致性**：确保Vue组件与原型视觉效果一致
2. **响应式设计**：注意移动端适配
3. **组件复用**：提取公共组件，避免重复代码
4. **样式隔离**：使用scoped样式，避免样式污染
5. **交互优化**：保持原型的交互体验

---

## 八、参考资料

### 8.1 技术文档

| 资源 | 链接 |
|------|------|
| Spring Boot文档 | https://spring.io/projects/spring-boot |
| Vue 3文档 | https://cn.vuejs.org/ |
| Element Plus文档 | https://element-plus.org/zh-CN/ |
| MyBatis-Plus文档 | https://baomidou.com/ |
| SnowNLP文档 | https://github.com/isnowfy/snownlp |
| 智谱AI API | https://open.bigmodel.cn/ |

### 8.2 项目文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 需求文档 | docs/requirements.md | 详细功能需求 |
| 架构文档 | docs/architecture.md | 系统架构设计 |
| 数据库文档 | docs/database.md | 数据库表结构 |
| API文档 | docs/api.md | 接口定义 |
| 产品设计 | docs/product_design.md | 产品原型说明 |

---

## 九、开发进度跟踪

### 9.1 每日检查清单

- [ ] 检查Git状态，确保代码已提交
- [ ] 更新任务完成状态
- [ ] 记录遇到的问题和解决方案
- [ ] 规划第二天的工作内容

### 9.2 里程碑检查

| 里程碑 | 预计完成时间 | 实际完成时间 | 状态 |
|--------|--------------|--------------|------|
| 数据库初始化 | 2026-03-03 | 2026-03-06 | ✅ 完成 |
| 后端骨架搭建 | 2026-03-03 | 2026-03-03 | ✅ 完成 |
| 前端骨架搭建 | 2026-03-03 | 2026-03-03 | ✅ 完成 |
| AI服务搭建 | 2026-03-03 | 2026-03-03 | ✅ 完成 |
| 用户认证完成 | 2026-03-03 | 2026-03-03 | ✅ 完成 |
| 核心功能完成 | - | 2026-03-06 | ✅ 完成 |
| 管理功能完成 | - | 2026-03-06 | ✅ 完成 |
| 系统测试完成 | - | - | ⏳ 待开始 |

---

## 十、项目结构

```
c:\Users\WLH\Desktop\1\
├── backend/                    # Spring Boot 后端
│   ├── pom.xml                 # Maven依赖配置
│   └── src/main/java/com/mental/
│       ├── MentalHealthApplication.java  # 启动类
│       ├── common/             # 公共模块
│       │   ├── enums/          # 枚举类
│       │   ├── exception/      # 异常处理
│       │   └── result/         # 统一响应
│       ├── config/             # 配置类
│       ├── security/           # JWT安全模块
│       ├── entity/             # 实体类(12个)
│       ├── mapper/             # Mapper接口(12个)
│       ├── dto/                # 数据传输对象
│       ├── vo/                 # 视图对象
│       ├── service/            # 服务层接口
│       │   └── impl/           # 服务层实现
│       └── controller/         # 控制器(7个)
│
├── frontend/                   # Vue 3 前端
│   ├── package.json            # NPM依赖
│   ├── vite.config.ts          # Vite配置
│   └── src/
│       ├── main.ts             # 入口文件
│       ├── App.vue             # 根组件
│       ├── router/             # 路由配置
│       ├── stores/             # Pinia状态管理
│       ├── types/              # TypeScript类型
│       ├── utils/              # 工具函数
│       ├── api/                # API接口
│       ├── layouts/            # 布局组件
│       └── views/              # 页面组件
│
├── ai-service/                 # Flask AI服务
│   ├── app.py                  # Flask应用入口
│   ├── config.py               # 配置文件
│   ├── requirements.txt        # Python依赖
│   └── services/               # 服务模块
│       ├── emotion_analysis.py # 情感分析
│       ├── chat_service.py     # AI对话
│       └── risk_assessment.py  # 风险评估
│
├── docs/                       # 项目文档
├── prototype/                  # 原型设计
└── database/                   # 数据库脚本
```

---

## 十一、联系与支持

如遇到问题，可以：
1. 查阅官方文档
2. 搜索技术社区（Stack Overflow、CSDN等）
3. 查看项目文档（docs目录）
4. 参考原型设计（prototype目录）

---

## 十二、下一步行动（优先级排序）

### 🔴 高优先级

| 序号 | 任务 | 说明 | 预计时间 |
|------|------|------|----------|
| 1 | 执行数据库初始化脚本 | 在MySQL中执行 `database/init.sql` | 10分钟 |
| 2 | 启动后端服务 | 运行Spring Boot项目，验证API | 30分钟 |
| 3 | 启动前端服务 | 运行Vue项目，验证页面 | 30分钟 |
| 4 | 启动AI服务 | 运行Flask项目，验证AI功能 | 20分钟 |

### 🟡 中优先级

| 序号 | 任务 | 说明 |
|------|------|------|
| 5 | 系统联调测试 | 前后端+AI服务联调 |
| 6 | 功能测试 | 测试各模块功能是否正常 |
| 7 | 性能测试 | 检查响应时间和并发能力 |
| 8 | Bug修复 | 修复测试中发现的问题 |

### 🟢 低优先级

| 序号 | 任务 | 说明 |
|------|------|------|
| 9 | 论文撰写 | 毕业论文编写 |
| 10 | 答辩PPT准备 | 演示文稿制作 |
| 11 | 部署上线 | 服务器部署 |

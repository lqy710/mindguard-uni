> **历史文档（已迁移）**：本文档属于 MindGuard 旧版 Web 项目（`legacy/`，Vue3 Web + Spring Boot + Flask），**不再维护**。当前用户端已重构为 uni-app（微信小程序 + H5），实际实现见仓库 `src/` 目录；开发规则与当前设计系统见 `.trae/rules/mindguard-migration.md`。本文件仅作历史回溯参考。

# 数据库文档

## 文档信息

| 项目名称 | 基于AI的心理健康检测与辅助系统 |
|---------|------------------------------|
| 文档版本 | V1.1 |
| 编写日期 | 2026-03-09 |
| 编写人 | [林秋颜] |

---

## 一、数据库概述

### 1.1 数据库信息

| 项目 | 说明 |
|------|------|
| 数据库名称 | mental_health |
| 字符集 | utf8mb4 |
| 排序规则 | utf8mb4_unicode_ci |
| 存储引擎 | InnoDB |

### 1.2 数据表概览

| 表名 | 说明 | 记录数预估 |
|------|------|-----------|
| user | 用户信息表 | 10万+ |
| scale | 心理量表表 | 10+ |
| question | 量表题目表 | 100+ |
| assessment | 测评记录表 | 100万+ |
| assessment_answer | 答题详情表 | 1000万+ |
| emotion_diary | 情绪日记表 | 500万+ |
| chat_record | 对话记录表 | 1000万+ |
| chat_session | 对话会话表 | 100万+ |
| article | 文章知识表 | 1000+ |
| article_category | 文章分类表 | 10+ |
| course | 课程表 | 100+ |
| warning | 预警记录表 | 10万+ |
| user_profile | 用户画像表 | 10万+ |

---

## 二、ER图

```
                                    ┌─────────────────┐
                                    │   user_profile  │
                                    ├─────────────────┤
                                    │ id              │
                                    │ user_id    ◀────┼────┐
                                    │ total_assessment │    │
                                    │ avg_score       │    │
                                    │ risk_trend      │    │
                                    └─────────────────┘    │
                                                           │
┌─────────────────┐                                        │
│      user       │                                        │
├─────────────────┤                                        │
│ id              │◀───────────────────────────────────────┤
│ username        │                                        │
│ password        │            ┌─────────────────┐        │
│ nickname        │            │    warning      │        │
│ avatar          │            ├─────────────────┤        │
│ gender          │◀───────────│ id              │        │
│ age             │            │ user_id         │        │
│ role            │            │ risk_level      │        │
│ status          │            │ trigger_source  │        │
│ created_at      │            │ trigger_content │        │
│ updated_at      │            │ status          │        │
└────────┬────────┘            │ handler_id      │        │
         │                     │ created_at      │        │
         │                     └─────────────────┘        │
         │                                                │
         │    ┌─────────────────┐                         │
         │    │     scale       │                         │
         │    ├─────────────────┤                         │
         │    │ id              │                         │
         │    │ name            │                         │
         │    │ description     │                         │
         │    │ category        │                         │
         │    │ question_num    │                         │
         │    │ estimated_time  │                         │
         │    │ status          │                         │
         │    └────────┬────────┘                         │
         │             │                                  │
         │             │ 1:N                              │
         │             ▼                                  │
         │    ┌─────────────────┐                         │
         │    │    question     │                         │
         │    ├─────────────────┤                         │
         │    │ id              │                         │
         │    │ scale_id   ◀────┼─────────────────────────┤
         │    │ order_num       │                         │
         │    │ content         │                         │
         │    │ options         │                         │
         │    │ score_rule      │                         │
         │    └────────┬────────┘                         │
         │             │                                  │
         │             │                                  │
         ▼             ▼                                  │
┌─────────────────┐  ┌─────────────────┐                 │
│   assessment    │  │assessment_answer │                │
├─────────────────┤  ├─────────────────┤                 │
│ id              │◀─│ id              │                 │
│ user_id    ◀────┼──│ assessment_id   │                 │
│ scale_id   ◀────┼──│ question_id ◀───┼─────────────────┘
│ total_score     │  │ answer          │
│ risk_level      │  │ created_at      │
│ report          │  └─────────────────┘
│ created_at      │
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│  chat_session   │       │   chat_record   │
├─────────────────┤       ├─────────────────┤
│ id              │◀──────│ id              │
│ user_id    ◀────┼───┐   │ session_id      │
│ title           │   │   │ role            │
│ created_at      │   │   │ content         │
│ updated_at      │   │   │ sentiment_score │
└─────────────────┘   │   │ created_at      │
                      │   └─────────────────┘
                      │
                      │   ┌─────────────────┐
                      │   │  emotion_diary  │
                      │   ├─────────────────┤
                      └───│ id              │
                          │ user_id         │
                          │ emotion_type    │
                          │ emotion_score   │
                          │ content         │
                          │ sentiment_score │
                          │ ai_analysis     │
                          │ created_at      │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│article_category │       │     article     │
├─────────────────┤       ├─────────────────┤
│ id              │◀──────│ id              │
│ name            │       │ category_id     │
│ description     │       │ title           │
│ sort            │       │ summary         │
│ created_at      │       │ content         │
└─────────────────┘       │ cover_image     │
                          │ author          │
                          │ view_count      │
                          │ status          │
                          │ created_at      │
                          └─────────────────┘
```

---

## 三、数据表详细设计

### 3.1 用户表 (user)

**表说明**：存储系统用户信息

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| username | VARCHAR | 50 | 否 | - | 用户名（唯一） |
| password | VARCHAR | 255 | 否 | - | 密码（BCrypt加密） |
| nickname | VARCHAR | 50 | 是 | NULL | 昵称 |
| avatar | VARCHAR | 255 | 是 | NULL | 头像URL |
| gender | TINYINT | - | 是 | 0 | 性别：0未知 1男 2女 |
| age | INT | - | 是 | NULL | 年龄 |
| role | VARCHAR | 20 | 否 | 'user' | 角色：user用户 admin管理员 |
| status | TINYINT | - | 否 | 1 | 状态：0禁用 1正常 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**：

| 索引名 | 索引类型 | 字段 |
|--------|----------|------|
| PRIMARY | 主键索引 | id |
| uk_username | 唯一索引 | username |
| idx_status | 普通索引 | status |
| idx_created_at | 普通索引 | created_at |

**建表语句**：

```sql
CREATE TABLE `user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `password` VARCHAR(255) NOT NULL COMMENT '密码',
  `nickname` VARCHAR(50) DEFAULT NULL COMMENT '昵称',
  `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
  `gender` TINYINT DEFAULT 0 COMMENT '性别：0未知 1男 2女',
  `age` INT DEFAULT NULL COMMENT '年龄',
  `role` VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：0禁用 1正常',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

---

### 3.2 心理量表表 (scale)

**表说明**：存储心理量表基本信息

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| name | VARCHAR | 100 | 否 | - | 量表名称 |
| description | TEXT | - | 是 | NULL | 量表描述 |
| category | VARCHAR | 50 | 否 | - | 分类：depression/anxiety/stress |
| question_num | INT | - | 否 | 0 | 题目数量 |
| estimated_time | INT | - | 否 | 5 | 预计用时（分钟） |
| scoring_rule | TEXT | - | 是 | NULL | 计分规则（JSON） |
| interpretation | TEXT | - | 是 | NULL | 结果解读（JSON） |
| status | TINYINT | - | 否 | 1 | 状态：0禁用 1正常 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**：

| 索引名 | 索引类型 | 字段 |
|--------|----------|------|
| PRIMARY | 主键索引 | id |
| idx_category | 普通索引 | category |
| idx_status | 普通索引 | status |

**建表语句**：

```sql
CREATE TABLE `scale` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` VARCHAR(100) NOT NULL COMMENT '量表名称',
  `description` TEXT DEFAULT NULL COMMENT '量表描述',
  `category` VARCHAR(50) NOT NULL COMMENT '分类',
  `question_num` INT NOT NULL DEFAULT 0 COMMENT '题目数量',
  `estimated_time` INT NOT NULL DEFAULT 5 COMMENT '预计用时',
  `scoring_rule` TEXT DEFAULT NULL COMMENT '计分规则',
  `interpretation` TEXT DEFAULT NULL COMMENT '结果解读',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心理量表表';
```

---

### 3.3 量表题目表 (question)

**表说明**：存储量表题目信息

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| scale_id | BIGINT | - | 否 | - | 量表ID |
| order_num | INT | - | 否 | 0 | 题目序号 |
| content | TEXT | - | 否 | - | 题目内容 |
| options | TEXT | - | 否 | - | 选项（JSON） |
| score_rule | VARCHAR | 50 | 否 | 'sum' | 计分规则：sum/avg |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：

| 索引名 | 索引类型 | 字段 |
|--------|----------|------|
| PRIMARY | 主键索引 | id |
| idx_scale_id | 普通索引 | scale_id |

**建表语句**：

```sql
CREATE TABLE `question` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `scale_id` BIGINT NOT NULL COMMENT '量表ID',
  `order_num` INT NOT NULL DEFAULT 0 COMMENT '题目序号',
  `content` TEXT NOT NULL COMMENT '题目内容',
  `options` TEXT NOT NULL COMMENT '选项JSON',
  `score_rule` VARCHAR(50) NOT NULL DEFAULT 'sum' COMMENT '计分规则',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_scale_id` (`scale_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='量表题目表';
```

---

### 3.4 测评记录表 (assessment)

**表说明**：存储用户测评记录

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| user_id | BIGINT | - | 否 | - | 用户ID |
| scale_id | BIGINT | - | 否 | - | 量表ID |
| total_score | DECIMAL | 5,2 | 否 | 0.00 | 总分 |
| risk_level | VARCHAR | 20 | 否 | 'low' | 风险等级：low/medium/high |
| report | TEXT | - | 是 | NULL | 评估报告（JSON） |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：

| 索引名 | 索引类型 | 字段 |
|--------|----------|------|
| PRIMARY | 主键索引 | id |
| idx_user_id | 普通索引 | user_id |
| idx_scale_id | 普通索引 | scale_id |
| idx_risk_level | 普通索引 | risk_level |
| idx_created_at | 普通索引 | created_at |

**建表语句**：

```sql
CREATE TABLE `assessment` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `scale_id` BIGINT NOT NULL COMMENT '量表ID',
  `total_score` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '总分',
  `risk_level` VARCHAR(20) NOT NULL DEFAULT 'low' COMMENT '风险等级',
  `report` TEXT DEFAULT NULL COMMENT '评估报告',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_scale_id` (`scale_id`),
  KEY `idx_risk_level` (`risk_level`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测评记录表';
```

---

### 3.5 答题详情表 (assessment_answer)

**表说明**：存储用户答题详情

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| assessment_id | BIGINT | - | 否 | - | 测评记录ID |
| question_id | BIGINT | - | 否 | - | 题目ID |
| answer | INT | - | 否 | 0 | 答案值 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：

| 索引名 | 索引类型 | 字段 |
|--------|----------|------|
| PRIMARY | 主键索引 | id |
| idx_assessment_id | 普通索引 | assessment_id |
| idx_question_id | 普通索引 | question_id |

**建表语句**：

```sql
CREATE TABLE `assessment_answer` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `assessment_id` BIGINT NOT NULL COMMENT '测评记录ID',
  `question_id` BIGINT NOT NULL COMMENT '题目ID',
  `answer` INT NOT NULL DEFAULT 0 COMMENT '答案值',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_assessment_id` (`assessment_id`),
  KEY `idx_question_id` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='答题详情表';
```

---

### 3.6 情绪日记表 (emotion_diary)

**表说明**：存储用户情绪日记

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| user_id | BIGINT | - | 否 | - | 用户ID |
| emotion_type | VARCHAR | 20 | 否 | - | 情绪类型 |
| emotion_score | INT | - | 否 | 5 | 情绪分数：1-10 |
| content | TEXT | - | 否 | - | 日记内容 |
| sentiment_score | DECIMAL | 3,2 | 是 | NULL | 情感分数：0-1 |
| ai_analysis | TEXT | - | 是 | NULL | AI分析结果（JSON） |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：

| 索引名 | 索引类型 | 字段 |
|--------|----------|------|
| PRIMARY | 主键索引 | id |
| idx_user_id | 普通索引 | user_id |
| idx_emotion_type | 普通索引 | emotion_type |
| idx_created_at | 普通索引 | created_at |

**建表语句**：

```sql
CREATE TABLE `emotion_diary` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `emotion_type` VARCHAR(20) NOT NULL COMMENT '情绪类型',
  `emotion_score` INT NOT NULL DEFAULT 5 COMMENT '情绪分数',
  `content` TEXT NOT NULL COMMENT '日记内容',
  `sentiment_score` DECIMAL(3,2) DEFAULT NULL COMMENT '情感分数',
  `ai_analysis` TEXT DEFAULT NULL COMMENT 'AI分析结果',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_emotion_type` (`emotion_type`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情绪日记表';
```

---

### 3.7 对话会话表 (chat_session)

**表说明**：存储用户对话会话

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| user_id | BIGINT | - | 否 | - | 用户ID |
| title | VARCHAR | 100 | 是 | NULL | 会话标题 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**建表语句**：

```sql
CREATE TABLE `chat_session` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(100) DEFAULT NULL COMMENT '会话标题',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话会话表';
```

---

### 3.8 对话记录表 (chat_record)

**表说明**：存储用户对话记录

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| session_id | BIGINT | - | 否 | - | 会话ID |
| user_id | BIGINT | - | 否 | - | 用户ID |
| role | VARCHAR | 20 | 否 | - | 角色：user/assistant |
| content | TEXT | - | 否 | - | 对话内容 |
| sentiment_score | DECIMAL | 3,2 | 是 | NULL | 情感分数 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**建表语句**：

```sql
CREATE TABLE `chat_record` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `session_id` BIGINT NOT NULL COMMENT '会话ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `role` VARCHAR(20) NOT NULL COMMENT '角色',
  `content` TEXT NOT NULL COMMENT '对话内容',
  `sentiment_score` DECIMAL(3,2) DEFAULT NULL COMMENT '情感分数',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话记录表';
```

---

### 3.9 文章分类表 (article_category)

**表说明**：存储文章分类信息

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| name | VARCHAR | 50 | 否 | - | 分类名称 |
| description | VARCHAR | 255 | 是 | NULL | 分类描述 |
| sort | INT | - | 否 | 0 | 排序 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**建表语句**：

```sql
CREATE TABLE `article_category` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` VARCHAR(50) NOT NULL COMMENT '分类名称',
  `description` VARCHAR(255) DEFAULT NULL COMMENT '分类描述',
  `sort` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章分类表';
```

---

### 3.10 文章表 (article)

**表说明**：存储心理健康文章

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| category_id | BIGINT | - | 否 | - | 分类ID |
| title | VARCHAR | 200 | 否 | - | 文章标题 |
| summary | VARCHAR | 500 | 是 | NULL | 文章摘要 |
| content | LONGTEXT | - | 否 | - | 文章内容 |
| cover_image | VARCHAR | 255 | 是 | NULL | 封面图片 |
| author | VARCHAR | 50 | 是 | NULL | 作者 |
| view_count | INT | - | 否 | 0 | 浏览量 |
| status | TINYINT | - | 否 | 1 | 状态：0草稿 1发布 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**建表语句**：

```sql
CREATE TABLE `article` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `category_id` BIGINT NOT NULL COMMENT '分类ID',
  `title` VARCHAR(200) NOT NULL COMMENT '文章标题',
  `summary` VARCHAR(500) DEFAULT NULL COMMENT '文章摘要',
  `content` LONGTEXT NOT NULL COMMENT '文章内容',
  `cover_image` VARCHAR(255) DEFAULT NULL COMMENT '封面图片',
  `author` VARCHAR(50) DEFAULT NULL COMMENT '作者',
  `view_count` INT NOT NULL DEFAULT 0 COMMENT '浏览量',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_category_id` (`category_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章表';
```

---

### 3.11 预警记录表 (warning)

**表说明**：存储预警记录

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| user_id | BIGINT | - | 否 | - | 用户ID |
| risk_level | VARCHAR | 20 | 否 | - | 风险等级：low/medium/high |
| trigger_source | VARCHAR | 50 | 否 | - | 触发来源：assessment/diary/chat |
| trigger_content | TEXT | - | 是 | NULL | 触发内容 |
| status | VARCHAR | 20 | 否 | 'pending' | 状态：pending/processing/resolved |
| handler_id | BIGINT | - | 是 | NULL | 处理人ID |
| handle_note | TEXT | - | 是 | NULL | 处理备注 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| handled_at | DATETIME | - | 是 | NULL | 处理时间 |

**建表语句**：

```sql
CREATE TABLE `warning` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `risk_level` VARCHAR(20) NOT NULL COMMENT '风险等级',
  `trigger_source` VARCHAR(50) NOT NULL COMMENT '触发来源',
  `trigger_content` TEXT DEFAULT NULL COMMENT '触发内容',
  `status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态',
  `handler_id` BIGINT DEFAULT NULL COMMENT '处理人ID',
  `handle_note` TEXT DEFAULT NULL COMMENT '处理备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `handled_at` DATETIME DEFAULT NULL COMMENT '处理时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_risk_level` (`risk_level`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预警记录表';
```

---

### 3.12 用户画像表 (user_profile)

**表说明**：存储用户心理画像

| 字段名 | 数据类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|----------|------|--------|--------|------|
| id | BIGINT | - | 否 | AUTO_INCREMENT | 主键ID |
| user_id | BIGINT | - | 否 | - | 用户ID |
| total_assessment | INT | - | 否 | 0 | 测评总次数 |
| avg_score | DECIMAL | 5,2 | 是 | NULL | 平均得分 |
| risk_trend | TEXT | - | 是 | NULL | 风险趋势（JSON） |
| emotion_trend | TEXT | - | 是 | NULL | 情绪趋势（JSON） |
| last_assessment_at | DATETIME | - | 是 | NULL | 最后测评时间 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**建表语句**：

```sql
CREATE TABLE `user_profile` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `total_assessment` INT NOT NULL DEFAULT 0 COMMENT '测评总次数',
  `avg_score` DECIMAL(5,2) DEFAULT NULL COMMENT '平均得分',
  `risk_trend` TEXT DEFAULT NULL COMMENT '风险趋势',
  `emotion_trend` TEXT DEFAULT NULL COMMENT '情绪趋势',
  `last_assessment_at` DATETIME DEFAULT NULL COMMENT '最后测评时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户画像表';
```

---

## 四、初始化数据

### 4.1 心理量表初始数据

```sql
-- PHQ-9抑郁量表
INSERT INTO `scale` (`id`, `name`, `description`, `category`, `question_num`, `estimated_time`, `scoring_rule`, `interpretation`) VALUES
(1, 'PHQ-9抑郁量表', '患者健康问卷抑郁量表，用于抑郁症状筛查', 'depression', 9, 5, 
'{"type": "sum", "max_score": 27}',
'[{"min": 0, "max": 4, "level": "low", "text": "无抑郁症状"}, {"min": 5, "max": 9, "level": "low", "text": "轻度抑郁"}, {"min": 10, "max": 14, "level": "medium", "text": "中度抑郁"}, {"min": 15, "max": 19, "level": "medium", "text": "中重度抑郁"}, {"min": 20, "max": 27, "level": "high", "text": "重度抑郁"}]');

-- GAD-7焦虑量表
INSERT INTO `scale` (`id`, `name`, `description`, `category`, `question_num`, `estimated_time`, `scoring_rule`, `interpretation`) VALUES
(2, 'GAD-7焦虑量表', '广泛性焦虑障碍量表，用于焦虑症状筛查', 'anxiety', 7, 3,
'{"type": "sum", "max_score": 21}',
'[{"min": 0, "max": 4, "level": "low", "text": "无焦虑症状"}, {"min": 5, "max": 9, "level": "low", "text": "轻度焦虑"}, {"min": 10, "max": 14, "level": "medium", "text": "中度焦虑"}, {"min": 15, "max": 21, "level": "high", "text": "重度焦虑"}]');

-- PSS-10压力量表
INSERT INTO `scale` (`id`, `name`, `description`, `category`, `question_num`, `estimated_time`, `scoring_rule`, `interpretation`) VALUES
(3, 'PSS-10压力量表', '感知压力量表，用于评估个体感知到的压力水平', 'stress', 10, 5,
'{"type": "sum", "max_score": 40}',
'[{"min": 0, "max": 13, "level": "low", "text": "低压力水平"}, {"min": 14, "max": 26, "level": "medium", "text": "中等压力水平"}, {"min": 27, "max": 40, "level": "high", "text": "高压力水平"}]');
```

### 4.2 PHQ-9题目数据

```sql
INSERT INTO `question` (`scale_id`, `order_num`, `content`, `options`) VALUES
(1, 1, '做事时提不起劲或没有兴趣', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(1, 2, '感到心情低落、沮丧或绝望', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(1, 3, '入睡困难、睡不着或睡眠过多', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(1, 4, '感觉疲倦或没有活力', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(1, 5, '食欲不振或吃得太多', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(1, 6, '觉得自己很糟，或觉得自己很失败，让自己或家人失望', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(1, 7, '对事物专注有困难，例如阅读报纸或看电视时', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(1, 8, '动作或说话速度缓慢到别人已经察觉，或相反，烦躁或坐立不安、动来动去', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(1, 9, '有不如死掉或用某种方式伤害自己的念头', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]');
```

### 4.3 文章分类初始数据

```sql
INSERT INTO `article_category` (`name`, `description`, `sort`) VALUES
('抑郁情绪', '关于抑郁情绪的文章', 1),
('焦虑情绪', '关于焦虑情绪的文章', 2),
('压力管理', '关于压力管理的文章', 3),
('人际关系', '关于人际关系的文章', 4),
('自我成长', '关于自我成长的文章', 5),
('情绪调节', '关于情绪调节的文章', 6);
```

### 4.4 管理员账户

```sql
INSERT INTO `user` (`username`, `password`, `nickname`, `role`, `status`) VALUES
('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '系统管理员', 'admin', 1);
```

---

## 五、数据库优化建议

### 5.1 索引优化

- 为高频查询字段添加索引
- 避免过多索引影响写入性能
- 定期分析索引使用情况

### 5.2 查询优化

- 使用分页查询避免全表扫描
- 合理使用JOIN，避免子查询
- 使用EXPLAIN分析慢查询

### 5.3 数据归档

- 定期归档历史测评数据
- 保留近期数据在主表
- 历史数据迁移到归档表

### 5.4 分表策略（可选）

- 测评记录表按用户ID分表
- 对话记录表按时间分表
- 日记表按用户ID分表

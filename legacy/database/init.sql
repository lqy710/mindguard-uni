-- ============================================
-- 心理健康检测与辅助系统 数据库初始化脚本
-- 版本: V1.0
-- 创建时间: 2026-03-06
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `mental_health` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `mental_health`;

-- ============================================
-- 一、创建数据表
-- ============================================

-- 1. 用户表
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

-- 2. 心理量表表
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

-- 3. 量表题目表
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

-- 4. 测评记录表
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

-- 5. 答题详情表
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

-- 6. 情绪日记表
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

-- 7. 对话会话表
CREATE TABLE `chat_session` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(100) DEFAULT NULL COMMENT '会话标题',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话会话表';

-- 8. 对话记录表
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

-- 8.1 对话反馈表（AI 效果数据回流）
CREATE TABLE `chat_feedback` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `session_id` BIGINT NOT NULL COMMENT '会话ID',
  `record_id` BIGINT NOT NULL COMMENT '被评价的AI回复ID(chat_record.id)',
  `rating` TINYINT NOT NULL COMMENT '评价: 1=点赞, -1=点踩',
  `category` VARCHAR(32) DEFAULT NULL COMMENT '负反馈原因: irrelevant/unsafe/unprofessional/other',
  `comment` VARCHAR(500) DEFAULT NULL COMMENT '用户补充说明',
  `reply_content` TEXT COMMENT '冗余的AI回复内容,便于离线标注',
  `user_content` TEXT COMMENT '冗余的用户提问内容,便于构造评估样本',
  `stage` VARCHAR(20) DEFAULT NULL COMMENT '会话阶段',
  `label_status` TINYINT NOT NULL DEFAULT 0 COMMENT '标注状态: 0=未标注, 1=已标注, 2=已转评估样本',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_record` (`user_id`, `record_id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_category` (`category`),
  KEY `idx_label_status` (`label_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话反馈表';

-- 9. 文章分类表
CREATE TABLE `article_category` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` VARCHAR(50) NOT NULL COMMENT '分类名称',
  `description` VARCHAR(255) DEFAULT NULL COMMENT '分类描述',
  `sort` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章分类表';

-- 10. 文章表
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

-- 11. 预警记录表
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

-- 12. 用户画像表
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

-- ============================================
-- 二、插入初始数据
-- ============================================

-- 1. 管理员账户 (密码: admin123, BCrypt加密)
INSERT INTO `user` (`username`, `password`, `nickname`, `role`, `status`) VALUES
('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '系统管理员', 'admin', 1);

-- 2. 测试用户账户 (密码: user123)
INSERT INTO `user` (`username`, `password`, `nickname`, `gender`, `age`, `role`, `status`) VALUES
('testuser', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', '测试用户', 1, 25, 'user', 1);

-- 3. 心理量表数据
INSERT INTO `scale` (`id`, `name`, `description`, `category`, `question_num`, `estimated_time`, `scoring_rule`, `interpretation`) VALUES
(1, 'PHQ-9抑郁量表', '患者健康问卷抑郁量表（Patient Health Questionnaire-9），是国际通用的抑郁症状筛查工具。该量表包含9个条目，用于评估过去两周内抑郁症状的严重程度。', 'depression', 9, 5, 
'{"type": "sum", "max_score": 27}',
'[{"min": 0, "max": 4, "level": "low", "text": "无抑郁症状", "suggestion": "您的心理状态良好，继续保持积极的生活方式。"}, {"min": 5, "max": 9, "level": "low", "text": "轻度抑郁", "suggestion": "建议关注自身情绪变化，适当进行运动和社交活动。"}, {"min": 10, "max": 14, "level": "medium", "text": "中度抑郁", "suggestion": "建议寻求专业心理咨询师的帮助，进行进一步评估。"}, {"min": 15, "max": 19, "level": "medium", "text": "中重度抑郁", "suggestion": "强烈建议尽快就医，接受专业治疗。"}, {"min": 20, "max": 27, "level": "high", "text": "重度抑郁", "suggestion": "请立即寻求专业医疗帮助，您可能需要药物治疗和心理治疗。"}]'),

(2, 'GAD-7焦虑量表', '广泛性焦虑障碍量表（Generalized Anxiety Disorder-7），是国际通用的焦虑症状筛查工具。该量表包含7个条目，用于评估过去两周内焦虑症状的严重程度。', 'anxiety', 7, 3,
'{"type": "sum", "max_score": 21}',
'[{"min": 0, "max": 4, "level": "low", "text": "无焦虑症状", "suggestion": "您的心理状态良好，继续保持放松的生活方式。"}, {"min": 5, "max": 9, "level": "low", "text": "轻度焦虑", "suggestion": "建议学习放松技巧，如深呼吸、冥想等。"}, {"min": 10, "max": 14, "level": "medium", "text": "中度焦虑", "suggestion": "建议寻求专业心理咨询师的帮助。"}, {"min": 15, "max": 21, "level": "high", "text": "重度焦虑", "suggestion": "请尽快就医，接受专业治疗。"}]'),

(3, 'PSS-10压力量表', '感知压力量表（Perceived Stress Scale-10），用于评估个体在过去一个月内感知到的压力水平。该量表包含10个条目，涵盖不可预测性和不可控制感等方面。', 'stress', 10, 5,
'{"type": "sum", "max_score": 40}',
'[{"min": 0, "max": 13, "level": "low", "text": "低压力水平", "suggestion": "您的压力水平较低，保持良好的生活节奏。"}, {"min": 14, "max": 26, "level": "medium", "text": "中等压力水平", "suggestion": "建议适当调整生活节奏，增加休息和娱乐时间。"}, {"min": 27, "max": 40, "level": "high", "text": "高压力水平", "suggestion": "建议寻求专业帮助，学习压力管理技巧。"}]'),

(4, 'SDS抑郁自评量表', '抑郁自评量表（Self-Rating Depression Scale），由Zung编制，用于评估抑郁症状的严重程度。该量表包含20个条目，涵盖情感、躯体和认知症状。', 'depression', 20, 10,
'{"type": "index", "max_score": 80}',
'[{"min": 0, "max": 39, "level": "low", "text": "无抑郁", "suggestion": "您的心理状态正常。"}, {"min": 40, "max": 47, "level": "low", "text": "轻度抑郁", "suggestion": "建议关注自身情绪，适当调节。"}, {"min": 48, "max": 55, "level": "medium", "text": "中度抑郁", "suggestion": "建议寻求专业帮助。"}, {"min": 56, "max": 80, "level": "high", "text": "重度抑郁", "suggestion": "请尽快就医治疗。"}]'),

(5, 'SAS焦虑自评量表', '焦虑自评量表（Self-Rating Anxiety Scale），由Zung编制，用于评估焦虑症状的严重程度。该量表包含20个条目，涵盖焦虑的情感和躯体症状。', 'anxiety', 20, 10,
'{"type": "index", "max_score": 80}',
'[{"min": 0, "max": 39, "level": "low", "text": "无焦虑", "suggestion": "您的心理状态正常。"}, {"min": 40, "max": 47, "level": "low", "text": "轻度焦虑", "suggestion": "建议学习放松技巧。"}, {"min": 48, "max": 55, "level": "medium", "text": "中度焦虑", "suggestion": "建议寻求专业帮助。"}, {"min": 56, "max": 80, "level": "high", "text": "重度焦虑", "suggestion": "请尽快就医治疗。"}]');

-- 4. PHQ-9量表题目
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

-- 5. GAD-7量表题目
INSERT INTO `question` (`scale_id`, `order_num`, `content`, `options`) VALUES
(2, 1, '感到紧张、焦虑或急切', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(2, 2, '不能停止或控制担忧', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(2, 3, '对各种事情过分担忧', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(2, 4, '很难放松', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(2, 5, '由于不安而无法静坐', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(2, 6, '变得容易烦恼或急躁', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]'),
(2, 7, '感到害怕，似乎将有可怕的事情发生', '[{"value": 0, "label": "完全不会"}, {"value": 1, "label": "好几天"}, {"value": 2, "label": "一半以上的天数"}, {"value": 3, "label": "几乎每天"}]');

-- 6. PSS-10量表题目
INSERT INTO `question` (`scale_id`, `order_num`, `content`, `options`) VALUES
(3, 1, '在过去一个月里，您有多少次因为发生了意外的事情而感到心烦意乱？', '[{"value": 0, "label": "从不"}, {"value": 1, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}]'),
(3, 2, '在过去一个月里，您有多少次感到无法控制生活中重要的事情？', '[{"value": 0, "label": "从不"}, {"value": 1, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}]'),
(3, 3, '在过去一个月里，您有多少次感到紧张和压力？', '[{"value": 0, "label": "从不"}, {"value": 1, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}]'),
(3, 4, '在过去一个月里，您有多少次对自己处理个人问题的能力感到自信？', '[{"value": 4, "label": "从不"}, {"value": 3, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 1, "label": "经常"}, {"value": 0, "label": "总是"}]'),
(3, 5, '在过去一个月里，您有多少次感到事情按照自己的意愿发展？', '[{"value": 4, "label": "从不"}, {"value": 3, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 1, "label": "经常"}, {"value": 0, "label": "总是"}]'),
(3, 6, '在过去一个月里，您有多少次发现自己无法应对所有必须做的事情？', '[{"value": 0, "label": "从不"}, {"value": 1, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}]'),
(3, 7, '在过去一个月里，您有多少次能够控制生活中的烦恼？', '[{"value": 4, "label": "从不"}, {"value": 3, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 1, "label": "经常"}, {"value": 0, "label": "总是"}]'),
(3, 8, '在过去一个月里，您有多少次觉得所有事情都顺利？', '[{"value": 4, "label": "从不"}, {"value": 3, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 1, "label": "经常"}, {"value": 0, "label": "总是"}]'),
(3, 9, '在过去一个月里，您有多少次因为无法控制的事情而生气？', '[{"value": 0, "label": "从不"}, {"value": 1, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}]'),
(3, 10, '在过去一个月里，您有多少次感到困难堆积如山，无法克服？', '[{"value": 0, "label": "从不"}, {"value": 1, "label": "偶尔"}, {"value": 2, "label": "有时"}, {"value": 3, "label": "经常"}, {"value": 4, "label": "总是"}]');

-- 7. SDS抑郁自评量表题目
INSERT INTO `question` (`scale_id`, `order_num`, `content`, `options`) VALUES
(4, 1, '我感到情绪沮丧，郁闷', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 2, '我感到早晨心情最好', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 3, '我要哭或想哭', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 4, '我夜间睡眠不好', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 5, '我吃饭像平时一样多', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 6, '我与异性密切接触时和以往一样感到愉快', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 7, '我感到体重减轻', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 8, '我为便秘烦恼', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 9, '我的心跳比平时快', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 10, '我无故感到疲劳', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 11, '我的头脑像往常一样清楚', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 12, '我做事情像平时一样不感到困难', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 13, '我坐卧不安，难以保持平静', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 14, '我对未来感到有希望', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 15, '我比平时更容易激怒', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 16, '我觉得决定什么事情很容易', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 17, '我感到自己是有用的和不可缺少的人', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 18, '我的生活很有意义', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(4, 19, '假若我死了别人会过得更好', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(4, 20, '我仍旧喜爱自己平时喜爱的东西', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]');

-- 8. SAS焦虑自评量表题目
INSERT INTO `question` (`scale_id`, `order_num`, `content`, `options`) VALUES
(5, 1, '我觉得比平时容易紧张和着急', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 2, '我无缘无故地感到害怕', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 3, '我容易心里烦乱或觉得惊恐', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 4, '我觉得我可能将要发疯', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 5, '我觉得一切都很好，也不会发生什么不幸', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(5, 6, '我手脚发抖打颤', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 7, '我因为头痛、颈痛和背痛而苦恼', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 8, '我感觉容易衰弱和疲乏', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 9, '我觉得心平气和，并且容易安静坐着', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(5, 10, '我觉得心跳很快', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 11, '我因为一阵阵头晕而苦恼', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 12, '我有晕倒发作，或觉得要晕倒似的', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 13, '我吸气呼气都感到很容易', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(5, 14, '我的手脚麻木和刺痛', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 15, '我因为胃痛和消化不良而苦恼', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 16, '我常常要小便', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 17, '我的手常常是干燥温暖的', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(5, 18, '我脸红发热', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]'),
(5, 19, '我容易入睡并且一夜睡得很好', '[{"value": 4, "label": "没有或很少时间"}, {"value": 3, "label": "小部分时间"}, {"value": 2, "label": "相当多时间"}, {"value": 1, "label": "绝大部分或全部时间"}]'),
(5, 20, '我做恶梦', '[{"value": 1, "label": "没有或很少时间"}, {"value": 2, "label": "小部分时间"}, {"value": 3, "label": "相当多时间"}, {"value": 4, "label": "绝大部分或全部时间"}]');

-- 9. 文章分类数据
INSERT INTO `article_category` (`name`, `description`, `sort`) VALUES
('抑郁情绪', '关于抑郁情绪的认识、调节和应对方法', 1),
('焦虑情绪', '关于焦虑情绪的管理和缓解技巧', 2),
('压力管理', '关于压力识别、应对和预防的方法', 3),
('人际关系', '关于人际交往、沟通技巧和关系维护', 4),
('自我成长', '关于自我认知、个人发展和人生规划', 5),
('情绪调节', '关于情绪管理、情感表达和心理调适', 6),
('睡眠健康', '关于睡眠质量改善和失眠应对', 7),
('职场心理', '关于工作压力、职业发展和职场适应', 8);

-- 10. 示例文章数据
INSERT INTO `article` (`category_id`, `title`, `summary`, `content`, `author`, `view_count`, `status`) VALUES
(1, '认识抑郁：它不只是"心情不好"', '抑郁症是一种常见的心理疾病，了解它的症状和表现，有助于我们及时发现问题并寻求帮助。', 
'<h2>什么是抑郁症？</h2><p>抑郁症是一种常见的心理疾病，它不同于普通的心情不好或短暂的情绪低落。抑郁症会持续影响一个人的思维、情感和日常功能。</p><h2>抑郁症的常见症状</h2><p>1. 持续的悲伤、空虚或绝望感</p><p>2. 对以前喜欢的活动失去兴趣</p><p>3. 睡眠问题（失眠或睡眠过多）</p><p>4. 疲劳和精力不足</p><p>5. 食欲变化</p><p>6. 注意力难以集中</p><p>7. 自责或无价值感</p><h2>如何应对？</h2><p>如果您或您身边的人出现上述症状，建议及时寻求专业帮助。心理咨询和适当的治疗可以有效改善抑郁症状。</p>', 
'心理健康专家', 156, 1),

(2, '焦虑症的自我调节方法', '焦虑是现代人常见的心理问题，学会正确的自我调节方法，可以帮助我们更好地应对焦虑情绪。', 
'<h2>认识焦虑</h2><p>焦虑是一种正常的情绪反应，但当焦虑过度或持续时间过长时，就可能影响我们的生活质量。</p><h2>自我调节技巧</h2><p><strong>1. 深呼吸练习</strong></p><p>缓慢深呼吸可以激活副交感神经系统，帮助身体放松。尝试4-7-8呼吸法：吸气4秒，屏息7秒，呼气8秒。</p><p><strong>2. 渐进式肌肉放松</strong></p><p>从头到脚依次紧张和放松各个肌肉群，帮助身体识别和释放紧张。</p><p><strong>3. 正念冥想</strong></p><p>关注当下，不加评判地观察自己的思想和感受，减少对未来的担忧。</p><p><strong>4. 认知重构</strong></p><p>识别并挑战消极的自动思维，用更合理的想法替代它们。</p>', 
'心理咨询师', 203, 1),

(3, '压力管理：让生活更轻松', '压力是现代生活不可避免的一部分，学会有效管理压力，可以提高生活质量，保持身心健康。', 
'<h2>压力的来源</h2><p>压力可能来自工作、学习、人际关系、经济状况等多个方面。了解压力的来源是管理的第一步。</p><h2>压力管理策略</h2><p><strong>时间管理</strong></p><p>合理安排时间，设置优先级，避免拖延，可以减少因时间紧迫带来的压力。</p><p><strong>运动锻炼</strong></p><p>规律的运动可以释放内啡肽，改善心情，增强应对压力的能力。</p><p><strong>社交支持</strong></p><p>与家人朋友保持联系，分享感受，获得情感支持。</p><p><strong>健康生活方式</strong></p><p>保证充足睡眠，均衡饮食，限制咖啡因和酒精摄入。</p>', 
'健康顾问', 178, 1),

(4, '如何建立健康的人际关系', '良好的人际关系是心理健康的重要组成部分，学会建立和维护健康的关系，可以让生活更加充实。', 
'<h2>健康关系的特征</h2><p>相互尊重、信任、开放沟通、平等互惠是健康关系的基本特征。</p><h2>建立健康关系的方法</h2><p><strong>1. 学会倾听</strong></p><p>真诚地倾听对方，理解他们的感受和需求。</p><p><strong>2. 表达自己</strong></p><p>清晰、诚实地表达自己的想法和感受，避免被动攻击。</p><p><strong>3. 设定边界</strong></p><p>了解自己的底线，学会说"不"，尊重自己也尊重他人。</p><p><strong>4. 处理冲突</strong></p><p>以建设性的方式处理分歧，寻求双赢的解决方案。</p>', 
'人际关系专家', 145, 1),

(5, '自我成长：认识你自己', '自我认知是个人成长的基础，了解自己的优势、劣势、价值观和目标，可以帮助我们更好地规划人生。', 
'<h2>为什么自我认知很重要？</h2><p>自我认知是情商的核心组成部分，它影响着我们的决策、人际关系和整体幸福感。</p><h2>提升自我认知的方法</h2><p><strong>1. 自我反思</strong></p><p>定期花时间思考自己的行为、感受和动机。</p><p><strong>2. 寻求反馈</strong></p><p>向信任的人询问他们眼中的你，获得不同的视角。</p><p><strong>3. 尝试新事物</strong></p><p>通过新的经历发现自己未知的潜能和兴趣。</p><p><strong>4. 写日记</strong></p><p>记录日常经历和感受，帮助理清思路，发现模式。</p>', 
'人生导师', 167, 1),

(6, '情绪管理的艺术', '情绪管理不是压抑情绪，而是学会理解、接纳和适当表达情绪。', 
'<h2>认识情绪</h2><p>情绪是我们对外界事件的反应，没有好坏之分。每种情绪都有其存在的意义。</p><h2>情绪管理技巧</h2><p><strong>1. 情绪识别</strong></p><p>学会准确识别自己的情绪状态，是管理的第一步。</p><p><strong>2. 接纳情绪</strong></p><p>允许自己感受各种情绪，不要试图压抑或否认。</p><p><strong>3. 情绪表达</strong></p><p>找到健康的方式表达情绪，如谈话、写作、运动等。</p><p><strong>4. 情绪调节</strong></p><p>学会在情绪激动时让自己平静下来，如深呼吸、转移注意力等。</p>', 
'心理治疗师', 189, 1),

(7, '改善睡眠质量的10个建议', '良好的睡眠是身心健康的基础，以下是一些科学有效的睡眠改善方法。', 
'<h2>睡眠的重要性</h2><p>睡眠对身体健康、心理健康、认知功能都有重要影响。长期睡眠不足可能导致多种健康问题。</p><h2>改善睡眠的建议</h2><p>1. 保持规律的作息时间</p><p>2. 创造舒适的睡眠环境</p><p>3. 睡前避免使用电子设备</p><p>4. 限制咖啡因和酒精摄入</p><p>5. 规律运动但避免睡前剧烈运动</p><p>6. 管理压力和焦虑</p><p>7. 避免白天过长午睡</p><p>8. 建立睡前放松仪式</p><p>9. 不要在床上做与睡眠无关的事</p><p>10. 如果睡不着，起来做些放松的事</p>', 
'睡眠专家', 234, 1),

(8, '职场压力应对指南', '职场压力是现代工作者面临的普遍问题，学会有效应对，可以保持工作效率和身心健康。', 
'<h2>职场压力的来源</h2><p>工作负荷、人际关系、职业发展不确定性等都可能成为职场压力的来源。</p><h2>应对策略</h2><p><strong>工作方面</strong></p><p>合理规划工作，学会拒绝超出能力范围的任务，寻求必要的支持。</p><p><strong>人际方面</strong></p><p>保持专业态度，学会有效沟通，建立良好的同事关系。</p><p><strong>个人方面</strong></p><p>保持工作与生活的平衡，培养工作外的兴趣爱好，注意自我照顾。</p><p><strong>职业发展</strong></p><p>设定清晰的职业目标，持续学习提升，保持开放心态。</p>', 
'职业顾问', 198, 1);

-- 11. 为测试用户创建用户画像
INSERT INTO `user_profile` (`user_id`, `total_assessment`, `avg_score`) VALUES
(2, 0, NULL);

-- ============================================
-- 三、创建数据库用户（可选）
-- ============================================

-- 创建应用专用数据库用户
-- CREATE USER IF NOT EXISTS 'mental'@'localhost' IDENTIFIED BY 'mental123';
-- GRANT ALL PRIVILEGES ON mental_health.* TO 'mental'@'localhost';
-- FLUSH PRIVILEGES;

-- ============================================
-- 初始化完成
-- ============================================

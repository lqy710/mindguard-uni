-- 修复admin用户密码
-- 密码: admin123
-- BCrypt哈希值: $2a$10$XF85Jz/HWeTtg2VPAPMQJeDBySJzzayNKVtqhbZWsO31UMd3mWuZ.

UPDATE user SET password = '$2a$10$XF85Jz/HWeTtg2VPAPMQJeDBySJzzayNKVtqhbZWsO31UMd3mWuZ.' WHERE username = 'admin';

-- 验证更新
SELECT id, username, password, role, status FROM user WHERE username = 'admin';

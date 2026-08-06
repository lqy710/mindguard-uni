-- 修复用户密码哈希值
-- 密码: admin123 (BCrypt加密)
UPDATE `user` SET `password` = '$2a$10$EqKcp1WFKVQISheBxmXNGexPR.i7QYXOJC.OFfQDT8iSaHuuPdlrW' WHERE `username` = 'admin';

-- 密码: user123 (BCrypt加密)  
UPDATE `user` SET `password` = '$2a$10$EqKcp1WFKVQISheBxmXNGexPR.i7QYXOJC.OFfQDT8iSaHuuPdlrW' WHERE `username` = 'testuser';

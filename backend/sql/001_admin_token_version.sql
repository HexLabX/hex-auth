-- 2026-09: 管理员令牌版本（修改密码后使旧JWT立即失效）
-- 已有数据库执行；新库由 create_all 自动包含
ALTER TABLE admin_users ADD COLUMN token_version INT NOT NULL DEFAULT 0 COMMENT '令牌版本，修改密码后递增使旧令牌失效';

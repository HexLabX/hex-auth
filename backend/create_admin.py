#!/usr/bin/env python3
"""
创建初始管理员用户脚本
"""

import bcrypt
from sqlalchemy.orm import Session
from app.core.database import engine, Base
from app.models.admin_user import AdminUser

# 创建数据库表（如果尚未创建）
Base.metadata.create_all(bind=engine)

# 创建会话
with Session(engine) as session:
    # 检查是否已有管理员用户
    admin = session.query(AdminUser).first()
    
    if admin:
        print(f"管理员用户已存在: {admin.username}")
    else:
        # 使用bcrypt直接生成密码哈希
        password = "admin123"
        password_bytes = password.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        password_hash = hashed_bytes.decode('utf-8')
        
        # 创建初始管理员用户
        initial_admin = AdminUser(
            username="admin",
            password_hash=password_hash,
            status="enabled"
        )
        session.add(initial_admin)
        session.commit()
        print(f"初始管理员用户已创建: username=admin, password=admin123")

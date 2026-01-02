from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class AdminStatus(str, enum.Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    status = Column(Enum(AdminStatus), default=AdminStatus.ENABLED, comment="状态")
    last_login = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
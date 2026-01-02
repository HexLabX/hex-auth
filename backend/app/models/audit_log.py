from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    admin_username = Column(String(50), nullable=False, comment="操作用户名")
    action = Column(String(50), nullable=False, comment="操作类型")
    target_type = Column(String(50), nullable=False, comment="操作对象类型")
    target_id = Column(String(50), nullable=False, comment="操作对象ID")
    detail = Column(JSON, nullable=True, comment="操作详情")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="操作时间")
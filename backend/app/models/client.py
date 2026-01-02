from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ClientType(str, enum.Enum):
    GUI = "gui"
    CLI = "cli"
    SERVICE = "service"
    PLUGIN = "plugin"

class ClientStatus(str, enum.Enum):
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    DISABLED = "disabled"

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    license_id = Column(Integer, ForeignKey("licenses.id"), index=True, nullable=False, comment="关联授权ID")
    product_code = Column(String(50), index=True, nullable=False, comment="产品标识")
    client_fp = Column(String(100), nullable=False, comment="客户端指纹")
    client_type = Column(Enum(ClientType), nullable=False, comment="客户端类型")
    ip_address = Column(String(50), nullable=True, comment="客户端IP地址")
    last_heartbeat = Column(DateTime(timezone=True), onupdate=func.now(), comment="最后心跳时间")
    status = Column(Enum(ClientStatus), default=ClientStatus.NORMAL, comment="状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 唯一约束：(license_id, client_fp)
    __table_args__ = (
        UniqueConstraint('license_id', 'client_fp', name='uq_license_client_fp'),
    )
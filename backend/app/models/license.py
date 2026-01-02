from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Date
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class LicenseStatus(str, enum.Enum):
    UNACTIVATED = "unactivated"
    ACTIVATED = "activated"
    EXPIRED = "expired"
    REVOKED = "revoked"

class License(Base):
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    license_key = Column(String(50), unique=True, index=True, nullable=False, comment="授权码")
    product_code = Column(String(50), index=True, nullable=False, comment="关联产品标识")
    max_devices = Column(Integer, default=1, comment="最大设备数限制")
    expire_at = Column(Date, nullable=False, comment="过期时间")
    status = Column(Enum(LicenseStatus), default=LicenseStatus.UNACTIVATED, comment="状态")
    remark = Column(String(200), nullable=True, comment="备注信息")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
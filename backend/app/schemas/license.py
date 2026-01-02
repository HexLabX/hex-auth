from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.models.license import LicenseStatus

try:
    from typing_extensions import Annotated
    
    # 授权基础模型
    class LicenseBase(BaseModel):
        license_key: Annotated[str, Field(..., min_length=10, max_length=50)]
        product_code: Annotated[str, Field(..., min_length=3, max_length=50)]
        max_devices: Annotated[int, Field(..., ge=1, le=100)]
        expire_at: date
        remark: Optional[Annotated[str, Field(max_length=200)]] = None
    
    # 创建授权请求
    class LicenseCreate(LicenseBase):
        pass
    
    # 更新授权请求
    class LicenseUpdate(BaseModel):
        max_devices: Optional[Annotated[int, Field(ge=1, le=100)]] = None
        expire_at: Optional[date] = None
        remark: Optional[Annotated[str, Field(max_length=200)]] = None
    
    # 授权响应
    class LicenseResponse(LicenseBase):
        id: int
        status: LicenseStatus
        created_at: datetime
        
        class Config:
            from_attributes = True
except ImportError:
    # 兼容旧版本pydantic
    # 授权基础模型
    class LicenseBase(BaseModel):
        license_key: str
        product_code: str
        max_devices: int
        expire_at: date
        remark: Optional[str] = None
        
        class Config:
            schema_extra = {
                "example": {
                    "license_key": "XXXX-XXXX-XXXX-XXXX",
                    "product_code": "XRAY_GUI",
                    "max_devices": 1,
                    "expire_at": "2025-12-31",
                    "remark": "测试授权"
                }
            }
    
    # 创建授权请求
    class LicenseCreate(LicenseBase):
        pass
    
    # 更新授权请求
    class LicenseUpdate(BaseModel):
        max_devices: Optional[int] = None
        expire_at: Optional[date] = None
        remark: Optional[str] = None
        
        class Config:
            schema_extra = {
                "example": {
                    "max_devices": 2,
                    "expire_at": "2026-12-31",
                    "remark": "更新测试授权"
                }
            }
    
    # 授权响应
    class LicenseResponse(LicenseBase):
        id: int
        status: LicenseStatus
        created_at: datetime
        
        class Config:
            orm_mode = True
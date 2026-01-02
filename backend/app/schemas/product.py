from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.product import ProductStatus

try:
    from typing_extensions import Annotated
    
    # 产品基础模型
    class ProductBase(BaseModel):
        product_code: Annotated[str, Field(..., min_length=3, max_length=50)]
        name: Annotated[str, Field(..., min_length=1, max_length=100)]
        heartbeat_interval: Optional[int] = Field(default=3600, ge=60, le=86400)
        status: Optional[ProductStatus] = Field(default=ProductStatus.ENABLED)
    
    # 创建产品请求
    class ProductCreate(ProductBase):
        pass
    
    # 更新产品请求
    class ProductUpdate(BaseModel):
        name: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
        heartbeat_interval: Optional[Annotated[int, Field(ge=60, le=86400)]] = None
        status: Optional[ProductStatus] = None
    
    # 产品响应
    class ProductResponse(ProductBase):
        id: int
        public_key: str
        created_at: datetime
        updated_at: Optional[datetime]
        
        class Config:
            from_attributes = True
except ImportError:
    # 兼容旧版本pydantic
    # 产品基础模型
    class ProductBase(BaseModel):
        product_code: str
        name: str
        heartbeat_interval: Optional[int] = 3600
        status: Optional[ProductStatus] = ProductStatus.ENABLED
        
        class Config:
            schema_extra = {
                "example": {
                    "product_code": "XRAY_GUI",
                    "name": "Xray GUI",
                    "heartbeat_interval": 3600,
                    "status": "enabled"
                }
            }
    
    # 创建产品请求
    class ProductCreate(ProductBase):
        pass
    
    # 更新产品请求
    class ProductUpdate(BaseModel):
        name: Optional[str] = None
        heartbeat_interval: Optional[int] = None
        status: Optional[ProductStatus] = None
        
        class Config:
            schema_extra = {
                "example": {
                    "name": "Updated Xray GUI",
                    "heartbeat_interval": 7200,
                    "status": "disabled"
                }
            }
    
    # 产品响应
    class ProductResponse(ProductBase):
        id: int
        public_key: str
        created_at: datetime
        updated_at: Optional[datetime]
        
        class Config:
            orm_mode = True
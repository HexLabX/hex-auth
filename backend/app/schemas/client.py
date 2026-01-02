from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.client import ClientType, ClientStatus

try:
    from typing_extensions import Annotated
    
    # 客户端实例基础模型
    class ClientBase(BaseModel):
        license_id: int
        product_code: Annotated[str, Field(..., min_length=3, max_length=50)]
        client_fp: Annotated[str, Field(..., min_length=10, max_length=100)]
        client_type: ClientType
        ip_address: Optional[Annotated[str, Field(max_length=50)]] = None
    
    # 客户端实例响应
    class ClientResponse(ClientBase):
        id: int
        last_heartbeat: Optional[datetime]
        status: ClientStatus
        created_at: datetime
        
        class Config:
            from_attributes = True
except ImportError:
    # 兼容旧版本pydantic
    # 客户端实例基础模型
    class ClientBase(BaseModel):
        license_id: int
        product_code: str
        client_fp: str
        client_type: ClientType
        ip_address: Optional[str] = None
        
        class Config:
            schema_extra = {
                "example": {
                    "license_id": 1,
                    "product_code": "XRAY_GUI",
                    "client_fp": "HASH1234567890",
                    "client_type": "gui",
                    "ip_address": "192.168.1.1"
                }
            }
    
    # 客户端实例响应
    class ClientResponse(ClientBase):
        id: int
        last_heartbeat: Optional[datetime]
        status: ClientStatus
        created_at: datetime
        
        class Config:
            orm_mode = True
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from typing_extensions import Annotated
    
    # 审计日志响应
    class AuditLogResponse(BaseModel):
        id: int
        admin_username: Annotated[str, Field(max_length=50)]
        action: Annotated[str, Field(max_length=50)]
        target_type: Annotated[str, Field(max_length=50)]
        target_id: Annotated[str, Field(max_length=50)]
        detail: Optional[Dict[str, Any]] = None
        created_at: datetime
        
        class Config:
            from_attributes = True
except ImportError:
    # 兼容旧版本pydantic
    # 审计日志响应
    class AuditLogResponse(BaseModel):
        id: int
        admin_username: str
        action: str
        target_type: str
        target_id: str
        detail: Optional[Dict[str, Any]] = None
        created_at: datetime
        
        class Config:
            orm_mode = True
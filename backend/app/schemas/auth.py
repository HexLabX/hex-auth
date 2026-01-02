from pydantic import BaseModel, EmailStr
from typing import Optional

# 登录请求
try:
    from typing_extensions import Annotated
    from pydantic import Field
    
    class LoginRequest(BaseModel):
        username: Annotated[str, Field(..., min_length=3, max_length=50)]
        password: Annotated[str, Field(..., min_length=6)]
        
    # 登录响应
    class LoginResponse(BaseModel):
        access_token: str
        token_type: str = "bearer"
except ImportError:
    # 兼容旧版本pydantic
    class LoginRequest(BaseModel):
        username: str
        password: str
        
        class Config:
            schema_extra = {
                "example": {
                    "username": "admin",
                    "password": "password123"
                }
            }
    
    # 登录响应
    class LoginResponse(BaseModel):
        access_token: str
        token_type: str = "bearer"
        
        class Config:
            schema_extra = {
                "example": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            }
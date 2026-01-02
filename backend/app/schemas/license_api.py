from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from typing_extensions import Annotated
    
    # 激活请求
    class ActivateRequest(BaseModel):
        license_key: Annotated[str, Field(..., min_length=10, max_length=50)]
        client_fp: Annotated[str, Field(..., min_length=10, max_length=100)]
        client_type: Annotated[str, Field(..., min_length=3, max_length=20)]
    
    # 激活响应
    class ActivateResponse(BaseModel):
        success: bool
        message: str
        token: Optional[Dict[str, Any]] = None
    
    # 心跳请求
    class HeartbeatRequest(BaseModel):
        token: Dict[str, Any]
    
    # 心跳响应
    class HeartbeatResponse(BaseModel):
        success: bool
        message: str
    
    # 状态请求
    class StatusRequest(BaseModel):
        token: Dict[str, Any]
    
    # 状态响应
    class StatusResponse(BaseModel):
        success: bool
        message: str
        status: Optional[str] = None
        expire_at: Optional[int] = None
except ImportError:
    # 兼容旧版本pydantic
    # 激活请求
    class ActivateRequest(BaseModel):
        license_key: str
        client_fp: str
        client_type: str
        
        class Config:
            schema_extra = {
                "example": {
                    "license_key": "XXXX-XXXX-XXXX-XXXX",
                    "client_fp": "HASH1234567890",
                    "client_type": "gui"
                }
            }
    
    # 激活响应
    class ActivateResponse(BaseModel):
        success: bool
        message: str
        token: Optional[Dict[str, Any]] = None
        
        class Config:
            schema_extra = {
                "example": {
                    "success": True,
                    "message": "Activation successful",
                    "token": {
                        "token": {
                            "iss": "hex-auth",
                            "product": "XRAY_GUI",
                            "license_key": "XXXX-XXXX-XXXX-XXXX",
                            "client_fp": "HASH1234567890",
                            "iat": 1730000000,
                            "exp": 1760000000
                        },
                        "signature": "base64-encoded-signature"
                    }
                }
            }
    
    # 心跳请求
    class HeartbeatRequest(BaseModel):
        token: Dict[str, Any]
        
        class Config:
            schema_extra = {
                "example": {
                    "token": {
                        "token": {
                            "iss": "hex-auth",
                            "product": "XRAY_GUI",
                            "license_key": "XXXX-XXXX-XXXX-XXXX",
                            "client_fp": "HASH1234567890",
                            "iat": 1730000000,
                            "exp": 1760000000
                        },
                        "signature": "base64-encoded-signature"
                    }
                }
            }
    
    # 心跳响应
    class HeartbeatResponse(BaseModel):
        success: bool
        message: str
        
        class Config:
            schema_extra = {
                "example": {
                    "success": True,
                    "message": "Heartbeat successful"
                }
            }
    
    # 状态请求
    class StatusRequest(BaseModel):
        token: Dict[str, Any]
        
        class Config:
            schema_extra = {
                "example": {
                    "token": {
                        "token": {
                            "iss": "hex-auth",
                            "product": "XRAY_GUI",
                            "license_key": "XXXX-XXXX-XXXX-XXXX",
                            "client_fp": "HASH1234567890",
                            "iat": 1730000000,
                            "exp": 1760000000
                        },
                        "signature": "base64-encoded-signature"
                    }
                }
            }
    
    # 状态响应
    class StatusResponse(BaseModel):
        success: bool
        message: str
        status: Optional[str] = None
        expire_at: Optional[int] = None
        
        class Config:
            schema_extra = {
                "example": {
                    "success": True,
                    "message": "License valid",
                    "status": "active",
                    "expire_at": 1760000000
                }
            }
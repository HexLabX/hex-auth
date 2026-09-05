from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str
    
    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 服务器配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_RELOAD: bool = True

    # CORS白名单，逗号分隔；生产建议设置为管理后台的实际访问地址
    CORS_ALLOW_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_allow_origins(self) -> list:
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
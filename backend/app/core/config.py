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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
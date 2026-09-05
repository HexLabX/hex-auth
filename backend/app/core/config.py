from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str

    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # RSA私钥主密钥（Fernet，用于加密存储各产品的RSA私钥）
    # 生成方式: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    RSA_MASTER_KEY: str

    # 登录限流：窗口期内按「用户名+IP」计的最大失败次数
    LOGIN_MAX_FAILURES: int = 5
    LOGIN_FAILURE_WINDOW_SECONDS: int = 900

    # 公开接口限流（按IP，固定窗口为1分钟）
    ACTIVATE_RATE_LIMIT_PER_MINUTE: int = 10
    HEARTBEAT_RATE_LIMIT_PER_MINUTE: int = 120

    # 心跳离线检测：每 CLIENT_OFFLINE_CHECK_SECONDS 秒扫描一次，
    # 超过 CLIENT_OFFLINE_MULTIPLIER 倍产品心跳间隔未上报的客户端标记为 ABNORMAL
    CLIENT_OFFLINE_CHECK_SECONDS: int = 60
    CLIENT_OFFLINE_MULTIPLIER: int = 3

    # 服务器配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_RELOAD: bool = True

    # CORS白名单，逗号分隔；生产建议设置为管理后台的实际访问地址
    CORS_ALLOW_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_allow_origins(self) -> list:
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]

    @field_validator("RSA_MASTER_KEY")
    @classmethod
    def validate_rsa_master_key(cls, v: str) -> str:
        from cryptography.fernet import Fernet
        try:
            Fernet(v.encode())
        except Exception:
            raise ValueError(
                "RSA_MASTER_KEY 不是有效的 Fernet 密钥。"
                '生成方式: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
            )
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

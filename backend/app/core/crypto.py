"""
RSA私钥静态加密。

私钥以 "enc:" 前缀 + Fernet 密文的形式存储在 products 表；
无前缀的历史明文私钥在读取时保持兼容，并在下次激活时自动升级为加密存储。
主密钥来自环境变量 RSA_MASTER_KEY，丢失后已加密的私钥无法恢复。
"""
from cryptography.fernet import Fernet, InvalidToken

_PREFIX = "enc:"


def is_encrypted_private_key(stored: str) -> bool:
    return stored.startswith(_PREFIX)


def encrypt_private_key(plaintext: str) -> str:
    return _PREFIX + Fernet(_get_key()).encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_private_key(stored: str) -> str:
    if not is_encrypted_private_key(stored):
        # 历史明文私钥，直接返回
        return stored
    try:
        return Fernet(_get_key()).decrypt(stored[len(_PREFIX):].encode("utf-8")).decode("utf-8")
    except InvalidToken as e:
        raise ValueError(
            "RSA私钥解密失败：RSA_MASTER_KEY 与该产品私钥加密时不匹配（主密钥错误或已被更换）"
        ) from e


def _get_key() -> bytes:
    from app.core.config import settings
    return settings.RSA_MASTER_KEY.encode("utf-8")

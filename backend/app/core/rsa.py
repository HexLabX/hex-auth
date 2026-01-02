from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64
import json
from typing import Tuple, Dict, Any

# 生成RSA密钥对
def generate_rsa_key_pair() -> Tuple[str, str]:
    key = RSA.generate(2048)
    private_key = key.export_key().decode("utf-8")
    public_key = key.publickey().export_key().decode("utf-8")
    return private_key, public_key

# 签名数据
def sign_data(data: Dict[str, Any], private_key: str) -> str:
    # 将数据转换为JSON字符串
    json_data = json.dumps(data, sort_keys=True)
    # 创建SHA-256哈希
    hash_obj = SHA256.new(json_data.encode("utf-8"))
    # 加载私钥
    rsa_key = RSA.import_key(private_key)
    # 创建签名器
    signer = PKCS1_v1_5.new(rsa_key)
    # 生成签名
    signature = signer.sign(hash_obj)
    # 对签名进行Base64编码
    return base64.b64encode(signature).decode("utf-8")

# 验证签名
def verify_signature(data: Dict[str, Any], signature: str, public_key: str) -> bool:
    try:
        # 将数据转换为JSON字符串
        json_data = json.dumps(data, sort_keys=True)
        # 创建SHA-256哈希
        hash_obj = SHA256.new(json_data.encode("utf-8"))
        # 加载公钥
        rsa_key = RSA.import_key(public_key)
        # 创建验证器
        verifier = PKCS1_v1_5.new(rsa_key)
        # 解码Base64签名
        decoded_signature = base64.b64decode(signature)
        # 验证签名
        return verifier.verify(hash_obj, decoded_signature)
    except Exception:
        return False

# 生成License Token
def generate_license_token(
    product: str,
    license_key: str,
    client_fp: str,
    expire_at: int,
    private_key: str
) -> Dict[str, Any]:
    # 创建Token数据
    token_data = {
        "iss": "hex-auth",
        "product": product,
        "license_key": license_key,
        "client_fp": client_fp,
        "iat": int(datetime.utcnow().timestamp()),
        "exp": expire_at
    }
    # 生成签名
    signature = sign_data(token_data, private_key)
    # 返回带有签名的Token
    return {
        "token": token_data,
        "signature": signature
    }

# 验证License Token
def verify_license_token(token: Dict[str, Any], public_key: str) -> bool:
    try:
        # 从Token中提取数据和签名
        token_data = token["token"]
        signature = token["signature"]
        # 验证签名
        if not verify_signature(token_data, signature, public_key):
            return False
        # 验证过期时间
        current_time = int(datetime.utcnow().timestamp())
        if token_data["exp"] < current_time:
            return False
        return True
    except Exception:
        return False
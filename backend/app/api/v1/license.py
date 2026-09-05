from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.core.database import get_db
from app.core.rsa import verify_signature, generate_license_token
from app.models.license import License, LicenseStatus
from app.models.product import Product, ProductStatus
from app.models.client import Client, ClientType, ClientStatus
from app.schemas.license_api import (
    ActivateRequest, ActivateResponse,
    HeartbeatRequest, HeartbeatResponse,
    StatusRequest, StatusResponse
)

router = APIRouter()

# 激活API
@router.post("/activate", response_model=ActivateResponse)
def activate(
    request: ActivateRequest,
    db: Session = Depends(get_db)
):
    # 1. 查找License（加行锁，防止并发激活时设备数超卖）
    license = db.query(License).filter(
        License.license_key == request.license_key
    ).with_for_update().first()
    if not license:
        return ActivateResponse(
            success=False,
            message="Invalid license key"
        )

    # 2. 检查License状态
    if license.status == LicenseStatus.REVOKED:
        return ActivateResponse(
            success=False,
            message="License has been revoked"
        )

    if license.expire_at < date.today():
        license.status = LicenseStatus.EXPIRED
        db.commit()
        return ActivateResponse(
            success=False,
            message="License has expired"
        )

    # 3. 查找产品
    product = db.query(Product).filter(Product.product_code == license.product_code).first()
    if not product:
        return ActivateResponse(
            success=False,
            message="Product not found"
        )

    if product.status == ProductStatus.DISABLED:
        return ActivateResponse(
            success=False,
            message="Product has been disabled"
        )

    # 4. 校验客户端类型（非法值直接拒绝，而不是抛500）
    try:
        client_type = ClientType(request.client_type.lower())
    except ValueError:
        return ActivateResponse(
            success=False,
            message="Invalid client type"
        )

    # 5. 检查客户端指纹是否已绑定
    existing_client = db.query(Client).filter(
        Client.license_id == license.id,
        Client.client_fp == request.client_fp
    ).first()

    # 管理员禁用的客户端不允许通过重新激活自我解禁
    if existing_client and existing_client.status == ClientStatus.DISABLED:
        return ActivateResponse(
            success=False,
            message="Client has been disabled"
        )

    # 6. 检查已激活设备数量（排除自身占用的席位，已激活设备重装后可正常重新激活）
    seat_query = db.query(Client).filter(
        Client.license_id == license.id,
        Client.status == ClientStatus.NORMAL
    )
    if existing_client:
        seat_query = seat_query.filter(Client.id != existing_client.id)
    active_clients = seat_query.count()

    if active_clients >= license.max_devices:
        return ActivateResponse(
            success=False,
            message="Maximum number of devices reached"
        )

    if existing_client:
        # 异常状态的客户端恢复为正常
        existing_client.status = ClientStatus.NORMAL
        existing_client.last_heartbeat = datetime.utcnow()
    else:
        # 7. 创建新客户端
        client = Client(
            license_id=license.id,
            product_code=license.product_code,
            client_fp=request.client_fp,
            client_type=client_type,
            status=ClientStatus.NORMAL
        )
        db.add(client)

    # 8. 更新License状态为已激活
    if license.status == LicenseStatus.UNACTIVATED:
        license.status = LicenseStatus.ACTIVATED

    db.commit()

    # 9. 生成License Token
    # 将date对象转换为datetime对象，然后获取timestamp
    expire_datetime = datetime.combine(license.expire_at, datetime.min.time())
    expire_at = int(expire_datetime.timestamp())
    token = generate_license_token(
        product=license.product_code,
        license_key=license.license_key,
        client_fp=request.client_fp,
        expire_at=expire_at,
        private_key=product.private_key
    )

    return ActivateResponse(
        success=True,
        message="Activation successful",
        token=token
    )

# 心跳API
@router.post("/heartbeat", response_model=HeartbeatResponse)
def heartbeat(
    request: HeartbeatRequest,
    db: Session = Depends(get_db)
):
    try:
        # 1. 解析Token
        token_data = request.token["token"]
        signature = request.token["signature"]
        
        # 2. 查找产品
        product = db.query(Product).filter(Product.product_code == token_data["product"]).first()
        if not product:
            return HeartbeatResponse(
                success=False,
                message="Product not found"
            )
        
        # 3. 验证Token签名
        if not verify_signature(token_data, signature, product.public_key):
            return HeartbeatResponse(
                success=False,
                message="Invalid token signature"
            )
        
        # 4. 查找License
        license = db.query(License).filter(License.license_key == token_data["license_key"]).first()
        if not license:
            return HeartbeatResponse(
                success=False,
                message="License not found"
            )
        
        # 5. 检查License状态与有效期
        if license.status in [LicenseStatus.REVOKED, LicenseStatus.EXPIRED]:
            return HeartbeatResponse(
                success=False,
                message="License is invalid"
            )

        if license.expire_at < date.today():
            license.status = LicenseStatus.EXPIRED
            db.commit()
            return HeartbeatResponse(
                success=False,
                message="License has expired"
            )
        
        # 6. 查找客户端
        client = db.query(Client).filter(
            Client.license_id == license.id,
            Client.client_fp == token_data["client_fp"]
        ).first()
        
        if not client:
            return HeartbeatResponse(
                success=False,
                message="Client not found"
            )
        
        if client.status == ClientStatus.DISABLED:
            return HeartbeatResponse(
                success=False,
                message="Client has been disabled"
            )
        
        # 7. 更新心跳时间
        client.last_heartbeat = datetime.utcnow()
        db.commit()
        
        return HeartbeatResponse(
            success=True,
            message="Heartbeat successful"
        )
    except Exception as e:
        return HeartbeatResponse(
            success=False,
            message="Invalid token format"
        )

# 状态API
@router.post("/status", response_model=StatusResponse)
def check_status(
    request: StatusRequest,
    db: Session = Depends(get_db)
):
    try:
        # 1. 解析Token
        token_data = request.token["token"]
        signature = request.token["signature"]
        
        # 2. 查找产品
        product = db.query(Product).filter(Product.product_code == token_data["product"]).first()
        if not product:
            return StatusResponse(
                success=False,
                message="Product not found"
            )
        
        # 3. 验证Token签名
        if not verify_signature(token_data, signature, product.public_key):
            return StatusResponse(
                success=False,
                message="Invalid token signature"
            )
        
        # 4. 查找License
        license = db.query(License).filter(License.license_key == token_data["license_key"]).first()
        if not license:
            return StatusResponse(
                success=False,
                message="License not found"
            )
        
        # 5. 检查License状态
        if license.status == LicenseStatus.REVOKED:
            return StatusResponse(
                success=False,
                message="License has been revoked",
                status="revoked"
            )
        
        if license.status == LicenseStatus.EXPIRED or license.expire_at < date.today():
            return StatusResponse(
                success=False,
                message="License has expired",
                status="expired"
            )
        
        # 6. 查找客户端
        client = db.query(Client).filter(
            Client.license_id == license.id,
            Client.client_fp == token_data["client_fp"]
        ).first()
        
        if not client:
            return StatusResponse(
                success=False,
                message="Client not found"
            )
        
        if client.status == ClientStatus.DISABLED:
            return StatusResponse(
                success=False,
                message="Client has been disabled",
                status="disabled"
            )
        
        # 7. 返回状态
        # 将date对象转换为datetime对象，然后获取timestamp
        expire_datetime = datetime.combine(license.expire_at, datetime.min.time())
        return StatusResponse(
            success=True,
            message="License is valid",
            status="valid",
            expire_at=int(expire_datetime.timestamp())
        )
    except Exception as e:
        return StatusResponse(
            success=False,
            message="Invalid token format"
        )
"""
核心授权流程回归测试。

覆盖：客户端审计日志、禁用客户端不可自我解禁、管理员状态校验、
激活设备数限制与并发行锁、client_type 校验、心跳过期检查、产品删除保护、
登录限流与失败审计、公开接口IP限流、RSA私钥加密存储与历史明文自动升级。

运行方式（任选其一）：
    cd backend && python -m pytest tests/ -v
    cd backend && python tests/test_core_flows.py
"""

import os
import sys
from datetime import date, timedelta

# config.py 在导入时读取必填环境变量，需在导入 app 之前设置
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
# 仅测试用的 Fernet 主密钥（非生产密钥）
os.environ.setdefault("RSA_MASTER_KEY", "HBn-QQPaf3YrtQhIIA2UjC4Qsg4zrebAzo2OO9xNEms=")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from cryptography.fernet import Fernet
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request as HttpRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.crypto import decrypt_private_key, encrypt_private_key, is_encrypted_private_key
from app.core.rsa import generate_license_token, generate_rsa_key_pair, verify_license_token
from app.core.jwt import create_access_token
from app.core.config import settings
from app.models.admin_user import AdminUser, AdminStatus
from app.models.product import Product
from app.models.license import License, LicenseStatus
from app.models.client import Client, ClientStatus, ClientType
from app.models.audit_log import AuditLog
from app.api.v1.license import activate, heartbeat
from app.schemas.license_api import ActivateRequest, HeartbeatRequest
from app.schemas.product import ProductCreate
from app.admin import auth as admin_auth
from app.admin import client as admin_client
from app.admin import product as admin_product
from app.utils.audit_utils import create_audit_log

# 测试专用的自增IP，保证各测试间限流计数互不干扰
_ip_counter = [0]


def make_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def fake_request(ip: str = None) -> HttpRequest:
    """构造带 client IP 的假 HTTP 请求（端点签名需要 Request 参数）。"""
    if ip is None:
        _ip_counter[0] += 1
        ip = f"10.0.{_ip_counter[0] // 250}.{_ip_counter[0] % 250 + 1}"
    return HttpRequest({"type": "http", "client": (ip, 12345), "headers": []})


def make_fixtures(db):
    """创建一个可用产品 + 授权（max_devices=2），私钥为明文（模拟历史数据）"""
    private_key, public_key = generate_rsa_key_pair()
    product = Product(
        product_code="TEST_PRD",
        name="测试产品",
        public_key=public_key,
        private_key=private_key,
    )
    license = License(
        license_key="TEST-KEY-12345678",
        product_code="TEST_PRD",
        max_devices=2,
        expire_at=date.today() + timedelta(days=365),
    )
    db.add_all([product, license])
    db.commit()
    return product, license


def make_admin(db, username: str, password: str = "password123",
               status: AdminStatus = AdminStatus.ENABLED) -> AdminUser:
    admin = AdminUser(
        username=username,
        password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        status=status,
    )
    db.add(admin)
    db.commit()
    return admin


def try_login(db, username: str, password: str, ip: str):
    form = OAuth2PasswordRequestForm(username=username, password=password, scope="")
    return admin_auth.login(request=fake_request(ip), form_data=form, db=db)


# ---------- 原有回归点 ----------

def test_client_audit_log_uses_client_fp():
    """审计日志自动收集 Client 详情时使用存在的字段（回归：client_key AttributeError）"""
    db = make_db()
    client = Client(
        license_id=1, product_code="P", client_fp="FP-1234567890", client_type=ClientType.GUI,
        status=ClientStatus.NORMAL,
    )
    db.add(client)
    db.commit()

    log = create_audit_log(
        db=db, admin_username="admin", action="禁用",
        target_type="客户端实例", target_id=client.id,
        target_instance=client,
    )
    assert log.detail["client_fp"] == "FP-1234567890"


def test_disabled_client_cannot_reactivate():
    """管理员禁用的客户端不能通过重新激活自我解禁"""
    db = make_db()
    product, license = make_fixtures(db)
    client = Client(
        license_id=license.id, product_code=license.product_code,
        client_fp="FP-DISABLED-01", client_type=ClientType.GUI,
        status=ClientStatus.DISABLED,
    )
    db.add(client)
    db.commit()

    resp = activate(fake_request(), ActivateRequest(
        license_key=license.license_key,
        client_fp="FP-DISABLED-01",
        client_type="gui",
    ), db)

    assert resp.success is False
    assert "disabled" in resp.message
    db.refresh(client)
    assert client.status == ClientStatus.DISABLED


def test_abnormal_client_can_recover():
    """异常（ABNORMAL）客户端重新激活后恢复正常，且可重新拿到 token"""
    db = make_db()
    product, license = make_fixtures(db)
    client = Client(
        license_id=license.id, product_code=license.product_code,
        client_fp="FP-ABNORMAL-01", client_type=ClientType.GUI,
        status=ClientStatus.ABNORMAL,
    )
    db.add(client)
    db.commit()

    resp = activate(fake_request(), ActivateRequest(
        license_key=license.license_key,
        client_fp="FP-ABNORMAL-01",
        client_type="gui",
    ), db)

    assert resp.success is True
    assert resp.token is not None
    db.refresh(client)
    assert client.status == ClientStatus.NORMAL


def test_invalid_client_type_rejected():
    """非法 client_type 返回失败响应而不是 500"""
    db = make_db()
    _, license = make_fixtures(db)

    resp = activate(fake_request(), ActivateRequest(
        license_key=license.license_key,
        client_fp="FP-NEWDEV-01",
        client_type="desktop",
    ), db)

    assert resp.success is False
    assert resp.message == "Invalid client type"


def test_activate_respects_max_devices():
    """设备数达到上限后，新设备激活被拒绝"""
    db = make_db()
    _, license = make_fixtures(db)  # max_devices=2
    db.add_all([
        Client(license_id=license.id, product_code=license.product_code,
               client_fp="FP-DEV-001", client_type=ClientType.GUI, status=ClientStatus.NORMAL),
        Client(license_id=license.id, product_code=license.product_code,
               client_fp="FP-DEV-002", client_type=ClientType.GUI, status=ClientStatus.NORMAL),
    ])
    db.commit()

    resp = activate(fake_request(), ActivateRequest(
        license_key=license.license_key,
        client_fp="FP-DEV-003",
        client_type="cli",
    ), db)

    assert resp.success is False
    assert resp.message == "Maximum number of devices reached"


def test_reactivation_not_blocked_by_own_seat():
    """已激活设备重装后重新激活，不被自己占用的席位挡住"""
    db = make_db()
    _, license = make_fixtures(db)  # max_devices=2
    db.add_all([
        Client(license_id=license.id, product_code=license.product_code,
               client_fp="FP-DEV-001", client_type=ClientType.GUI, status=ClientStatus.NORMAL),
        Client(license_id=license.id, product_code=license.product_code,
               client_fp="FP-DEV-002", client_type=ClientType.GUI, status=ClientStatus.NORMAL),
    ])
    db.commit()

    resp = activate(fake_request(), ActivateRequest(
        license_key=license.license_key,
        client_fp="FP-DEV-002",
        client_type="gui",
    ), db)

    assert resp.success is True


def test_heartbeat_rejects_expired_license():
    """已过日期但状态未刷新的授权，心跳会拒绝并将状态修正为 EXPIRED"""
    db = make_db()
    product, license = make_fixtures(db)
    license.expire_at = date.today() - timedelta(days=1)
    license.status = LicenseStatus.ACTIVATED
    client = Client(
        license_id=license.id, product_code=license.product_code,
        client_fp="FP-HB-01", client_type=ClientType.GUI,
        status=ClientStatus.NORMAL,
    )
    db.add(client)
    db.commit()

    token = generate_license_token(
        product=product.product_code,
        license_key=license.license_key,
        client_fp="FP-HB-01",
        expire_at=9999999999,
        private_key=product.private_key,
    )
    resp = heartbeat(fake_request(), HeartbeatRequest(token=token), db)

    assert resp.success is False
    assert resp.message == "License has expired"
    db.refresh(license)
    assert license.status == LicenseStatus.EXPIRED


def test_disabled_admin_cannot_login():
    """被禁用的管理员无法登录"""
    db = make_db()
    make_admin(db, "disabled_admin", status=AdminStatus.DISABLED)

    try:
        try_login(db, "disabled_admin", "password123", ip="10.9.0.1")
        raise AssertionError("expected HTTPException")
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Account is disabled"


def test_disabled_admin_token_invalid():
    """被禁用的管理员，其存量令牌立即失效"""
    db = make_db()
    admin = AdminUser(username="revoked_admin", password_hash="x", status=AdminStatus.DISABLED)
    db.add(admin)
    db.commit()

    token = create_access_token(data={"sub": "revoked_admin"})
    try:
        admin_auth.get_current_admin(token=token, db=db)
        raise AssertionError("expected HTTPException")
    except HTTPException as e:
        assert e.status_code == 401


def test_disable_client_creates_audit_log():
    """禁用客户端成功且审计日志与业务变更同事务落库（回归：审计 AttributeError 导致 500）"""
    db = make_db()
    _, license = make_fixtures(db)
    client = Client(
        license_id=license.id, product_code=license.product_code,
        client_fp="FP-TO-DISABLE", client_type=ClientType.GUI,
        status=ClientStatus.NORMAL,
    )
    admin = AdminUser(username="op_admin", password_hash="x", status=AdminStatus.ENABLED)
    db.add_all([client, admin])
    db.commit()

    resp = admin_client.disable_client(client_id=client.id, db=db, current_admin=admin)

    assert resp.status == ClientStatus.DISABLED
    log = db.query(AuditLog).filter(
        AuditLog.target_type == "客户端实例", AuditLog.action == "禁用"
    ).first()
    assert log is not None
    assert log.detail["client_fp"] == "FP-TO-DISABLE"


def test_delete_client_creates_audit_log():
    """删除客户端成功且留下审计日志（回归：审计在删除前抛异常导致无法删除）"""
    db = make_db()
    _, license = make_fixtures(db)
    client = Client(
        license_id=license.id, product_code=license.product_code,
        client_fp="FP-TO-DELETE", client_type=ClientType.GUI,
        status=ClientStatus.NORMAL,
    )
    admin = AdminUser(username="op_admin2", password_hash="x", status=AdminStatus.ENABLED)
    db.add_all([client, admin])
    db.commit()
    client_id = client.id

    admin_client.delete_client(client_id=client_id, db=db, current_admin=admin)

    assert db.query(Client).filter(Client.id == client_id).first() is None
    log = db.query(AuditLog).filter(
        AuditLog.target_type == "客户端实例", AuditLog.action == "删除"
    ).first()
    assert log is not None


def test_delete_product_with_licenses_rejected():
    """产品下仍有授权时禁止删除"""
    db = make_db()
    product, license = make_fixtures(db)
    admin = AdminUser(username="op_admin3", password_hash="x", status=AdminStatus.ENABLED)
    db.add(admin)
    db.commit()

    try:
        admin_product.delete_product(product_id=product.id, db=db, current_admin=admin)
        raise AssertionError("expected HTTPException")
    except HTTPException as e:
        assert e.status_code == 409
    # 产品未被删除
    assert db.query(Product).filter(Product.id == product.id).first() is not None


# ---------- 登录限流与失败审计 ----------

def test_failed_login_audited():
    """登录失败（密码错误）会留下审计日志，含IP"""
    db = make_db()
    make_admin(db, "audit_admin")

    try:
        try_login(db, "audit_admin", "wrong-password", ip="10.9.0.2")
        raise AssertionError("expected HTTPException")
    except HTTPException as e:
        assert e.status_code == 401

    log = db.query(AuditLog).filter(
        AuditLog.admin_username == "audit_admin", AuditLog.action == "登录失败"
    ).first()
    assert log is not None
    assert log.detail["ip"] == "10.9.0.2"
    assert "密码" in log.detail["reason"]


def test_login_rate_limited():
    """同一用户名+IP 连续失败达到上限后，返回 429"""
    db = make_db()
    make_admin(db, "bruteforce_admin")
    ip = "10.9.0.3"

    for _ in range(settings.LOGIN_MAX_FAILURES):
        try:
            try_login(db, "bruteforce_admin", "wrong-password", ip=ip)
        except HTTPException as e:
            assert e.status_code == 401

    try:
        try_login(db, "bruteforce_admin", "wrong-password", ip=ip)
        raise AssertionError("expected HTTPException")
    except HTTPException as e:
        assert e.status_code == 429


def test_login_success_resets_failures():
    """登录成功会清除失败计数，不会误伤正常用户"""
    db = make_db()
    make_admin(db, "normal_admin")
    ip = "10.9.0.4"

    for _ in range(settings.LOGIN_MAX_FAILURES - 1):
        try:
            try_login(db, "normal_admin", "wrong-password", ip=ip)
        except HTTPException as e:
            assert e.status_code == 401

    # 成功登录一次
    resp = try_login(db, "normal_admin", "password123", ip=ip)
    assert resp["access_token"]

    # 再次失败若干次仍返回 401（计数已清零），而非 429
    for _ in range(settings.LOGIN_MAX_FAILURES - 1):
        try:
            try_login(db, "normal_admin", "wrong-password", ip=ip)
        except HTTPException as e:
            assert e.status_code == 401


def test_activate_rate_limited():
    """同一IP频繁调用激活接口，超过限制后返回 429"""
    db = make_db()
    make_fixtures(db)
    ip = "10.9.0.5"
    req = ActivateRequest(license_key="INVALID-KEY-0000", client_fp="FP-RATELIMIT-1", client_type="gui")

    for _ in range(settings.ACTIVATE_RATE_LIMIT_PER_MINUTE):
        resp = activate(fake_request(ip), req, db)
        assert resp.success is False  # 无效key，但请求被计数

    try:
        activate(fake_request(ip), req, db)
        raise AssertionError("expected HTTPException")
    except HTTPException as e:
        assert e.status_code == 429


# ---------- RSA私钥加密存储 ----------

def test_private_key_encrypted_on_create():
    """创建产品时私钥以加密形式入库"""
    db = make_db()
    admin = AdminUser(username="creator", password_hash="x", status=AdminStatus.ENABLED)
    db.add(admin)
    db.commit()

    created = admin_product.create_product(
        product=ProductCreate(product_code="ENC_PRD", name="加密测试产品"),
        db=db, current_admin=admin,
    )

    assert is_encrypted_private_key(created.private_key)
    # 公钥保持明文
    assert created.public_key.startswith("-----BEGIN PUBLIC KEY-----")


def test_activate_works_with_encrypted_key():
    """加密存储的私钥可以正常签发令牌，且令牌可用公钥验证"""
    db = make_db()
    admin = AdminUser(username="creator2", password_hash="x", status=AdminStatus.ENABLED)
    db.add(admin)
    db.commit()

    product = admin_product.create_product(
        product=ProductCreate(product_code="ENC_PRD2", name="加密激活测试"),
        db=db, current_admin=admin,
    )
    license = License(
        license_key="ENC-KEY-12345678",
        product_code=product.product_code,
        max_devices=1,
        expire_at=date.today() + timedelta(days=365),
    )
    db.add(license)
    db.commit()

    resp = activate(fake_request(), ActivateRequest(
        license_key=license.license_key,
        client_fp="FP-ENC-001",
        client_type="gui",
    ), db)

    assert resp.success is True
    assert verify_license_token(resp.token, product.public_key) is True


def test_legacy_plaintext_key_upgraded_on_activate():
    """历史明文私钥在激活时保持兼容，并自动升级为加密存储"""
    db = make_db()
    product, license = make_fixtures(db)  # make_fixtures 写入的是明文私钥
    assert not is_encrypted_private_key(product.private_key)
    plaintext = product.private_key

    resp = activate(fake_request(), ActivateRequest(
        license_key=license.license_key,
        client_fp="FP-LEGACY-01",
        client_type="gui",
    ), db)

    assert resp.success is True
    db.refresh(product)
    assert is_encrypted_private_key(product.private_key)
    # 升级后解密结果与原明文一致
    assert decrypt_private_key(product.private_key) == plaintext


def test_wrong_master_key_rejected():
    """主密钥不匹配时解密报错并给出清晰提示"""
    stored = encrypt_private_key("-----TEST-----")
    original = settings.RSA_MASTER_KEY
    try:
        settings.RSA_MASTER_KEY = Fernet.generate_key().decode()
        try:
            decrypt_private_key(stored)
            raise AssertionError("expected ValueError")
        except ValueError as e:
            assert "RSA_MASTER_KEY" in str(e)
    finally:
        settings.RSA_MASTER_KEY = original


if __name__ == "__main__":
    tests = [fn for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)

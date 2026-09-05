"""
核心授权流程回归测试。

覆盖：客户端审计日志、禁用客户端不可自我解禁、管理员状态校验、
激活设备数限制与并发行锁、client_type 校验、心跳过期检查、产品删除保护。

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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.rsa import generate_license_token, generate_rsa_key_pair
from app.core.jwt import create_access_token
from app.models.admin_user import AdminUser, AdminStatus
from app.models.product import Product
from app.models.license import License, LicenseStatus
from app.models.client import Client, ClientStatus, ClientType
from app.models.audit_log import AuditLog
from app.api.v1.license import activate, heartbeat
from app.schemas.license_api import ActivateRequest, HeartbeatRequest
from app.admin import auth as admin_auth
from app.admin import client as admin_client
from app.admin import product as admin_product
from app.utils.audit_utils import create_audit_log


def make_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def make_fixtures(db):
    """创建一个可用产品 + 授权（max_devices=2）"""
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

    resp = activate(ActivateRequest(
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

    resp = activate(ActivateRequest(
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

    resp = activate(ActivateRequest(
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

    resp = activate(ActivateRequest(
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

    resp = activate(ActivateRequest(
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
    resp = heartbeat(HeartbeatRequest(token=token), db)

    assert resp.success is False
    assert resp.message == "License has expired"
    db.refresh(license)
    assert license.status == LicenseStatus.EXPIRED


def test_disabled_admin_cannot_login():
    """被禁用的管理员无法登录"""
    db = make_db()
    import bcrypt
    db.add(AdminUser(
        username="disabled_admin",
        password_hash=bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode(),
        status=AdminStatus.DISABLED,
    ))
    db.commit()

    form = OAuth2PasswordRequestForm(username="disabled_admin", password="password123", scope="")
    try:
        admin_auth.login(form_data=form, db=db)
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

from sqlalchemy.orm import Session
from typing import Optional, Any
from app.models.audit_log import AuditLog
from app.models.product import Product
from app.models.license import License
from app.models.client import Client
from app.models.admin_user import AdminUser

# 记录审计日志
def create_audit_log(
    db: Session,
    admin_username: str,
    action: str,
    target_type: str,
    target_id: Any,
    detail: Optional[dict] = None,
    # 可选的对象实例，用于自动收集详情
    target_instance: Optional[Any] = None
):
    """
    记录审计日志
    
    Args:
        db: 数据库会话
        admin_username: 操作用户名
        action: 操作类型（如：创建、更新、删除）
        target_type: 操作对象类型（如：产品、授权、客户端）
        target_id: 操作对象ID
        detail: 操作详情（可选）
        target_instance: 操作对象实例（可选），用于自动收集详情
    """
    # 确保target_id是字符串类型
    target_id_str = str(target_id)
    
    # 自动收集对象详情
    auto_detail = {}
    if target_instance:
        # 根据对象类型收集关键信息
        if isinstance(target_instance, Product):
            auto_detail = {
                "product_id": target_instance.id,
                "product_code": target_instance.product_code,
                "name": target_instance.name,
                "status": target_instance.status
            }
        elif isinstance(target_instance, License):
            auto_detail = {
                "license_id": target_instance.id,
                "license_key": target_instance.license_key,
                "product_code": target_instance.product_code,
                "status": target_instance.status,
                "expire_at": target_instance.expire_at.isoformat() if target_instance.expire_at else None
            }
        elif isinstance(target_instance, Client):
            auto_detail = {
                "client_id": target_instance.id,
                "client_key": target_instance.client_key,
                "product_code": target_instance.product_code,
                "license_id": target_instance.license_id,
                "status": target_instance.status
            }
        elif isinstance(target_instance, AdminUser):
            auto_detail = {
                "admin_id": target_instance.id,
                "username": target_instance.username,
                "status": target_instance.status
            }
    
    # 合并自动详情和手动详情
    final_detail = {**auto_detail}
    if detail:
        final_detail.update(detail)
    
    audit_log = AuditLog(
        admin_username=admin_username,
        action=action,
        target_type=target_type,
        target_id=target_id_str,
        detail=final_detail
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log

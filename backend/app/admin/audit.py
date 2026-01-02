from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse
from app.admin.auth import get_current_admin

router = APIRouter()

# 查询审计日志
@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    admin_username: str = None,
    action: str = None,
    target_type: str = None,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    query = db.query(AuditLog)
    
    # 按操作用户名过滤
    if admin_username:
        query = query.filter(AuditLog.admin_username == admin_username)
    
    # 按操作类型过滤
    if action:
        query = query.filter(AuditLog.action == action)
    
    # 按操作对象类型过滤
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
    
    # 按时间倒序排序
    query = query.order_by(AuditLog.created_at.desc())
    
    logs = query.offset(skip).limit(limit).all()
    return logs

# 查询单个审计日志
@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    return log

# 清空审计日志
@router.delete("/clear")
def clear_audit_logs(
    log_ids: list[int] = None,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    清空审计日志
    
    Args:
        log_ids: 可选，要删除的日志ID列表。如果为None，则删除所有日志
    """
    if log_ids:
        # 删除指定ID的日志
        deleted_count = db.query(AuditLog).filter(AuditLog.id.in_(log_ids)).delete(synchronize_session=False)
    else:
        # 删除所有日志
        deleted_count = db.query(AuditLog).delete(synchronize_session=False)
    
    db.commit()
    
    # 记录清空日志的操作
    from app.utils.audit_utils import create_audit_log
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="清空",
        target_type="审计日志",
        target_id="multiple",
        detail={
            "deleted_count": deleted_count,
            "log_ids": log_ids
        }
    )
    
    return {
        "message": "审计日志清空成功",
        "deleted_count": deleted_count
    }
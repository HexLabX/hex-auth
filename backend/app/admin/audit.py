from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse
from app.admin.auth import get_current_admin

router = APIRouter()

# 清空请求的模型
class ClearAuditLogsRequest(BaseModel):
    log_ids: Optional[List[int]] = None

# 查询审计日志
@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
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

# 清空审计日志（POST方法 - 用于清空选中的日志）
# 注意：必须在 /{log_id} 路由之前定义
@router.post("/clear")
def clear_audit_logs(
    request: ClearAuditLogsRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    清空审计日志

    Args:
        request: 包含log_ids的请求体，如果log_ids为None或空列表，则清空所有日志
    """
    log_ids = request.log_ids

    if log_ids and len(log_ids) > 0:
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

# 清空所有审计日志（POST方法 - 专门用于清空所有）
# 注意：必须在 /{log_id} 路由之前定义
@router.post("/clear-all")
def clear_all_audit_logs(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    清空所有审计日志
    """
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
        target_id="all",
        detail={
            "deleted_count": deleted_count
        }
    )

    return {
        "message": "所有审计日志清空成功",
        "deleted_count": deleted_count
    }

# 查询单个审计日志
# 注意：必须放在具体路由之后，避免拦截 /clear 和 /clear-all
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
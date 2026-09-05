from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timezone
from typing import List
from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.product import Product
from app.models.license import License
from app.models.client import Client, ClientStatus
from app.models.audit_log import AuditLog
from app.schemas.dashboard import DashboardResponse, DashboardStatsResponse
from app.admin.auth import get_current_admin

router = APIRouter()

# 按操作对象类型选择图标（target_type存储为中文）
def _activity_icon(target_type: str) -> str:
    lowered = target_type.lower()
    if "授权" in target_type or "license" in lowered:
        return "🔑"
    if "产品" in target_type or "product" in lowered:
        return "📦"
    if "客户端" in target_type or "client" in lowered:
        return "💻"
    return "📋"

# 获取仪表盘数据
@router.get("/", response_model=DashboardResponse)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    # 获取当前日期（UTC）
    today = datetime.now(timezone.utc).date()
    
    # 计算产品数量
    product_count = db.query(func.count(Product.id)).scalar() or 0
    
    # 计算授权数量
    license_count = db.query(func.count(License.id)).scalar() or 0
    
    # 计算活跃实例数量
    active_client_count = db.query(func.count(Client.id)).filter(
        Client.status == ClientStatus.NORMAL
    ).scalar() or 0

    # 计算今日激活数量（按客户端激活记录统计）
    today_activations = db.query(func.count(Client.id)).filter(
        func.date(Client.created_at) == today
    ).scalar() or 0

    # 获取近期活动（最近10条）
    recent_activities = db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).limit(10).all()

    # 格式化近期活动
    formatted_activities = []
    for activity in recent_activities:
        formatted_activities.append({
            "id": activity.id,
            "title": f"{activity.action}了{activity.target_type}",
            "icon": _activity_icon(activity.target_type),
            "time": activity.created_at
        })

    # 服务健康状态检查（能响应即API/服务正常，真实探测数据库连通性）
    try:
        db.execute(text("SELECT 1"))
        health_status = {
            "api": True,
            "database": True,
            "service": True
        }
    except Exception:
        health_status = {
            "api": True,
            "database": False,
            "service": True
        }
    
    # 构建响应
    return {
        "stats": {
            "productCount": product_count,
            "licenseCount": license_count,
            "activeClientCount": active_client_count,
            "todayActivations": today_activations
        },
        "healthStatus": health_status,
        "recentActivities": formatted_activities
    }

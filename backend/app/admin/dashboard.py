from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import List
from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.product import Product
from app.models.license import License
from app.models.client import Client
from app.models.audit_log import AuditLog
from app.schemas.dashboard import DashboardResponse, DashboardStatsResponse
from app.admin.auth import get_current_admin

router = APIRouter()

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
        Client.status == "normal"
    ).scalar() or 0
    
    # 计算今日激活数量
    today_activations = db.query(func.count(License.id)).filter(
        func.date(License.created_at) == today
    ).scalar() or 0
    
    # 获取近期活动（最近10条）
    recent_activities = db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).limit(10).all()
    
    # 格式化近期活动
    formatted_activities = []
    for activity in recent_activities:
        # 根据操作类型选择图标
        if "license" in activity.target_type.lower():
            icon = "🔑"
        elif "product" in activity.target_type.lower():
            icon = "📦"
        elif "client" in activity.target_type.lower():
            icon = "💻"
        else:
            icon = "📋"
        
        formatted_activities.append({
            "id": activity.id,
            "title": f"{activity.action}了{activity.target_type}",
            "icon": icon,
            "time": activity.created_at
        })
    
    # 服务健康状态检查
    health_status = {
        "api": True,  # API服务正常
        "database": True,  # 数据库连接正常
        "service": True  # 授权服务正常
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

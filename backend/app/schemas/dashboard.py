from pydantic import BaseModel
from datetime import datetime

# 仪表盘统计数据响应模型
class DashboardStatsResponse(BaseModel):
    productCount: int
    licenseCount: int
    activeClientCount: int
    todayActivations: int

# 近期活动响应模型
class RecentActivityResponse(BaseModel):
    id: int
    title: str
    icon: str
    time: datetime

# 仪表盘健康状态响应模型
class HealthStatusResponse(BaseModel):
    api: bool
    database: bool
    service: bool

# 仪表盘完整响应模型
class DashboardResponse(BaseModel):
    stats: DashboardStatsResponse
    healthStatus: HealthStatusResponse
    recentActivities: list[RecentActivityResponse]

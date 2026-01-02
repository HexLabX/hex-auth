from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="hex-auth 授权中心",
    description="统一在线授权中心，为多形态程序提供在线激活、心跳校验、授权吊销与后台管理能力",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "hex-auth 授权中心 API"}

# 导入路由
from app.admin.auth import router as auth_router
from app.admin.product import router as product_router
from app.admin.license import router as license_router
from app.admin.client import router as client_router
from app.admin.audit import router as audit_router
from app.admin.dashboard import router as dashboard_router
from app.api.v1.license import router as license_api_router

# 注册路由
app.include_router(auth_router, prefix="/admin/auth", tags=["admin-auth"])
app.include_router(dashboard_router, prefix="/admin/dashboard", tags=["admin-dashboard"])
app.include_router(product_router, prefix="/admin/product", tags=["admin-product"])
app.include_router(license_router, prefix="/admin/license", tags=["admin-license"])
app.include_router(client_router, prefix="/admin/client", tags=["admin-client"])
app.include_router(audit_router, prefix="/admin/audit", tags=["admin-audit"])
app.include_router(license_api_router, prefix="/api/v1/license", tags=["license-api"])

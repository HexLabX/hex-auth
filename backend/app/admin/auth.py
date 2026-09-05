from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.jwt import create_access_token, verify_token
from app.core.config import settings
from app.models.admin_user import AdminUser, AdminStatus
from app.schemas.auth import LoginRequest, LoginResponse
from app.utils.audit_utils import create_audit_log
import bcrypt

router = APIRouter()

# OAuth2密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/auth/login")

# 验证密码
def verify_password(plain_password, hashed_password):
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

# 获取密码哈希值
def get_password_hash(password):
    password_bytes = password.encode('utf-8')
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

# 获取当前管理员
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if admin is None:
        raise credentials_exception
    # 已被禁用的管理员，其存量令牌立即失效
    if admin.status == AdminStatus.DISABLED:
        raise credentials_exception
    return admin

# 登录路由
@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 查询管理员
    admin = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
    
    # 验证管理员和密码
    if not admin or not verify_password(form_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 拒绝被禁用的管理员登录
    if admin.status == AdminStatus.DISABLED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新登录时间
    from datetime import datetime, timezone
    admin.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # 记录登录审计日志
    create_audit_log(
        db=db,
        admin_username=admin.username,
        action="登录",
        target_type="管理员",
        target_id=admin.id,
        target_instance=admin
    )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# 获取当前管理员信息
@router.get("/me")
def get_me(current_admin: AdminUser = Depends(get_current_admin)):
    return {
        "username": current_admin.username,
        "status": current_admin.status,
        "last_login": current_admin.last_login,
        "created_at": current_admin.created_at
    }

# 修改密码
@router.post("/change-password")
def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    # 验证旧密码
    if not verify_password(old_password, current_admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 检查新密码长度
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度不能少于6位"
        )

    # 更新密码
    current_admin.password_hash = get_password_hash(new_password)
    db.commit()

    # 记录审计日志
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="修改密码",
        target_type="管理员",
        target_id=current_admin.id,
        target_instance=current_admin
    )

    return {"message": "密码修改成功"}
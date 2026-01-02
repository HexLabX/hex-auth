from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.client import Client, ClientStatus
from app.schemas.client import ClientResponse
from app.admin.auth import get_current_admin
from app.utils.audit_utils import create_audit_log

router = APIRouter()

# 查询客户端实例列表
@router.get("/", response_model=List[ClientResponse])
def get_clients(
    skip: int = 0,
    limit: int = 100,
    status: ClientStatus = None,
    product_code: str = None,
    license_id: int = None,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    query = db.query(Client)
    
    # 按状态过滤
    if status:
        query = query.filter(Client.status == status)
    
    # 按产品代码过滤
    if product_code:
        query = query.filter(Client.product_code == product_code)
    
    # 按授权ID过滤
    if license_id:
        query = query.filter(Client.license_id == license_id)
    
    clients = query.offset(skip).limit(limit).all()
    return clients

# 查询单个客户端实例
@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client

# 禁用客户端实例
@router.post("/{client_id}/disable", response_model=ClientResponse)
def disable_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # 禁用客户端
    client.status = ClientStatus.DISABLED
    
    db.commit()
    db.refresh(client)
    
    # 记录审计日志
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="禁用",
        target_type="客户端实例",
        target_id=client.id,
        target_instance=client
    )
    
    return client

# 启用客户端实例
@router.post("/{client_id}/enable", response_model=ClientResponse)
def enable_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # 启用客户端
    client.status = ClientStatus.NORMAL
    
    db.commit()
    db.refresh(client)
    
    # 记录审计日志
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="启用",
        target_type="客户端实例",
        target_id=client.id,
        target_instance=client
    )
    
    return client

# 删除客户端实例
@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # 记录审计日志
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="删除",
        target_type="客户端实例",
        target_id=client.id,
        target_instance=client
    )
    
    # 删除客户端
    db.delete(client)
    db.commit()
    
    return None
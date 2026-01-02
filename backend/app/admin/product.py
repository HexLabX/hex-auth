from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.rsa import generate_rsa_key_pair
from app.models.admin_user import AdminUser
from app.models.product import Product, ProductStatus
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.admin.auth import get_current_admin
from app.utils.audit_utils import create_audit_log

router = APIRouter()

# 创建产品
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    # 检查产品代码是否已存在
    existing_product = db.query(Product).filter(Product.product_code == product.product_code).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code already exists"
        )
    
    # 生成RSA密钥对
    private_key, public_key = generate_rsa_key_pair()
    
    # 创建产品
    db_product = Product(
        product_code=product.product_code,
        name=product.name,
        public_key=public_key,
        private_key=private_key,
        heartbeat_interval=product.heartbeat_interval,
        status=product.status
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # 记录审计日志
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="创建",
        target_type="产品",
        target_id=db_product.id,
        target_instance=db_product
    )
    
    return db_product

# 查询产品列表
@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    status: ProductStatus = None,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    query = db.query(Product)
    
    # 按状态过滤
    if status:
        query = query.filter(Product.status == status)
    
    products = query.offset(skip).limit(limit).all()
    return products

# 查询单个产品
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

# 更新产品
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # 更新产品信息
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    # 记录审计日志
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="更新",
        target_type="产品",
        target_id=product.id,
        target_instance=product,
        detail={"updated_fields": list(update_data.keys())}
    )
    
    return product

# 删除产品
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # 记录审计日志
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="删除",
        target_type="产品",
        target_id=product.id,
        target_instance=product
    )
    
    db.delete(product)
    db.commit()
    
    return None
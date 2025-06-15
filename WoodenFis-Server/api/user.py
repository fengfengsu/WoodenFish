from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal
from typing import List
import random
import string
from datetime import datetime, timedelta

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_verification_code() -> str:
    """生成6位数字验证码"""
    return ''.join(random.choices(string.digits, k=6))

@router.post("/send-code", response_model=schemas.SendCodeResponse)
def send_verification_code(request: schemas.SendCodeRequest, db: Session = Depends(get_db)):
    """
    发送验证码
    """
    # 验证手机号格式
    if not request.phone.startswith('1') or len(request.phone) != 11:
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    
    # 生成验证码
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)  # 5分钟过期
    
    # 保存验证码到数据库
    crud.create_verification_code(db, request.phone, code, expires_at)
    
    # TODO: 在实际应用中，这里应该调用短信服务发送验证码
    # 现在仅用于演示，返回生成的验证码（生产环境中绝不能这样做）
    return schemas.SendCodeResponse(
        message=f"验证码已发送到 {request.phone}，测试用验证码: {code}",
        success=True
    )

@router.post("/login", response_model=schemas.LoginResponse)
def login_with_code(request: schemas.VerifyCodeRequest, db: Session = Depends(get_db)):
    """
    验证码登录
    """
    # 验证验证码
    verification_code = crud.get_valid_verification_code(db, request.phone, request.code)
    if not verification_code:
        raise HTTPException(status_code=400, detail="验证码无效或已过期")
    
    # 标记验证码为已使用
    crud.use_verification_code(db, verification_code.id)
    
    # 查找或创建用户
    user = crud.get_user_by_phone(db, request.phone)
    if not user:
        # 如果用户不存在，自动创建新用户
        username = f"用户{request.phone[-4:]}"  # 使用手机号后4位生成用户名
        user_create = schemas.UserCreateByPhone(
            username=username,
            phone=request.phone
        )
        user = crud.create_user_by_phone(db, user_create)
        
        # 为新用户创建统计记录
        crud.create_user_stat(db, user.id)
    
    return schemas.LoginResponse(
        user=user,
        message="登录成功"
    )

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    传统注册方式（保留兼容性）
    """
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    if user.email:
        db_user = crud.get_user_by_email(db, user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="邮箱已注册")
    
    if user.phone:
        db_user = crud.get_user_by_phone(db, user.phone)
        if db_user:
            raise HTTPException(status_code=400, detail="手机号已注册")
    
    # 密码加密（示例，实际应用请用更安全的hash）
    hashed_password = None
    if user.password:
        hashed_password = user.password + "notreallyhashed"
    
    return crud.create_user(db, user, hashed_password)

@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户信息
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

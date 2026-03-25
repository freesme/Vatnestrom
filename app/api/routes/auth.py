"""
认证 API 路由

接口列表:
  - POST /auth/register           注册新用户
  - POST /auth/login              用户登录，返回 JWT
  - POST /auth/logout             登出，使所有令牌失效
  - GET  /auth/me                 获取当前用户信息
  - PUT  /auth/users/{user_id}/role  修改用户角色（仅管理员）
  - PUT  /auth/users/{user_id}/ban   封禁/解封用户（仅管理员）
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Role
from app.services.auth import (
    create_access_token,
    create_user,
    decode_access_token,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_user_role,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------- Pydantic schemas ----------

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleUpdateRequest(BaseModel):
    role: Role


class BanRequest(BaseModel):
    is_active: bool


# ---------- 依赖 ----------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """从 JWT 中解析当前用户"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")
    user = get_user_by_id(db, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账户已被禁用")
    if payload.get("tv", 0) != user.token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌已失效")
    return user


def require_admin(current_user=Depends(get_current_user)):
    """要求当前用户为管理员"""
    if current_user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user


# ---------- 辅助 ----------

def _user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=str(user.created_at),
    )


# ---------- 路由 ----------

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """注册新用户"""
    if get_user_by_username(db, req.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if get_user_by_email(db, req.email):
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = create_user(db, req.username, req.email, req.password)
    logger.info("user registered | id=%d username=%s", user.id, user.username)
    return _user_response(user)


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录，返回 JWT 令牌

    使用 OAuth2 标准表单字段：username + password
    """
    user = get_user_by_username(db, form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被禁用")

    token = create_access_token(user.id, user.role.value, user.token_version)
    logger.info("user logged in | id=%d username=%s", user.id, user.username)
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """登出：使当前用户的所有令牌失效"""
    current_user.token_version += 1
    db.commit()
    logger.info("user logged out | id=%d username=%s", current_user.id, current_user.username)


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    """获取当前登录用户信息"""
    return _user_response(current_user)


@router.put("/users/{user_id}/role", response_model=UserResponse)
def change_role(
    user_id: int,
    req: RoleUpdateRequest,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """修改用户角色（仅管理员可操作）"""
    user = update_user_role(db, user_id, req.role)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    logger.info("role updated | id=%d new_role=%s by_admin=%s", user.id, req.role.value, admin.username)
    return _user_response(user)


@router.put("/users/{user_id}/ban", response_model=UserResponse)
def ban_user(
    user_id: int,
    req: BanRequest,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """封禁/解封用户（仅管理员可操作）"""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能封禁自己")

    user.is_active = req.is_active
    if not req.is_active:
        user.token_version += 1
    db.commit()
    db.refresh(user)

    action = "banned" if not req.is_active else "unbanned"
    logger.info("user %s | id=%d by_admin=%s", action, user.id, admin.username)
    return _user_response(user)

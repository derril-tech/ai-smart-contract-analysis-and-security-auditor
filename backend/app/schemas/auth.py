"""
Authentication schemas for ChainGuard AI
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

from app.core.security import validate_email, validate_password_strength


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class RoleType(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True
    is_verified: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    tenant_id: Optional[str] = None
    role_ids: Optional[List[str]] = []
    
    @validator('password')
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v
    
    @validator('email')
    def validate_email_format(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = None
    language: Optional[str] = None


class UserResponse(UserBase):
    id: str
    tenant_id: str
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    roles: List['RoleResponse'] = []
    permissions: List[str] = []
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


# Tenant schemas
class TenantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    domain: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    max_users: int = Field(default=5, ge=1, le=1000)
    max_projects: int = Field(default=10, ge=1, le=10000)
    max_storage_gb: int = Field(default=1, ge=1, le=1000)


class TenantCreate(TenantBase):
    admin_email: EmailStr
    admin_first_name: str = Field(..., min_length=1, max_length=50)
    admin_last_name: str = Field(..., min_length=1, max_length=50)
    admin_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('admin_password')
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    domain: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    subscription_plan: Optional[SubscriptionPlan] = None
    max_users: Optional[int] = Field(None, ge=1, le=1000)
    max_projects: Optional[int] = Field(None, ge=1, le=10000)
    max_storage_gb: Optional[int] = Field(None, ge=1, le=1000)
    settings: Optional[dict] = None


class TenantResponse(TenantBase):
    id: str
    settings: dict = {}
    created_at: datetime
    updated_at: datetime
    user_count: int = 0
    project_count: int = 0
    storage_used_gb: float = 0.0
    
    class Config:
        from_attributes = True


# Role schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    is_system: bool = False


class RoleCreate(RoleBase):
    permission_ids: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permission_ids: Optional[List[str]] = None


class RoleResponse(RoleBase):
    id: str
    permissions: List['PermissionResponse'] = []
    user_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Permission schemas
class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    is_system: bool = False


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    resource: Optional[str] = Field(None, min_length=1, max_length=50)
    action: Optional[str] = Field(None, min_length=1, max_length=50)


class PermissionResponse(PermissionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Authentication schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False
    totp_token: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v):
        validation = validate_password_strength(v)
        if not validation['valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# Two-factor authentication schemas
class Setup2FARequest(BaseModel):
    password: str


class Setup2FAResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class Verify2FARequest(BaseModel):
    token: str


class Disable2FARequest(BaseModel):
    password: str
    backup_code: Optional[str] = None


# Session schemas
class SessionInfo(BaseModel):
    id: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    is_active: bool


class SessionListResponse(BaseModel):
    sessions: List[SessionInfo]
    total: int


# Audit log schemas
class AuditLogBase(BaseModel):
    event_type: str
    user_id: str
    tenant_id: str
    details: dict
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    id: str
    created_at: datetime
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int


# API key schemas
class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    permissions: List[str] = []
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyResponse(APIKeyBase):
    id: str
    key_prefix: str
    created_at: datetime
    last_used_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    api_keys: List[APIKeyResponse]
    total: int


# Update forward references
UserResponse.model_rebuild()
RoleResponse.model_rebuild()
PermissionResponse.model_rebuild()

"""
Authentication API routes for ChainGuard AI
"""

from datetime import timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    verify_token, get_current_user_id, get_current_tenant_id, get_current_user_permissions,
    log_security_event, get_client_ip, rate_limit, generate_secure_password,
    create_session_token, invalidate_session, generate_totp_secret, verify_totp,
    generate_backup_codes, encrypt_sensitive_data, decrypt_sensitive_data
)
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    LogoutRequest, UserCreate, UserResponse, UserUpdate, UserListResponse,
    TenantCreate, TenantResponse, TenantUpdate, RoleCreate, RoleResponse,
    RoleUpdate, PermissionCreate, PermissionResponse, PermissionUpdate,
    ChangePasswordRequest, ResetPasswordRequest, ResetPasswordConfirm,
    VerifyEmailRequest, ResendVerificationRequest, Setup2FARequest,
    Setup2FAResponse, Verify2FARequest, Disable2FARequest, SessionInfo,
    SessionListResponse, AuditLogResponse, AuditLogListResponse,
    APIKeyCreate, APIKeyResponse, APIKeyListResponse
)
from app.models.user import User, Tenant, Role, Permission, RefreshToken, AuditLog, UserSession
from app.models.base import TenantModel

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
@rate_limit(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """User login endpoint"""
    try:
        # Get user by email
        result = await db.execute(
            "SELECT * FROM user WHERE email = :email AND is_active = true",
            {"email": request.email}
        )
        user_data = result.fetchone()
        
        if not user_data:
            log_security_event(
                "login_failed",
                "unknown",
                "unknown",
                {"email": request.email, "reason": "user_not_found"},
                get_client_ip(req)
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(request.password, user_data.password_hash):
            log_security_event(
                "login_failed",
                user_data.id,
                user_data.tenant_id,
                {"email": request.email, "reason": "invalid_password"},
                get_client_ip(req)
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is verified
        if not user_data.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified"
            )
        
        # Verify 2FA if enabled
        if user_data.totp_secret:
            if not request.totp_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="2FA token required"
                )
            
            if not verify_totp(user_data.totp_secret, request.totp_token):
                log_security_event(
                    "login_failed",
                    user_data.id,
                    user_data.tenant_id,
                    {"email": request.email, "reason": "invalid_2fa"},
                    get_client_ip(req)
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid 2FA token"
                )
        
        # Get user permissions
        permissions = await get_user_permissions(db, user_data.id)
        
        # Create tokens
        access_token_expires = timedelta(minutes=30 if not request.remember_me else 1440)  # 30 min or 24 hours
        access_token = create_access_token(
            subject=user_data.id,
            expires_delta=access_token_expires,
            tenant_id=user_data.tenant_id,
            permissions=permissions
        )
        
        refresh_token = create_refresh_token(subject=user_data.id)
        
        # Store refresh token
        await db.execute(
            "INSERT INTO refreshtoken (token_hash, user_id, expires_at, created_at) VALUES (:token_hash, :user_id, :expires_at, NOW())",
            {
                "token_hash": get_password_hash(refresh_token),
                "user_id": user_data.id,
                "expires_at": timedelta(days=30)
            }
        )
        
        # Update last login
        await db.execute(
            "UPDATE user SET last_login_at = NOW() WHERE id = :user_id",
            {"user_id": user_data.id}
        )
        
        # Create session
        session_token = create_session_token(user_data.id, user_data.tenant_id)
        await db.execute(
            "INSERT INTO usersession (session_id, user_id, tenant_id, user_agent, ip_address, expires_at, created_at) VALUES (:session_id, :user_id, :tenant_id, :user_agent, :ip_address, :expires_at, NOW())",
            {
                "session_id": session_token,
                "user_id": user_data.id,
                "tenant_id": user_data.tenant_id,
                "user_agent": req.headers.get("User-Agent"),
                "ip_address": get_client_ip(req),
                "expires_at": timedelta(hours=24)
            }
        )
        
        await db.commit()
        
        # Log successful login
        log_security_event(
            "login_success",
            user_data.id,
            user_data.tenant_id,
            {"email": request.email},
            get_client_ip(req)
        )
        
        # Build user response
        user_response = UserResponse(
            id=user_data.id,
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=user_data.is_active,
            is_verified=user_data.is_verified,
            tenant_id=user_data.tenant_id,
            profile_picture_url=user_data.profile_picture_url,
            bio=user_data.bio,
            timezone=user_data.timezone,
            language=user_data.language,
            last_login_at=user_data.last_login_at,
            created_at=user_data.created_at,
            updated_at=user_data.updated_at,
            roles=[],
            permissions=permissions
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        
        # Check if refresh token exists in database
        result = await db.execute(
            "SELECT * FROM refreshtoken WHERE user_id = :user_id AND expires_at > NOW()",
            {"user_id": user_id}
        )
        refresh_token_data = result.fetchone()
        
        if not refresh_token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user permissions
        permissions = await get_user_permissions(db, user_id)
        
        # Create new access token
        access_token = create_access_token(
            subject=user_id,
            tenant_id=payload.get("tenant_id"),
            permissions=permissions
        )
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800  # 30 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """Logout user"""
    try:
        # Invalidate refresh token
        await db.execute(
            "DELETE FROM refreshtoken WHERE token_hash = :token_hash",
            {"token_hash": get_password_hash(request.refresh_token)}
        )
        
        await db.commit()
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error("Logout error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/register", response_model=UserResponse)
@rate_limit(max_requests=3, window_seconds=3600)  # 3 registrations per hour
async def register(
    request: UserCreate,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """User registration endpoint"""
    try:
        # Check if user already exists
        result = await db.execute(
            "SELECT id FROM user WHERE email = :email OR username = :username",
            {"email": request.email, "username": request.username}
        )
        existing_user = result.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Hash password
        password_hash = get_password_hash(request.password)
        
        # Create user
        await db.execute(
            """
            INSERT INTO user (email, username, password_hash, first_name, last_name, 
                             is_active, is_verified, tenant_id, created_at, updated_at)
            VALUES (:email, :username, :password_hash, :first_name, :last_name,
                    :is_active, :is_verified, :tenant_id, NOW(), NOW())
            """,
            {
                "email": request.email,
                "username": request.username,
                "password_hash": password_hash,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "is_active": request.is_active,
                "is_verified": request.is_verified,
                "tenant_id": request.tenant_id
            }
        )
        
        await db.commit()
        
        # Log registration
        log_security_event(
            "user_registered",
            "new_user",
            request.tenant_id or "unknown",
            {"email": request.email, "username": request.username},
            get_client_ip(req)
        )
        
        # Return user data (without password)
        return UserResponse(
            id="new_user_id",  # Would be actual ID in real implementation
            email=request.email,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            is_active=request.is_active,
            is_verified=request.is_verified,
            tenant_id=request.tenant_id or "",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            roles=[],
            permissions=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    try:
        # Get current user
        result = await db.execute(
            "SELECT password_hash FROM user WHERE id = :user_id",
            {"user_id": current_user_id}
        )
        user_data = result.fetchone()
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(request.current_password, user_data.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_password_hash = get_password_hash(request.new_password)
        await db.execute(
            "UPDATE user SET password_hash = :password_hash, updated_at = NOW() WHERE id = :user_id",
            {"password_hash": new_password_hash, "user_id": current_user_id}
        )
        
        # Invalidate all refresh tokens
        await db.execute(
            "DELETE FROM refreshtoken WHERE user_id = :user_id",
            {"user_id": current_user_id}
        )
        
        await db.commit()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password change error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset"""
    try:
        # Check if user exists
        result = await db.execute(
            "SELECT id FROM user WHERE email = :email AND is_active = true",
            {"email": request.email}
        )
        user_data = result.fetchone()
        
        if user_data:
            # Generate reset token (in real implementation, send email)
            reset_token = create_access_token(
                subject=user_data.id,
                expires_delta=timedelta(hours=1)
            )
            
            # Store reset token (in real implementation, store in database)
            logger.info(f"Password reset token for {request.email}: {reset_token}")
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        logger.error("Password reset error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/reset-password/confirm")
async def reset_password_confirm(
    request: ResetPasswordConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset"""
    try:
        # Verify reset token
        payload = verify_token(request.token)
        user_id = payload.get("sub")
        
        # Update password
        new_password_hash = get_password_hash(request.new_password)
        await db.execute(
            "UPDATE user SET password_hash = :password_hash, updated_at = NOW() WHERE id = :user_id",
            {"password_hash": new_password_hash, "user_id": user_id}
        )
        
        # Invalidate all refresh tokens
        await db.execute(
            "DELETE FROM refreshtoken WHERE user_id = :user_id",
            {"user_id": user_id}
        )
        
        await db.commit()
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password reset confirm error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify email address"""
    try:
        # Verify token and update user
        payload = verify_token(request.token)
        user_id = payload.get("sub")
        
        await db.execute(
            "UPDATE user SET is_verified = true, updated_at = NOW() WHERE id = :user_id",
            {"user_id": user_id}
        )
        
        await db.commit()
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Email verification error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resend email verification"""
    try:
        # Check if user exists and is not verified
        result = await db.execute(
            "SELECT id FROM user WHERE email = :email AND is_verified = false",
            {"email": request.email}
        )
        user_data = result.fetchone()
        
        if user_data:
            # Generate verification token (in real implementation, send email)
            verification_token = create_access_token(
                subject=user_data.id,
                expires_delta=timedelta(hours=24)
            )
            
            logger.info(f"Verification token for {request.email}: {verification_token}")
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists and is not verified, a verification link has been sent"}
        
    except Exception as e:
        logger.error("Resend verification error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Two-factor authentication endpoints
@router.post("/2fa/setup", response_model=Setup2FAResponse)
async def setup_2fa(
    request: Setup2FARequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Setup two-factor authentication"""
    try:
        # Verify password
        result = await db.execute(
            "SELECT password_hash FROM user WHERE id = :user_id",
            {"user_id": current_user_id}
        )
        user_data = result.fetchone()
        
        if not verify_password(request.password, user_data.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )
        
        # Generate TOTP secret
        totp_secret = generate_totp_secret()
        backup_codes = generate_backup_codes()
        
        # Encrypt and store secret
        encrypted_secret = encrypt_sensitive_data(totp_secret)
        await db.execute(
            "UPDATE user SET totp_secret = :totp_secret, backup_codes = :backup_codes, updated_at = NOW() WHERE id = :user_id",
            {
                "totp_secret": encrypted_secret,
                "backup_codes": backup_codes,
                "user_id": current_user_id
            }
        )
        
        await db.commit()
        
        return Setup2FAResponse(
            secret=totp_secret,
            qr_code_url=f"otpauth://totp/ChainGuard:{current_user_id}?secret={totp_secret}&issuer=ChainGuard",
            backup_codes=backup_codes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("2FA setup error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/2fa/verify")
async def verify_2fa(
    request: Verify2FARequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Verify two-factor authentication"""
    try:
        # Get user's TOTP secret
        result = await db.execute(
            "SELECT totp_secret FROM user WHERE id = :user_id",
            {"user_id": current_user_id}
        )
        user_data = result.fetchone()
        
        if not user_data.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA not enabled"
            )
        
        # Decrypt and verify TOTP
        decrypted_secret = decrypt_sensitive_data(user_data.totp_secret)
        if not verify_totp(decrypted_secret, request.token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA token"
            )
        
        return {"message": "2FA verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("2FA verification error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/2fa/disable")
async def disable_2fa(
    request: Disable2FARequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Disable two-factor authentication"""
    try:
        # Verify password
        result = await db.execute(
            "SELECT password_hash, backup_codes FROM user WHERE id = :user_id",
            {"user_id": current_user_id}
        )
        user_data = result.fetchone()
        
        if not verify_password(request.password, user_data.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password"
            )
        
        # Verify backup code if provided
        if request.backup_code and request.backup_code not in user_data.backup_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid backup code"
            )
        
        # Disable 2FA
        await db.execute(
            "UPDATE user SET totp_secret = NULL, backup_codes = NULL, updated_at = NOW() WHERE id = :user_id",
            {"user_id": current_user_id}
        )
        
        await db.commit()
        
        return {"message": "2FA disabled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("2FA disable error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Helper function to get user permissions
async def get_user_permissions(db: AsyncSession, user_id: str) -> List[str]:
    """Get user permissions from database"""
    try:
        result = await db.execute(
            """
            SELECT DISTINCT p.name
            FROM permission p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = :user_id
            """,
            {"user_id": user_id}
        )
        
        permissions = [row.name for row in result.fetchall()]
        return permissions
        
    except Exception as e:
        logger.error("Error getting user permissions", error=str(e))
        return []

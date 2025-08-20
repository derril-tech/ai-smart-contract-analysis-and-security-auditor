"""
Security utilities for ChainGuard AI
"""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

# Token types
class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"
    API = "api"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def generate_secure_password(length: int = 16) -> str:
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
            return password


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = TokenType.ACCESS,
    tenant_id: Optional[str] = None,
    permissions: Optional[list] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": token_type,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_urlsafe(32)
    }
    
    if tenant_id:
        to_encode["tenant_id"] = tenant_id
    
    if permissions:
        to_encode["permissions"] = permissions
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": TokenType.REFRESH,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_urlsafe(32)
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning("JWT token verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Get current user ID from JWT token"""
    payload = verify_token(credentials.credentials)
    
    if payload.get("type") != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return user_id


def get_current_tenant_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Get current tenant ID from JWT token"""
    payload = verify_token(credentials.credentials)
    
    tenant_id: str = payload.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant ID not found in token"
        )
    
    return tenant_id


def get_current_user_permissions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> list:
    """Get current user permissions from JWT token"""
    payload = verify_token(credentials.credentials)
    
    permissions: list = payload.get("permissions", [])
    return permissions


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db_session = Depends(lambda: None)  # Will be injected by FastAPI
):
    """Get current user from database"""
    from app.models.user import User
    
    # This would typically query the database
    # For now, return a mock user object
    # In real implementation, you'd query the database
    return {
        "id": user_id,
        "email": "user@example.com",
        "username": "user",
        "is_active": True,
        "tenant_id": "tenant_id"
    }


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get permissions from token
            permissions = get_current_user_permissions()
            
            if permission not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: str):
    """Decorator to require specific role"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get user from token and check role
            # This would typically query the database
            # For now, just pass through
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Rate limiting
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed"""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[key]) < max_requests:
            self.requests[key].append(now)
            return True
        
        return False


rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        async def wrapper(request, *args, **kwargs):
            # Get client IP
            client_ip = request.client.host
            
            if not rate_limiter.is_allowed(client_ip, max_requests, window_seconds):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# API key authentication
def verify_api_key(api_key: str) -> bool:
    """Verify API key"""
    # In production, this would check against database
    # For now, just check against environment variable
    return api_key == settings.API_KEY


def get_api_key_user(api_key: str):
    """Get user from API key"""
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Return system user for API key
    return {
        "id": "api_user",
        "email": "api@chainguard.ai",
        "username": "api_user",
        "is_active": True,
        "tenant_id": "system"
    }


# Security headers
def get_security_headers() -> dict:
    """Get security headers"""
    return {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:;"
        ),
        "Permissions-Policy": (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        ),
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }


# Input validation and sanitization
def sanitize_input(input_str: str) -> str:
    """Sanitize user input"""
    import html
    
    # HTML escape
    sanitized = html.escape(input_str)
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Remove control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
    
    return sanitized


def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> dict:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*" for c in password):
        errors.append("Password must contain at least one special character (!@#$%^&*)")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# Audit logging
def log_security_event(
    event_type: str,
    user_id: str,
    tenant_id: str,
    details: dict,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log security event"""
    logger.info(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        tenant_id=tenant_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )


# Session management
def create_session_token(user_id: str, tenant_id: str) -> str:
    """Create session token"""
    return create_access_token(
        subject=user_id,
        token_type=TokenType.ACCESS,
        tenant_id=tenant_id,
        expires_delta=timedelta(hours=24)
    )


def invalidate_session(session_id: str):
    """Invalidate session"""
    # In production, this would add to a blacklist in Redis
    logger.info("Session invalidated", session_id=session_id)


# Two-factor authentication
def generate_totp_secret() -> str:
    """Generate TOTP secret"""
    import base64
    import os
    
    secret = os.urandom(20)
    return base64.b32encode(secret).decode('utf-8')


def verify_totp(secret: str, token: str) -> bool:
    """Verify TOTP token"""
    try:
        import pyotp
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    except Exception as e:
        logger.error("TOTP verification failed", error=str(e))
        return False


def generate_backup_codes() -> list:
    """Generate backup codes for 2FA"""
    codes = []
    for _ in range(10):
        code = ''.join(secrets.choice(string.digits) for _ in range(8))
        codes.append(code)
    return codes


# Encryption utilities
def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data"""
    from cryptography.fernet import Fernet
    
    key = settings.ENCRYPTION_KEY.encode()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    from cryptography.fernet import Fernet
    
    key = settings.ENCRYPTION_KEY.encode()
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data.encode())
    return decrypted_data.decode()


# CSRF protection
def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verify CSRF token"""
    # In production, this would check against session
    # For now, just return True
    return True


# Security middleware helpers
def get_client_ip(request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def is_suspicious_request(request) -> bool:
    """Check if request is suspicious"""
    suspicious_indicators = [
        # SQL injection patterns
        "'; DROP TABLE",
        "UNION SELECT",
        "OR 1=1",
        # XSS patterns
        "<script>",
        "javascript:",
        "onload=",
        # Path traversal
        "../",
        "..\\",
        # Command injection
        "; rm -rf",
        "| cat /etc/passwd",
    ]
    
    # Check URL
    url = str(request.url)
    for indicator in suspicious_indicators:
        if indicator.lower() in url.lower():
            return True
    
    # Check headers
    for header_name, header_value in request.headers.items():
        for indicator in suspicious_indicators:
            if indicator.lower() in header_value.lower():
                return True
    
    return False

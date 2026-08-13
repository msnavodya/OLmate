import logging
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config import settings
import os

logger = logging.getLogger("olmate.auth")

bearer_scheme = HTTPBearer(auto_error=False)

# Prefer strong hashing (argon2). Only allow insecure fallback when explicitly enabled.
try:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
except Exception:
    if settings.DEBUG or settings.ALLOW_INSECURE_FALLBACK:
        logger.warning("argon2 not available; using plaintext fallback for development")
        pwd_context = CryptContext(schemes=["plaintext"], deprecated="auto")
    else:
        raise


def hash_password(password: str) -> str:
    """Hash password using argon2 (preferred)."""
    if not password:
        raise ValueError("Password must not be empty")

    try:
        return pwd_context.hash(password)
    except Exception:
        if settings.DEBUG or settings.ALLOW_INSECURE_FALLBACK:
            import hashlib
            salt = os.urandom(16).hex()
            pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return f"dev${salt}${pwd_hash}"
        logger.exception("Password hashing failed in production mode")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash. Supports dev fallback format beginning with 'dev$'."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        if settings.DEBUG or settings.ALLOW_INSECURE_FALLBACK:
            if hashed_password.startswith("dev$"):
                import hashlib
                parts = hashed_password.split("$")
                if len(parts) == 3:
                    salt = parts[1]
                    expected_hash = parts[2]
                    actual_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
                    return actual_hash == expected_hash
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=15)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return user_id

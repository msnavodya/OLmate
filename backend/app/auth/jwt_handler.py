from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from config import settings
import os

# Use argon2 for password hashing (more reliable than bcrypt)
try:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
except Exception:
    # Fallback to simple hash for development if argon2 not available
    pwd_context = CryptContext(schemes=["plaintext"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using argon2 or fallback"""
    # Truncate password to avoid bcrypt 72-byte limit
    if len(password) > 72:
        password = password[:72]
    try:
        return pwd_context.hash(password)
    except Exception as e:
        # Fallback: simple hash for development
        import hashlib
        salt = os.urandom(32).hex()
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"dev${salt}${pwd_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # Truncate password to avoid bcrypt 72-byte limit
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback: simple hash verification for development
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
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
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

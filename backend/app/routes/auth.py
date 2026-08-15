from fastapi import APIRouter, Depends, HTTPException, status
import logging
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from app.models.user import PasswordChange, UserRegister, UserLogin, UserResponse, UserUpdate, TokenResponse
from app.auth.jwt_handler import get_current_user_id, hash_password, verify_password, create_access_token
from app.database.mongodb import get_database
from config import settings

router = APIRouter()

logger = logging.getLogger("olmate.auth.routes")

def get_db():
    return get_database()

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister, db=Depends(get_db)):
    users_collection = db["users"]
    email = user.email.strip().lower()
    name = user.name.strip()

    if len(name) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name must be at least 2 characters"
        )

    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    logger.info("Register attempt for email=%s", email)
    # Check if user exists
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        logger.warning("Registration failed: email already registered %s", email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user.password)
    new_user = {
        "name": name,
        "email": email,
        "password_hash": hashed_password,
        "role": user.role,
        "created_at": datetime.utcnow()
    }
    
    result = users_collection.insert_one(new_user)
    user_id = str(result.inserted_id)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info("User registered id=%s email=%s", user_id, email)

    return TokenResponse(
        access_token=access_token,
        user={
            "id": user_id,
            "name": name,
            "email": email,
            "role": user.role
        }
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db=Depends(get_db)):
    users_collection = db["users"]
    email = credentials.email.strip().lower()
    logger.info("Login attempt for email=%s", email)

    # Find user
    user = users_collection.find_one({"email": email})
    if not user or not verify_password(credentials.password, user.get("password_hash")):
        logger.warning("Login failed for email=%s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    )

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    user = _find_user_by_id(db, current_user_id)
    return _to_user_response(user)

@router.patch("/me", response_model=UserResponse)
async def update_profile(
    updates: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    users_collection = db["users"]
    user = _find_user_by_id(db, current_user_id)
    changes = {}

    if updates.name is not None:
        name = updates.name.strip()
        if len(name) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name must be at least 2 characters",
            )
        changes["name"] = name

    if updates.email is not None:
        email = updates.email.strip().lower()
        existing_user = users_collection.find_one({"email": email})
        if existing_user and str(existing_user["_id"]) != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        changes["email"] = email

    if changes:
        users_collection.update_one({"_id": user["_id"]}, {"$set": changes})
        user.update(changes)

    return _to_user_response(user)

@router.post("/me/password")
async def change_password(
    payload: PasswordChange,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if len(payload.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters",
        )

    users_collection = db["users"]
    user = _find_user_by_id(db, current_user_id)
    if not verify_password(payload.current_password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": hash_password(payload.new_password)}},
    )
    return {"message": "Password updated successfully"}

def _find_user_by_id(db, user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token",
        )

    user = db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

def _to_user_response(user) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user["role"],
        created_at=user.get("created_at"),
    )

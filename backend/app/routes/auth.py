from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from bson.objectid import ObjectId
from app.models.user import UserRegister, UserLogin, TokenResponse
from app.auth.jwt_handler import hash_password, verify_password, create_access_token
from app.database.mongodb import get_database
from config import settings

router = APIRouter()

def get_db():
    return get_database()

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister, db=Depends(get_db)):
    users_collection = db["users"]
    
    # Check if user exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "password_hash": hashed_password,
        "role": user.role,
        "created_at": __import__("datetime").datetime.utcnow()
    }
    
    result = users_collection.insert_one(new_user)
    user_id = str(result.inserted_id)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db=Depends(get_db)):
    users_collection = db["users"]
    
    # Find user
    user = users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password_hash"]):
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

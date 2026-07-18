from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.database.mongodb import get_database

router = APIRouter()

def get_db():
    return get_database()

@router.get("/users")
async def get_users(db=Depends(get_db)):
    users_collection = db["users"]
    users = list(users_collection.find({}, {"password_hash": 0}))
    
    return [
        {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user.get("created_at")
        }
        for user in users
    ]

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), db=Depends(get_db)):
    """
    Upload study materials (PDFs, notes) to knowledge base.
    This will be fully implemented in Phase 3.
    """
    return {
        "message": "Document upload endpoint - will be implemented in Phase 3",
        "filename": file.filename
    }

@router.get("/analytics")
async def get_analytics(db=Depends(get_db)):
    """
    Get chatbot usage analytics.
    This will be fully implemented in Phase 4.
    """
    chats_collection = db["chats"]
    total_chats = chats_collection.count_documents({})
    
    return {
        "total_chats": total_chats,
        "message": "Full analytics will be implemented in Phase 4"
    }

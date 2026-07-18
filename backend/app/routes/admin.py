from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pathlib import Path
from config import settings
from app.database.mongodb import get_database
from app.rag.rag_service import SUPPORTED_EXTENSIONS, process_pdf

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
    """Upload study materials to the local knowledge base."""
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()
    if not filename or suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt, .md, and .pdf knowledge files are supported",
        )

    knowledge_base_path = Path(settings.KNOWLEDGE_BASE_PATH).expanduser().resolve()
    knowledge_base_path.mkdir(parents=True, exist_ok=True)
    destination = knowledge_base_path / filename

    destination.write_bytes(await file.read())
    metadata = process_pdf(str(destination)) if suffix == ".pdf" else {"filename": filename}

    return {
        "message": "Document uploaded and ready for chat and quizzes",
        "filename": filename,
        "metadata": metadata,
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

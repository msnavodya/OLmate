from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from bson.objectid import ObjectId

from config import settings
from app.auth.jwt_handler import get_current_user_id
from app.database.mongodb import get_database
from app.rag.rag_service import SUPPORTED_EXTENSIONS, process_pdf

router = APIRouter()

def get_db():
    return get_database()


def require_admin(current_user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    if not ObjectId.is_valid(current_user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token")

    user = db["users"].find_one({"_id": ObjectId(current_user_id)})
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def knowledge_base_path() -> Path:
    path = Path(settings.KNOWLEDGE_BASE_PATH).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path

@router.get("/users")
async def get_users(db=Depends(get_db), _admin=Depends(require_admin)):
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
async def upload_document(file: UploadFile = File(...), _admin=Depends(require_admin)):
    """Upload study materials to the local knowledge base."""
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()
    if not filename or suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt, .md, and .pdf knowledge files are supported",
        )

    destination = knowledge_base_path() / filename

    destination.write_bytes(await file.read())
    metadata = process_pdf(str(destination)) if suffix == ".pdf" else {"filename": filename}

    return {
        "message": "Document uploaded and ready for chat and quizzes",
        "filename": filename,
        "metadata": metadata,
    }


@router.get("/documents")
async def list_documents(_admin=Depends(require_admin)):
    """List knowledge-base files currently available to chat and quizzes."""
    files = []
    for path in knowledge_base_path().rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append({
                "filename": path.name,
                "path": str(path.relative_to(knowledge_base_path())),
                "type": path.suffix.lower().lstrip("."),
                "size": path.stat().st_size,
            })

    return {"total_documents": len(files), "documents": sorted(files, key=lambda item: item["path"])}


@router.get("/analytics")
async def get_analytics(db=Depends(get_db), _admin=Depends(require_admin)):
    chats_collection = db["chats"]
    quizzes_collection = db["quizzes"]
    users_collection = db["users"]

    total_chats = chats_collection.count_documents({})
    total_quizzes = quizzes_collection.count_documents({})
    total_users = users_collection.count_documents({})
    chats = list(chats_collection.find({}, sort=[("created_at", -1)]))
    quizzes = list(quizzes_collection.find({}, sort=[("created_at", -1)]))

    return {
        "total_users": total_users,
        "total_chats": total_chats,
        "total_quizzes": total_quizzes,
        "knowledge_documents": len(_list_knowledge_documents()["documents"]),
        "chat_subjects": _count_by_field(chats, "subject"),
        "quiz_subjects": _count_by_field(quizzes, "subject"),
        "recent_chats": [
            {
                "id": str(chat["_id"]),
                "subject": chat.get("subject"),
                "question": chat.get("question"),
                "created_at": chat.get("created_at"),
            }
            for chat in chats[:5]
        ],
        "recent_quizzes": [
            {
                "id": str(quiz["_id"]),
                "subject": quiz.get("subject"),
                "topic": quiz.get("topic"),
                "score": quiz.get("score"),
                "created_at": quiz.get("created_at"),
            }
            for quiz in quizzes[:5]
        ],
    }


def _count_by_field(documents: list[dict], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for document in documents:
        value = document.get(field) or "Unknown"
        counts[value] = counts.get(value, 0) + 1
    return counts


def _list_knowledge_documents():
    files = []
    base_path = knowledge_base_path()
    for path in base_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append({
                "filename": path.name,
                "path": str(path.relative_to(base_path)),
                "type": path.suffix.lower().lstrip("."),
                "size": path.stat().st_size,
            })

    return {"total_documents": len(files), "documents": sorted(files, key=lambda item: item["path"])}

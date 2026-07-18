from fastapi import APIRouter, Depends, HTTPException, status
from bson.objectid import ObjectId
from app.models.chat import ChatMessage, ChatResponse
from app.database.mongodb import get_database
from app.auth.jwt_handler import decode_access_token
import datetime

router = APIRouter()

def get_db():
    return get_database()

def get_current_user(token: str):
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return user_id

@router.post("/send", response_model=ChatResponse)
async def send_chat(message: ChatMessage, db=Depends(get_db)):
    chats_collection = db["chats"]
    
    # Create chat document
    chat_doc = {
        "user_id": message.user_id,
        "question": message.question,
        "answer": "This is a placeholder response. Integration with OpenAI will be done in Phase 2.",
        "subject": message.subject,
        "created_at": datetime.datetime.utcnow()
    }
    
    result = chats_collection.insert_one(chat_doc)
    
    return ChatResponse(
        id=str(result.inserted_id),
        user_id=message.user_id,
        question=message.question,
        answer=chat_doc["answer"],
        subject=message.subject,
        created_at=chat_doc["created_at"]
    )

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, db=Depends(get_db)):
    chats_collection = db["chats"]
    
    chats = list(chats_collection.find(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    ))
    
    return [
        {
            "id": str(chat["_id"]),
            "question": chat["question"],
            "answer": chat["answer"],
            "subject": chat["subject"],
            "created_at": chat["created_at"]
        }
        for chat in chats
    ]

@router.delete("/history/{chat_id}")
async def delete_chat(chat_id: str, db=Depends(get_db)):
    chats_collection = db["chats"]
    result = chats_collection.delete_one({"_id": ObjectId(chat_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return {"message": "Chat deleted successfully"}

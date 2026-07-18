from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from bson.objectid import ObjectId
from app.models.chat import ChatMessage, ChatResponse
from app.database.mongodb import get_database
from app.auth.jwt_handler import get_current_user_id
from app.chatbot.openai_service import get_ai_response, stream_ai_response
from app.rag.rag_service import retrieve_relevant_context
import datetime
import json

router = APIRouter()

def get_db():
    return get_database()

@router.post("/send", response_model=ChatResponse)
async def send_chat(
    message: ChatMessage,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    _validate_chat_message(message)
    _ensure_user_owns_resource(message.user_id, current_user_id)

    chats_collection = db["chats"]
    created_at = datetime.datetime.utcnow()
    context = retrieve_relevant_context(message.question, message.subject)
    answer = get_ai_response(message.question, message.subject, context)

    # Create chat document
    chat_doc = {
        "user_id": message.user_id,
        "question": message.question,
        "answer": answer,
        "subject": message.subject,
        "created_at": created_at
    }

    result = chats_collection.insert_one(chat_doc)

    return ChatResponse(
        id=str(result.inserted_id),
        user_id=message.user_id,
        question=message.question,
        answer=answer,
        subject=message.subject,
        created_at=created_at
    )


@router.post("/stream")
async def stream_chat(
    message: ChatMessage,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    _validate_chat_message(message)
    _ensure_user_owns_resource(message.user_id, current_user_id)

    def event_stream():
        answer_parts = []
        created_at = datetime.datetime.utcnow()

        try:
            context = retrieve_relevant_context(message.question, message.subject)
            for chunk in stream_ai_response(message.question, message.subject, context):
                answer_parts.append(chunk)
                yield _json_line({"type": "chunk", "chunk": chunk})

            answer = "".join(answer_parts)
            chat_doc = {
                "user_id": message.user_id,
                "question": message.question,
                "answer": answer,
                "subject": message.subject,
                "created_at": created_at
            }
            result = db["chats"].insert_one(chat_doc)
            yield _json_line({
                "type": "done",
                "message": {
                    "id": str(result.inserted_id),
                    "user_id": message.user_id,
                    "question": message.question,
                    "answer": answer,
                    "subject": message.subject,
                    "created_at": created_at.isoformat(),
                },
            })
        except Exception as exc:
            yield _json_line({"type": "error", "error": str(exc)})

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _validate_chat_message(message: ChatMessage):
    if not message.user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is required"
        )

    if not message.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required"
        )


def _json_line(payload: dict) -> str:
    return json.dumps(payload, default=str) + "\n"

@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    _ensure_user_owns_resource(user_id, current_user_id)
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
async def delete_chat(
    chat_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if not ObjectId.is_valid(chat_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chat ID"
        )

    chats_collection = db["chats"]
    result = chats_collection.delete_one({"_id": ObjectId(chat_id), "user_id": current_user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return {"message": "Chat deleted successfully"}

def _ensure_user_owns_resource(resource_user_id: str, current_user_id: str):
    if resource_user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own chats",
        )

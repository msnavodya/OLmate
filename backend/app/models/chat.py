from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatMessage(BaseModel):
    user_id: str
    question: str
    subject: str
    class Config:
        str_strip_whitespace = True

class ChatResponse(BaseModel):
    id: Optional[str] = None
    user_id: str
    question: str
    answer: str
    subject: str
    created_at: Optional[datetime] = None

class ChatHistory(BaseModel):
    id: Optional[str] = None
    user_id: str
    question: str
    answer: str
    subject: str
    created_at: Optional[datetime] = None

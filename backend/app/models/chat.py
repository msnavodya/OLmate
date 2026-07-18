from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ChatMessage(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str
    question: str
    subject: str

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

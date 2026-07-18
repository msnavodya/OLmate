from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuizRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str
    subject: str
    topic: str = ""
    question_count: int = Field(default=5, ge=3, le=10)


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_option: int
    explanation: str


class QuizResponse(BaseModel):
    id: Optional[str] = None
    user_id: str
    subject: str
    topic: str
    questions: List[QuizQuestion]
    created_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    score: Optional[int] = None


class QuizSubmission(BaseModel):
    user_id: str
    answers: Dict[str, int]


class QuizSubmissionResult(BaseModel):
    quiz_id: str
    score: int
    total: int
    answers: Dict[str, int]
    correct_answers: Dict[str, int]
    submitted_at: datetime

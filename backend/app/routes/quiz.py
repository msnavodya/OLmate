from datetime import datetime
from random import Random
from typing import Dict, List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt_handler import get_current_user_id
from app.database.mongodb import get_database
from app.models.quiz import QuizQuestion, QuizRequest, QuizResponse, QuizSubmission, QuizSubmissionResult
from app.rag.rag_service import retrieve_relevant_context

router = APIRouter()


def get_db():
    return get_database()


SUBJECT_QUESTIONS: Dict[str, List[dict]] = {
    "Science": [
        {
            "question": "Which substance in leaves absorbs light energy for photosynthesis?",
            "options": ["Chlorophyll", "Haemoglobin", "Starch", "Calcium carbonate"],
            "correct_option": 0,
            "explanation": "Chlorophyll is the green pigment that absorbs light energy in leaves.",
        },
        {
            "question": "What gas is released as a by-product of photosynthesis?",
            "options": ["Carbon dioxide", "Oxygen", "Nitrogen", "Hydrogen"],
            "correct_option": 1,
            "explanation": "Plants release oxygen when they make glucose using carbon dioxide and water.",
        },
        {
            "question": "Which part of the cell controls most cell activities?",
            "options": ["Cell wall", "Vacuole", "Nucleus", "Cytoplasm"],
            "correct_option": 2,
            "explanation": "The nucleus contains genetic material and controls cell activities.",
        },
    ],
    "Mathematics": [
        {
            "question": "What is the value of 3x + 4 when x = 2?",
            "options": ["6", "8", "10", "14"],
            "correct_option": 2,
            "explanation": "Substitute x = 2: 3 x 2 + 4 = 10.",
        },
        {
            "question": "What is the perimeter of a square with side length 7 cm?",
            "options": ["14 cm", "21 cm", "28 cm", "49 cm"],
            "correct_option": 2,
            "explanation": "A square has four equal sides, so perimeter = 4 x 7 = 28 cm.",
        },
        {
            "question": "Which number is a prime number?",
            "options": ["1", "9", "15", "17"],
            "correct_option": 3,
            "explanation": "17 has exactly two factors: 1 and 17.",
        },
    ],
    "English": [
        {
            "question": "Choose the correct verb: She ___ to school every day.",
            "options": ["go", "goes", "going", "gone"],
            "correct_option": 1,
            "explanation": "With the singular subject 'She', the simple present verb is 'goes'.",
        },
        {
            "question": "Which word is an adjective?",
            "options": ["quickly", "beautiful", "run", "under"],
            "correct_option": 1,
            "explanation": "An adjective describes a noun; 'beautiful' can describe a person, place, or thing.",
        },
        {
            "question": "What is the opposite of 'ancient'?",
            "options": ["old", "modern", "early", "historic"],
            "correct_option": 1,
            "explanation": "'Modern' means present-day or recent, so it is the opposite of ancient.",
        },
    ],
    "History": [
        {
            "question": "Why are dates important in history answers?",
            "options": ["They replace explanations", "They show sequence and accuracy", "They make answers longer", "They are always enough for full marks"],
            "correct_option": 1,
            "explanation": "Dates help show when events happened and how one event led to another.",
        },
        {
            "question": "What should a cause-and-effect history answer include?",
            "options": ["Only names", "Only a map", "Reasons and results", "A poem"],
            "correct_option": 2,
            "explanation": "Cause-and-effect questions require both why something happened and what happened after.",
        },
    ],
    "ICT": [
        {
            "question": "Which device is mainly used to input text?",
            "options": ["Monitor", "Keyboard", "Speaker", "Printer"],
            "correct_option": 1,
            "explanation": "A keyboard is an input device used to enter text and commands.",
        },
        {
            "question": "What does CPU stand for?",
            "options": ["Central Processing Unit", "Computer Power Utility", "Control Program Unit", "Central Print Unit"],
            "correct_option": 0,
            "explanation": "CPU stands for Central Processing Unit, the main processor of a computer.",
        },
    ],
}

GENERIC_QUESTIONS = [
    {
        "question": "What is the best first step when answering an O/L {subject} question about {topic}?",
        "options": ["Write a clear definition", "Skip to the conclusion", "Copy the question only", "Use unrelated facts"],
        "correct_option": 0,
        "explanation": "A clear definition or direct answer helps the examiner see your main idea immediately.",
    },
    {
        "question": "Which answer style usually earns better marks in {subject}?",
        "options": ["One long paragraph without examples", "Key points with an example", "Only memorized phrases", "No subject keywords"],
        "correct_option": 1,
        "explanation": "Short key points plus a relevant example make your answer clearer and more exam-friendly.",
    },
    {
        "question": "How should you finish a short answer about {topic}?",
        "options": ["Add a final link to the question", "Introduce a new unrelated topic", "Leave the answer incomplete", "Repeat only the heading"],
        "correct_option": 0,
        "explanation": "A final linking sentence shows how your points answer the exact question.",
    },
]


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    if not request.user_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is required")
    _ensure_user_owns_resource(request.user_id, current_user_id)
    if not request.subject.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject is required")

    created_at = datetime.utcnow()
    topic = request.topic.strip() or "revision basics"
    context = retrieve_relevant_context(topic, request.subject, top_k=4)
    questions = _build_questions(request.subject, topic, request.question_count, context)
    quiz_doc = {
        "user_id": request.user_id,
        "subject": request.subject,
        "topic": topic,
        "questions": [question.model_dump() for question in questions],
        "created_at": created_at,
    }

    result = db["quizzes"].insert_one(quiz_doc)
    return QuizResponse(id=str(result.inserted_id), **quiz_doc)


@router.post("/{quiz_id}/submit", response_model=QuizSubmissionResult)
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmission,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    _ensure_user_owns_resource(submission.user_id, current_user_id)
    if not ObjectId.is_valid(quiz_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid quiz ID")

    quizzes_collection = db["quizzes"]
    quiz = quizzes_collection.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    if quiz["user_id"] != submission.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Quiz does not belong to this user")

    correct_answers = {
        question["id"]: question["correct_option"]
        for question in quiz["questions"]
    }
    score = sum(
        1 for question_id, correct_option in correct_answers.items()
        if submission.answers.get(question_id) == correct_option
    )
    submitted_at = datetime.utcnow()

    quizzes_collection.update_one(
        {"_id": ObjectId(quiz_id)},
        {"$set": {"answers": submission.answers, "score": score, "submitted_at": submitted_at}},
    )

    return QuizSubmissionResult(
        quiz_id=quiz_id,
        score=score,
        total=len(correct_answers),
        answers=submission.answers,
        correct_answers=correct_answers,
        submitted_at=submitted_at,
    )


@router.get("/history/{user_id}", response_model=List[QuizResponse])
async def get_quiz_history(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db=Depends(get_db),
):
    _ensure_user_owns_resource(user_id, current_user_id)
    quizzes = list(db["quizzes"].find({"user_id": user_id}, sort=[("created_at", -1)]))
    return [
        QuizResponse(
            id=str(quiz["_id"]),
            user_id=quiz["user_id"],
            subject=quiz["subject"],
            topic=quiz["topic"],
            questions=quiz["questions"],
            created_at=quiz.get("created_at"),
            submitted_at=quiz.get("submitted_at"),
            score=quiz.get("score"),
        )
        for quiz in quizzes
    ]


def _build_questions(subject: str, topic: str, question_count: int, context: str = "") -> List[QuizQuestion]:
    seed = f"{subject}:{topic}".lower()
    randomizer = Random(seed)
    raw_questions = _questions_from_context(subject, topic, context)
    raw_questions.extend(SUBJECT_QUESTIONS.get(subject, []))
    raw_questions.extend(
        {
            **question,
            "question": question["question"].format(subject=subject, topic=topic),
        }
        for question in GENERIC_QUESTIONS
    )
    randomizer.shuffle(raw_questions)

    selected = raw_questions[:question_count]
    while len(selected) < question_count:
        index = len(selected) + 1
        selected.append({
            "question": f"Which habit helps you improve in {subject} when revising {topic}?",
            "options": ["Practice and review mistakes", "Avoid past papers", "Ignore teacher feedback", "Guess every answer"],
            "correct_option": 0,
            "explanation": "Practice, correction, and reviewing mistakes build exam confidence.",
        })

    return [
        QuizQuestion(id=f"q{index + 1}", **question)
        for index, question in enumerate(selected)
    ]


def _questions_from_context(subject: str, topic: str, context: str) -> List[dict]:
    sentences = []
    for line in context.splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith(("Source:", "Subject:")):
            continue
        for sentence in clean_line.split("."):
            clean_sentence = sentence.strip()
            if 45 <= len(clean_sentence) <= 180:
                sentences.append(clean_sentence)
            if len(sentences) >= 3:
                break
        if len(sentences) >= 3:
            break

    questions = []
    for sentence in sentences:
        questions.append({
            "question": f"According to the OL Mate knowledge base, which statement about {topic} is correct?",
            "options": [
                sentence,
                f"{subject} answers should ignore the main keywords.",
                "A good answer should use unrelated facts first.",
                f"{topic} cannot be explained with examples.",
            ],
            "correct_option": 0,
            "explanation": sentence,
        })
    return questions


def _ensure_user_owns_resource(resource_user_id: str, current_user_id: str):
    if resource_user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own quizzes",
        )

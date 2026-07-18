"""Tutor response generation for OL Mate.

Uses OpenAI when a real API key is configured. Otherwise it falls back to a
deterministic local tutor so the development web app remains fully usable.
"""

from __future__ import annotations

import re
import time
from typing import Iterable

from config import settings

SYSTEM_PROMPT = '''
You are OL Mate, an AI tutor for Sri Lankan GCE Ordinary Level students.

Rules:
- Answer according to the Sri Lankan O/L syllabus.
- Use simple language suitable for students aged 15-17.
- Give step-by-step solutions for mathematics.
- Keep answers concise but clear.
- If unsure, say you are not certain.
- Do not provide unrelated information.
'''

SUBJECT_FOCUS = {
    "Mathematics": "show formulas, substitutions, and the final answer clearly",
    "Science": "connect ideas to definitions, observations, and simple examples",
    "English": "explain meaning, grammar, vocabulary, and exam writing technique",
    "Sinhala": "focus on language use, meaning, grammar, and literature context",
    "Tamil": "focus on language use, meaning, grammar, and literature context",
    "History": "explain causes, events, people, dates, and effects in order",
    "Buddhism": "explain the teaching, value, example, and daily-life application",
    "Christianity": "explain the teaching, value, example, and daily-life application",
    "Islam": "explain the teaching, value, example, and daily-life application",
    "Hinduism": "explain the teaching, value, example, and daily-life application",
    "ICT": "define the term, show how it works, and give a practical example",
    "Commerce": "explain the business idea, purpose, example, and exam keywords",
    "Geography": "explain the process, place factors, maps, and human impact",
    "Civic Education": "explain the citizen role, institution, rights, and responsibilities",
}

QUICK_TOPICS = {
    "photosynthesis": (
        "Photosynthesis is the process where green plants make glucose using sunlight, carbon dioxide, and water.",
        [
            "Chlorophyll in leaves absorbs light energy.",
            "Carbon dioxide enters through stomata, and water comes from roots.",
            "Glucose is used for energy and growth; oxygen is released as a by-product.",
        ],
        "Equation: carbon dioxide + water -> glucose + oxygen, in the presence of light and chlorophyll.",
    ),
    "quadratic": (
        "A quadratic equation has the form ax^2 + bx + c = 0, where a is not zero.",
        [
            "Try factorisation first if the numbers are simple.",
            "If it cannot be factorised easily, use x = (-b +/- sqrt(b^2 - 4ac)) / 2a.",
            "Always substitute your answers back into the original equation to check.",
        ],
        "Example: x^2 - 5x + 6 = 0 -> (x - 2)(x - 3) = 0, so x = 2 or x = 3.",
    ),
    "world war i": (
        "World War I began in 1914 after long-term tension between European powers and the assassination of Archduke Franz Ferdinand.",
        [
            "Militarism increased competition in armies and weapons.",
            "Alliances turned a local conflict into a wider war.",
            "Imperial rivalry and nationalism created distrust between countries.",
        ],
        "A strong answer should separate long-term causes from the immediate trigger.",
    ),
}

def get_ai_response(question: str, subject: str, context: str = "") -> str:
    """Return a study-friendly answer for the given question."""
    clean_question = " ".join(question.split())
    clean_subject = subject.strip() or "General"

    if _has_real_openai_key():
        response = _get_openai_response(clean_question, clean_subject, context)
        if response:
            return response

    return _get_local_tutor_response(clean_question, clean_subject, context)


def stream_ai_response(question: str, subject: str, context: str = "") -> Iterable[str]:
    """Yield tutor answer chunks for a ChatGPT-like typing experience."""
    clean_question = " ".join(question.split())
    clean_subject = subject.strip() or "General"

    if _has_real_openai_key():
        try:
            yielded_content = False
            for chunk in _stream_openai_response(clean_question, clean_subject, context):
                yielded_content = True
                yield chunk
            if yielded_content:
                return
        except Exception as exc:
            print(f"[WARNING] OpenAI stream failed, using local tutor: {exc}")

    yield from _chunk_text(_get_local_tutor_response(clean_question, clean_subject, context))


def _has_real_openai_key() -> bool:
    key = settings.OPENAI_API_KEY.strip()
    return bool(key and not key.startswith("sk-your") and "your-openai" not in key)


def _get_openai_response(question: str, subject: str, context: str) -> str | None:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Subject: {subject}\n"
                    f"Context: {context or 'No extra context'}\n"
                    f"Question: {question}"
                ),
            },
        ]
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=700,
        )
        return completion.choices[0].message.content
    except Exception as exc:
        print(f"[WARNING] OpenAI response failed, using local tutor: {exc}")
        return None


def _stream_openai_response(question: str, subject: str, context: str) -> Iterable[str]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Subject: {subject}\n"
                f"Context: {context or 'No extra context'}\n"
                f"Question: {question}"
            ),
        },
    ]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=700,
        stream=True,
    )

    for event in completion:
        token = event.choices[0].delta.content
        if token:
            yield token


def _get_local_tutor_response(question: str, subject: str, context: str = "") -> str:
    lower_question = question.lower()
    focus = SUBJECT_FOCUS.get(subject, "explain the idea with simple steps and an exam-friendly example")
    context_points = _extract_context_points(context)

    topic_response = _match_topic(lower_question)
    if topic_response:
        summary, points, example = topic_response
        points = [*context_points[:2], *points] if context_points else points
        return _format_response(subject, question, summary, points, example, focus)

    math_response = _try_simple_math(lower_question)
    if subject == "Mathematics" and math_response:
        summary, points, example = math_response
        points = [*context_points[:2], *points] if context_points else points
        return _format_response(subject, question, summary, points, example, focus)

    if context_points:
        summary = (
            f"For O/L {subject}, the useful knowledge for this question is: {context_points[0]}"
        )
        points = [
            *context_points[:4],
            "Connect these points directly to the wording of the question.",
        ]
    else:
        summary = (
            f"For O/L {subject}, this question is asking you to explain the main idea clearly, "
            "then support it with points that an examiner can follow."
        )
        points = [
            f"Start with a short definition or direct answer for: {question}",
            f"Use the {subject} keywords your teacher would expect.",
            f"Add one example, reason, or step so the answer is not just memorized wording.",
            "Finish with a check sentence that links back to the question.",
        ]
    example = (
        "Revision pattern: Definition -> 2 or 3 key points -> example -> final link to the question."
    )
    return _format_response(subject, question, summary, points, example, focus)


def _extract_context_points(context: str) -> list[str]:
    if not context:
        return []

    points = []
    for line in context.splitlines():
        clean_line = line.strip()
        if not clean_line or clean_line.startswith(("Source:", "Subject:")):
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", clean_line):
            clean_sentence = sentence.strip(" -")
            if len(clean_sentence) >= 35:
                points.append(clean_sentence)
            if len(points) >= 4:
                return points
    return points


def _match_topic(lower_question: str) -> tuple[str, list[str], str] | None:
    for keyword, response in QUICK_TOPICS.items():
        if keyword in lower_question:
            return response
    return None


def _try_simple_math(lower_question: str) -> tuple[str, list[str], str] | None:
    expression = _extract_arithmetic_expression(lower_question)
    if not expression:
        return None

    try:
        value = eval(expression, {"__builtins__": {}}, {})
    except Exception:
        return None

    return (
        f"The value of {expression} is {value}.",
        [
            "Apply brackets first if there are any.",
            "Then complete multiplication and division from left to right.",
            "Finally complete addition and subtraction from left to right.",
        ],
        f"So, {expression} = {value}.",
    )


def _extract_arithmetic_expression(text: str) -> str | None:
    match = re.search(r"[-+*/().\d\s]{3,}", text)
    if not match:
        return None

    expression = match.group(0).strip()
    if not re.fullmatch(r"[-+*/().\d\s]+", expression):
        return None
    if not any(operator in expression for operator in ("+", "-", "*", "/")):
        return None
    return expression


def _chunk_text(text: str) -> Iterable[str]:
    words = text.split(" ")
    for index, word in enumerate(words):
        suffix = " " if index < len(words) - 1 else ""
        yield f"{word}{suffix}"
        time.sleep(0.012)


def _format_response(
    subject: str,
    question: str,
    summary: str,
    points: Iterable[str],
    example: str,
    focus: str,
) -> str:
    bullet_points = "\n".join(f"- {point}" for point in points)
    return (
        f"### {subject} answer\n\n"
        f"**Question:** {question}\n\n"
        f"**Short answer:** {summary}\n\n"
        f"**Key points:**\n{bullet_points}\n\n"
        f"**Example / exam tip:** {example}\n\n"
        f"**How to write it in an exam:** {focus}."
    )

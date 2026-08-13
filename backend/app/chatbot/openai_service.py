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
- Answer the student's exact question first. Do not start with generic revision notes.
- Use the supplied context only when it clearly matches the question. Ignore unrelated context.
- Give step-by-step solutions for mathematics and calculations.
- For mathematics, format answers like ChatGPT: brief intro, display LaTeX equations,
  clear step headings, a boxed final answer, and a check or alternative method when useful.
- Use $$...$$ for display math and \\(...\\) for inline math.
- For theory subjects, use short sections: Direct answer, Explanation, Exam point.
- Keep answers concise but clear. Avoid long memorized lists unless the question asks for them.
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

    local_math_response = _try_local_math_first(clean_question, clean_subject)
    if local_math_response:
        return local_math_response

    if _has_real_openai_key():
        response = _get_openai_response(clean_question, clean_subject, context)
        if response:
            return response

    return _get_local_tutor_response(clean_question, clean_subject, context)


def stream_ai_response(question: str, subject: str, context: str = "") -> Iterable[str]:
    """Yield tutor answer chunks for a ChatGPT-like typing experience."""
    clean_question = " ".join(question.split())
    clean_subject = subject.strip() or "General"

    local_math_response = _try_local_math_first(clean_question, clean_subject)
    if local_math_response:
        yield from _chunk_text(local_math_response)
        return

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


def _try_local_math_first(question: str, subject: str) -> str | None:
    """Prefer deterministic working for equations the local solver understands."""
    if subject != "Mathematics":
        return None

    return _try_worked_math_solution(question)


def _has_real_openai_key() -> bool:
    key = settings.OPENAI_API_KEY.strip()
    return bool(key and not key.startswith("sk-your") and "your-openai" not in key)


def _get_openai_response(question: str, subject: str, context: str) -> str | None:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(question, subject, context)},
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
        {"role": "user", "content": _build_user_prompt(question, subject, context)},
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


def _build_user_prompt(question: str, subject: str, context: str) -> str:
    return (
        f"Subject: {subject}\n"
        f"Student question: {question}\n\n"
        "Relevant syllabus context, if useful:\n"
        f"{context or 'No extra context'}\n\n"
        "Answer instructions:\n"
        "- Solve or answer this exact question.\n"
        "- If the context is unrelated, ignore it completely.\n"
        "- Do not mention percentages, ratios, or other topics unless the question asks for them.\n"
        "- For math, show clean working and finish with a boxed final answer."
    )


def _get_local_tutor_response(question: str, subject: str, context: str = "") -> str:
    lower_question = question.lower()
    focus = SUBJECT_FOCUS.get(subject, "explain the idea with simple steps and an exam-friendly example")
    context_points = _extract_context_points(context, question)

    if subject == "Mathematics":
        worked_math_response = _try_worked_math_solution(question)
        if worked_math_response:
            return worked_math_response

    topic_response = _match_topic(lower_question)
    if topic_response:
        summary, points, example = topic_response
        points = [*context_points[:2], *points] if context_points else points
        return _format_response(subject, question, summary, points, example, focus)

    math_response = _try_simple_math(lower_question)
    if subject == "Mathematics" and math_response:
        expression, value = math_response
        return _format_arithmetic_solution(expression, value)

    if context_points:
        summary = _make_direct_context_summary(subject, question, context_points[0])
        points = _unique_points(context_points[:4])
        example = _context_exam_tip(subject)
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


def _extract_context_points(context: str, question: str = "") -> list[str]:
    if not context:
        return []

    question_terms = _tokenize_for_matching(question)
    definition_term = _extract_definition_term(question)
    scored_points = []
    fallback_points = []

    for line in context.splitlines():
        clean_line = _clean_context_line(line)
        if not clean_line or clean_line.startswith(("Source:", "Subject:")):
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", clean_line):
            clean_sentence = _clean_context_sentence(sentence)
            if len(clean_sentence) < 20 or "answers should" in clean_sentence.lower():
                continue

            score = len(question_terms.intersection(_tokenize_for_matching(clean_sentence)))
            if definition_term and _sentence_defines_term(clean_sentence, definition_term):
                score += 4
            if score > 0:
                scored_points.append((score, clean_sentence))
            elif len(fallback_points) < 4:
                fallback_points.append(clean_sentence)

    scored_points.sort(key=lambda item: item[0], reverse=True)
    points = [point for _, point in scored_points[:4]]
    if len(points) < 2:
        points.extend(fallback_points[: 4 - len(points)])
    return points[:4]


def _clean_context_line(line: str) -> str:
    clean_line = line.strip()
    clean_line = re.sub(r"#+\s*", "", clean_line)
    clean_line = re.sub(r"\b[A-Za-z ]+ Knowledge Base\b", "", clean_line)
    clean_line = re.sub(r"\bExam Answer Pattern\b", "", clean_line)
    return re.sub(r"\s+", " ", clean_line).strip()


def _clean_context_sentence(sentence: str) -> str:
    clean_sentence = sentence.strip(" -")
    clean_sentence = re.sub(r"^#+\s*", "", clean_sentence)
    clean_sentence = re.sub(r"^(Biology|Chemistry|Physics|Computer System|Business Basics)\b\s*", "", clean_sentence)
    return re.sub(r"\s+", " ", clean_sentence).strip()


def _tokenize_for_matching(text: str) -> set[str]:
    stopwords = {
        "about", "answer", "are", "can", "define", "explain", "for", "give",
        "how", "is", "main", "meaning", "of", "ol", "question", "the", "this",
        "to", "use", "what", "when", "where", "why", "with",
    }
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(token) > 2 and token not in stopwords
    }


def _make_direct_context_summary(subject: str, question: str, best_point: str) -> str:
    if re.search(r"\b(what is|define|meaning of)\b", question.lower()):
        return best_point
    return f"For O/L {subject}, the key point is: {best_point}"


def _unique_points(points: list[str]) -> list[str]:
    unique = []
    seen = set()
    for point in points:
        key = point.lower()
        if key in seen:
            continue
        unique.append(point)
        seen.add(key)
    return unique


def _context_exam_tip(subject: str) -> str:
    if subject == "Mathematics":
        return "Show each calculation step clearly and box the final answer."
    if subject == "ICT":
        return "Write the definition first, then add its function and one practical example."
    if subject == "Science":
        return "State the idea, then add a process, equation, observation, or example."
    if subject == "Commerce":
        return "Give the meaning, purpose, and a real business example when possible."
    return "Start with the direct answer, then add two clear supporting points."


def _extract_definition_term(question: str) -> str:
    match = re.search(r"\b(?:what is|define|meaning of)\s+(?:a|an|the)?\s*([a-zA-Z0-9 ]+?)\??$", question.lower())
    if not match:
        return ""
    term = match.group(1).strip()
    return re.sub(r"\s+", " ", term)


def _sentence_defines_term(sentence: str, term: str) -> bool:
    lower_sentence = sentence.lower()
    escaped_term = re.escape(term)
    return bool(
        re.search(rf"\b{escaped_term}\b\s+(?:is|are|means|refers to)\b", lower_sentence)
        or re.search(rf"\bthe\s+{escaped_term}\b", lower_sentence)
    )


def _match_topic(lower_question: str) -> tuple[str, list[str], str] | None:
    for keyword, response in QUICK_TOPICS.items():
        if keyword in lower_question:
            return response
    return None


def _try_simple_math(lower_question: str) -> tuple[str, int | float] | None:
    expression = _extract_arithmetic_expression(lower_question)
    if not expression:
        return None

    try:
        value = eval(expression, {"__builtins__": {}}, {})
    except Exception:
        return None

    return expression, value


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


def _try_worked_math_solution(question: str) -> str | None:
    quadratic = _parse_quadratic_equation(question)
    if quadratic:
        return _format_quadratic_solution(*quadratic)

    linear = _parse_linear_equation(question)
    if linear:
        return _format_linear_solution(*linear)

    return None


def _parse_quadratic_equation(question: str) -> tuple[str, int, int, int] | None:
    normalized = _normalize_math_question(question)
    match = re.search(r"[-+x^0-9\s]+=[-+x^0-9\s]+", normalized)
    if not match:
        return None

    equation = match.group(0).strip()
    left, right = equation.split("=", 1)
    left_coeffs = _parse_polynomial(left)
    right_coeffs = _parse_polynomial(right)
    if left_coeffs is None or right_coeffs is None:
        return None

    a = left_coeffs[0] - right_coeffs[0]
    b = left_coeffs[1] - right_coeffs[1]
    c = left_coeffs[2] - right_coeffs[2]
    if a == 0:
        return None

    canonical = _format_equation(a, b, c)
    return canonical, a, b, c


def _parse_linear_equation(question: str) -> tuple[str, int, int] | None:
    normalized = _normalize_math_question(question)
    match = re.search(r"[-+x^0-9\s]+=[-+x^0-9\s]+", normalized)
    if not match:
        return None

    equation = match.group(0).strip()
    left, right = equation.split("=", 1)
    left_coeffs = _parse_polynomial(left)
    right_coeffs = _parse_polynomial(right)
    if left_coeffs is None or right_coeffs is None:
        return None

    a = left_coeffs[0] - right_coeffs[0]
    b = left_coeffs[1] - right_coeffs[1]
    c = left_coeffs[2] - right_coeffs[2]
    if a != 0 or b == 0:
        return None

    canonical = _format_linear_equation(b, c)
    return canonical, b, c


def _normalize_math_question(question: str) -> str:
    normalized = (
        question.lower()
        .replace("−", "-")
        .replace("²", "^2")
        .replace("**", "^")
    )
    return re.sub(r"\bx\s+2\b", "x^2", normalized)


def _parse_polynomial(expression: str) -> tuple[int, int, int] | None:
    compact = expression.replace(" ", "")
    if not compact or not re.fullmatch(r"[-+x^0-9]+", compact):
        return None

    if compact[0] not in "+-":
        compact = f"+{compact}"

    a = b = c = 0
    for term in re.findall(r"[+-][^+-]+", compact):
        sign = -1 if term[0] == "-" else 1
        body = term[1:]

        if "x^2" in body:
            coefficient = body.replace("x^2", "")
            a += sign * _parse_coefficient(coefficient)
        elif "x" in body:
            coefficient = body.replace("x", "")
            b += sign * _parse_coefficient(coefficient)
        elif body.isdigit():
            c += sign * int(body)
        else:
            return None

    return a, b, c


def _parse_coefficient(value: str) -> int:
    if value == "":
        return 1
    return int(value)


def _format_quadratic_solution(equation: str, a: int, b: int, c: int) -> str:
    if a == 1 and b == 0 and c < 0:
        root_square = -c / a
        if root_square > 0 and root_square.is_integer():
            root_value = int(root_square ** 0.5)
            if root_value * root_value == int(root_square):
                return _format_difference_of_squares_solution(equation, root_value)

    roots = _integer_quadratic_roots(a, b, c)
    if a == 1 and roots:
        first, second = roots
        factors = _factor_pair_for_roots(first, second)
        return (
            f"To solve:\n\n"
            f"$$\n{equation}\n$$\n\n"
            f"### Step 1: Factor the quadratic\n\n"
            f"$$\n{equation.replace(' = 0', '')} = {factors}\n$$\n\n"
            f"### Step 2: Set each factor equal to zero\n\n"
            f"- \\(x {'-' if first >= 0 else '+'} {abs(first)} = 0 \\Rightarrow x = {first}\\)\n"
            f"- \\(x {'-' if second >= 0 else '+'} {abs(second)} = 0 \\Rightarrow x = {second}\\)\n\n"
            f"### Final Answer\n\n"
            f"$$\n\\boxed{{x = {first} \\text{{ or }} x = {second}}}\n$$"
        )

    return _format_quadratic_formula_solution(equation, a, b, c)


def _format_difference_of_squares_solution(equation: str, root_value: int) -> str:
    return (
        f"To solve:\n\n"
        f"$$\n{equation}\n$$\n\n"
        f"### Step 1: Move the constant to the other side\n\n"
        f"$$\nx^2 = {root_value ** 2}\n$$\n\n"
        f"### Step 2: Take the square root of both sides\n\n"
        f"$$\nx = \\pm \\sqrt{{{root_value ** 2}}}\n$$\n\n"
        f"$$\nx = \\pm {root_value}\n$$\n\n"
        f"### Final Answer\n\n"
        f"$$\n\\boxed{{x = {root_value} \\text{{ or }} x = -{root_value}}}\n$$\n\n"
        f"### Alternative Method: Factorization\n\n"
        f"$$\n{equation}\n$$\n\n"
        f"This is a **difference of squares**:\n\n"
        f"$$\n(x + {root_value})(x - {root_value}) = 0\n$$\n\n"
        f"Set each factor equal to zero:\n\n"
        f"- \\(x + {root_value} = 0 \\Rightarrow x = -{root_value}\\)\n"
        f"- \\(x - {root_value} = 0 \\Rightarrow x = {root_value}\\)\n\n"
        f"**Answer:**\n\n"
        f"$$\n\\boxed{{x = -{root_value},\\; {root_value}}}\n$$"
    )


def _format_linear_solution(equation: str, b: int, c: int) -> str:
    moved_constant = -c
    answer = moved_constant / b
    answer_text = _format_number(answer)

    return (
        f"To solve:\n\n"
        f"$$\n{equation}\n$$\n\n"
        f"### Step 1: Move the constant term\n\n"
        f"$$\n{_format_polynomial_term(b, 'x', is_first=True)} = {moved_constant}\n$$\n\n"
        f"### Step 2: Divide by the coefficient of \\(x\\)\n\n"
        f"$$\nx = \\frac{{{moved_constant}}}{{{b}}}\n$$\n\n"
        f"$$\nx = {answer_text}\n$$\n\n"
        f"### Final Answer\n\n"
        f"$$\n\\boxed{{x = {answer_text}}}\n$$"
    )


def _format_quadratic_formula_solution(equation: str, a: int, b: int, c: int) -> str:
    discriminant = b * b - 4 * a * c
    return (
        f"To solve:\n\n"
        f"$$\n{equation}\n$$\n\n"
        f"### Step 1: Identify \\(a\\), \\(b\\), and \\(c\\)\n\n"
        f"$$\na = {a},\\quad b = {b},\\quad c = {c}\n$$\n\n"
        f"### Step 2: Use the quadratic formula\n\n"
        f"$$\nx = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}\n$$\n\n"
        f"### Step 3: Substitute the values\n\n"
        f"$$\nx = \\frac{{-{b} \\pm \\sqrt{{{b}^2 - 4({a})({c})}}}}{{2({a})}}\n$$\n\n"
        f"$$\nx = \\frac{{{-b} \\pm \\sqrt{{{discriminant}}}}}{{{2 * a}}}\n$$\n\n"
        f"### Final Answer\n\n"
        f"$$\n\\boxed{{x = \\frac{{{-b} \\pm \\sqrt{{{discriminant}}}}}{{{2 * a}}}}}\n$$"
    )


def _format_arithmetic_solution(expression: str, value: int | float) -> str:
    value_text = _format_number(value)

    return (
        f"To calculate:\n\n"
        f"$$\n{expression} = ?\n$$\n\n"
        f"### Step 1: Use the order of operations\n\n"
        "Complete brackets first, then multiplication/division, then addition/subtraction.\n\n"
        f"### Step 2: Simplify\n\n"
        f"$$\n{expression} = {value_text}\n$$\n\n"
        f"### Final Answer\n\n"
        f"$$\n\\boxed{{{value_text}}}\n$$"
    )


def _integer_quadratic_roots(a: int, b: int, c: int) -> tuple[int, int] | None:
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return None

    sqrt_discriminant = int(discriminant ** 0.5)
    if sqrt_discriminant * sqrt_discriminant != discriminant:
        return None

    denominator = 2 * a
    first_numerator = -b + sqrt_discriminant
    second_numerator = -b - sqrt_discriminant
    if first_numerator % denominator != 0 or second_numerator % denominator != 0:
        return None

    first = first_numerator // denominator
    second = second_numerator // denominator
    return first, second


def _factor_pair_for_roots(first: int, second: int) -> str:
    first_sign = "-" if first >= 0 else "+"
    second_sign = "-" if second >= 0 else "+"
    return f"(x {first_sign} {abs(first)})(x {second_sign} {abs(second)})"


def _format_equation(a: int, b: int, c: int) -> str:
    terms = [_format_polynomial_term(a, "x^2", is_first=True)]
    if b:
        terms.append(_format_polynomial_term(b, "x"))
    if c:
        terms.append(_format_polynomial_term(c, ""))
    return f"{''.join(terms)} = 0"


def _format_linear_equation(b: int, c: int) -> str:
    terms = [_format_polynomial_term(b, "x", is_first=True)]
    if c:
        terms.append(_format_polynomial_term(c, ""))
    return f"{''.join(terms)} = 0"


def _format_polynomial_term(coefficient: int, variable: str, is_first: bool = False) -> str:
    sign = "-" if coefficient < 0 else "+"
    abs_coefficient = abs(coefficient)
    value = variable if abs_coefficient == 1 and variable else f"{abs_coefficient}{variable}"

    if is_first:
        return f"-{value}" if coefficient < 0 else value

    return f" {sign} {value}"


def _format_number(value: int | float) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


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
        f"### {subject} Answer\n\n"
        f"**Question:** {question}\n\n"
        f"**Direct answer:** {summary}\n\n"
        f"**Explanation:**\n{bullet_points}\n\n"
        f"**Example / exam tip:** {example}\n\n"
        f"**Exam point:** {focus}."
    )

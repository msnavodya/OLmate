from app.chatbot.openai_service import get_ai_response
from app.chatbot import openai_service
from app.rag.rag_service import retrieve_relevant_context


def test_math_quadratic_answer_uses_worked_latex_format():
    answer = get_ai_response("Solve x^2 - 9 = 0", "Mathematics")

    assert "### Step 1" in answer
    assert "### Final Answer" in answer
    assert "$$" in answer
    assert "\\boxed{x = -3,\\; 3}" in answer
    assert "difference of squares" in answer.lower()


def test_math_quadratic_answer_handles_spaced_square_notation():
    answer = get_ai_response("Solve: x 2 -9=0", "Mathematics")

    assert "**Short answer:**" not in answer
    assert "$$\nx^2 - 9 = 0\n$$" in answer
    assert "\\boxed{x = -3,\\; 3}" in answer


def test_math_quadratic_answer_does_not_defer_to_openai(monkeypatch):
    monkeypatch.setattr(openai_service.settings, "OPENAI_API_KEY", "sk-real-looking-key")

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("OpenAI should not be called for supported math equations")

    monkeypatch.setattr(openai_service, "_get_openai_response", fail_if_called)

    answer = get_ai_response("Solve: x 2 -9=0", "Mathematics")

    assert "To increase by a percentage" not in answer
    assert "$$\nx^2 - 9 = 0\n$$" in answer
    assert "\\boxed{x = -3,\\; 3}" in answer


def test_math_linear_equation_uses_worked_solution():
    answer = get_ai_response("Solve 2x + 3 = 11", "Mathematics")

    assert "**Short answer:**" not in answer
    assert "$$\n2x - 8 = 0\n$$" in answer
    assert "\\boxed{x = 4}" in answer


def test_math_arithmetic_uses_worked_solution():
    answer = get_ai_response("Calculate 6 + 4 * 3", "Mathematics")

    assert "**Short answer:**" not in answer
    assert "### Final Answer" in answer
    assert "\\boxed{18}" in answer


def test_math_ratio_word_problem_uses_friendly_steps():
    answer = get_ai_response(
        "The ratio of boys to girls in a class is 3 : 5. If there are 40 students altogether, find the number of boys and girls.",
        "Mathematics",
    )

    assert "Question 1" in answer
    assert "**Step 1: Find the total number of parts**" in answer
    assert "3 + 5 = 8" in answer
    assert "40 \\div 8 = 5" in answer
    assert "3 \\times 5 = 15" in answer
    assert "5 \\times 5 = 25" in answer
    assert "**Answer: 15 boys and 25 girls**" in answer


def test_math_triangle_area_word_problem_uses_friendly_steps():
    answer = get_ai_response(
        "Find the area of a triangle with a base of 12 cm and height of 8 cm.",
        "Mathematics",
    )

    assert "Question 1" in answer
    assert "**Step 1: Use the formula**" in answer
    assert "\\frac{1}{2} \\times \\text{base} \\times \\text{height}" in answer
    assert "\\frac{1}{2} \\times 12 \\times 8" in answer
    assert "= 6 \\times 8" in answer
    assert "**Answer: 48 cm" in answer


def test_math_profit_percentage_word_problem_uses_friendly_steps_with_context():
    question = "A shopkeeper buys an item for Rs. 4,000 and sells it for Rs. 4,800. Find the percentage profit."
    context = retrieve_relevant_context(question, "Mathematics")

    answer = get_ai_response(question, "Mathematics", context)

    assert "Question 1" in answer
    assert "**Direct answer:**" not in answer
    assert "Business is an economic activity" not in answer
    assert "**Step 1: Find the profit**" in answer
    assert "4800 - 4000 = 800" in answer
    assert "\\frac{800}{4000} \\times 100" in answer
    assert "**Answer: 20% profit**" in answer


def test_symbolic_math_query_does_not_retrieve_unrelated_percentage_notes():
    context = retrieve_relevant_context("Solve x^2 - 9 = 0", "Mathematics")

    assert "To increase by a percentage" not in context


def test_context_answer_prefers_matching_ict_definition():
    question = "What is CPU?"
    context = retrieve_relevant_context(question, "ICT")

    answer = get_ai_response(question, "ICT", context)

    assert "The CPU processes instructions" in answer
    assert "For O/L ICT, this question is asking" not in answer


def test_context_answer_prefers_exact_definition_sentence():
    question = "What is capital?"
    context = retrieve_relevant_context(question, "Commerce")

    answer = get_ai_response(question, "Commerce", context)

    assert "Capital is the owner's investment" in answer
    assert "Direct answer: Land, labour, capital" not in answer

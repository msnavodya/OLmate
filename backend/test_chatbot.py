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

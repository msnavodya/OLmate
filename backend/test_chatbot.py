from app.chatbot.openai_service import get_ai_response


def test_math_quadratic_answer_uses_worked_latex_format():
    answer = get_ai_response("Solve x^2 - 9 = 0", "Mathematics")

    assert "### Step 1" in answer
    assert "### Final Answer" in answer
    assert "$$" in answer
    assert "\\boxed{x = -3,\\; 3}" in answer
    assert "difference of squares" in answer.lower()

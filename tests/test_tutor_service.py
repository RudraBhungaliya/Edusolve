"""
Unit tests for the TutorService orchestrator.
"""

from unittest.mock import MagicMock
import pytest
from services.exceptions import ValidationError
from services.groq_client import GroqService
from services.models import PracticeQuestion, StructuredAnswer, TutorResponse
from services.tutor_service import TutorService


@pytest.fixture
def mock_groq_service():
    """Create a mock GroqService fixture."""
    return MagicMock(spec=GroqService)


class TestTutorServiceDoubtSolving:
    """Tests for TutorService.solve_doubt."""

    def test_solve_doubt_success(self, mock_groq_service):
        ai_doubt_output = """
EXPLANATION:
Newton's First Law states that an object remains at rest or in uniform motion unless acted on by an external net force.

KEY FORMULA / FACT:
F_net = 0 implies acceleration a = 0 (Inertia).

REAL EXAMPLE:
When a bus stops suddenly, passengers lurch forward because of inertia.
"""
        practice_json_output = """
[
  {"question": "What is inertia?", "answer": "Resistance to change in motion.", "type": "short"},
  {"question": "If net force is zero, what is acceleration?", "answer": "Zero", "type": "mcq"},
  {"question": "Give one example of inertia of rest.", "answer": "Dust leaves a carpet when beaten.", "type": "short"}
]
"""
        # First call is doubt answer, second call is practice questions
        mock_groq_service.generate_chat_completion.side_effect = [
            ai_doubt_output,
            practice_json_output,
        ]

        service = TutorService(groq_service=mock_groq_service)
        response = service.solve_doubt(
            question="Explain Newton's First Law",
            subject="Science",
            grade=9,
        )

        assert isinstance(response, TutorResponse)
        assert response.success is True
        assert response.grade == 9
        assert response.subject == "Science"
        assert response.question == "Explain Newton's First Law"

        # Structured answer verified
        assert isinstance(response.structured_answer, StructuredAnswer)
        assert response.structured_answer.is_domain_match is True
        assert "Newton's First Law" in response.structured_answer.explanation
        assert "F_net = 0" in response.structured_answer.key_formula_fact
        assert "bus stops suddenly" in response.structured_answer.real_example

        # Practice questions verified
        assert len(response.practice_questions) == 3
        assert response.practice_questions[0].question == "What is inertia?"
        assert response.practice_questions[1].type == "mcq"

        # Legacy dict export test
        legacy = response.to_legacy_dict()
        assert "question" in legacy
        assert "subject" in legacy
        assert "grade" in legacy
        assert "answer" in legacy
        assert "practice_questions" in legacy
        assert "structured_answer" in legacy

    def test_solve_doubt_out_of_domain_skips_practice_questions(self, mock_groq_service):
        out_of_domain_reply = "I only help with Science and Maths doubts!"
        mock_groq_service.generate_chat_completion.return_value = out_of_domain_reply

        service = TutorService(groq_service=mock_groq_service)
        response = service.solve_doubt(
            question="Who won the Battle of Panipat?",
            subject="Science",  # Input claims science, but content is non-science
            grade=9,
        )

        assert response.success is True
        assert response.structured_answer.is_domain_match is False
        assert response.practice_questions == []
        # Groq should only be called once (no practice questions requested)
        assert mock_groq_service.generate_chat_completion.call_count == 1

    def test_solve_doubt_invalid_grade_raises_validation_error(self, mock_groq_service):
        service = TutorService(groq_service=mock_groq_service)
        with pytest.raises(ValidationError) as exc_info:
            service.solve_doubt(
                question="What is a cell?",
                subject="Science",
                grade=7,  # Invalid grade
            )
        assert exc_info.value.field == "grade"
        assert mock_groq_service.generate_chat_completion.call_count == 0

    def test_solve_doubt_invalid_subject_raises_validation_error(self, mock_groq_service):
        service = TutorService(groq_service=mock_groq_service)
        with pytest.raises(ValidationError) as exc_info:
            service.solve_doubt(
                question="Explain monetary policy",
                subject="Economics",
                grade=10,
            )
        assert exc_info.value.field == "subject"

    def test_solve_doubt_empty_question_raises_validation_error(self, mock_groq_service):
        service = TutorService(groq_service=mock_groq_service)
        with pytest.raises(ValidationError) as exc_info:
            service.solve_doubt(
                question="   ",
                subject="Maths",
                grade=10,
            )
        assert exc_info.value.field == "question"


class TestTutorServiceSafeVariant:
    """Tests for TutorService.solve_doubt_safe."""

    def test_safe_variant_returns_error_response_on_validation_failure(self, mock_groq_service):
        service = TutorService(groq_service=mock_groq_service)
        response = service.solve_doubt_safe(
            question="",
            subject="Science",
            grade=9,
        )
        assert response.success is False
        assert response.error is not None
        assert "empty" in response.error.lower()

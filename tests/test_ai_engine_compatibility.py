"""
Backward compatibility tests for ai_engine.py module-level functions.
"""

from unittest.mock import patch, MagicMock
import ai_engine


class TestAiEngineModuleCompatibility:
    """Ensure ai_engine module functions retain identical signatures and return structures."""

    @patch("ai_engine._tutor_service")
    def test_ask_doubt_delegation(self, mock_service):
        mock_service.ask_doubt_raw.return_value = "EXPLANATION:\nTest explanation"
        result = ai_engine.ask_doubt("What is speed?", "Science", 9)
        assert result == "EXPLANATION:\nTest explanation"
        mock_service.ask_doubt_raw.assert_called_once_with(
            question="What is speed?", subject="Science", grade=9
        )

    @patch("ai_engine._tutor_service")
    def test_get_practice_questions_delegation(self, mock_service):
        from services.models import PracticeQuestion
        mock_service.generate_practice_questions.return_value = [
            PracticeQuestion(question="Q1", answer="A1", type="mcq")
        ]
        result = ai_engine.get_practice_questions("Explanation text", "Maths", 10)
        assert len(result) == 1
        assert result[0] == {"question": "Q1", "answer": "A1", "type": "mcq"}

    @patch("ai_engine._tutor_service")
    def test_solve_doubt_delegation(self, mock_service):
        mock_response = MagicMock()
        mock_response.to_legacy_dict.return_value = {
            "question": "What is mass?",
            "subject": "Science",
            "grade": 9,
            "answer": "Mass is matter quantity.",
            "practice_questions": [],
            "structured_answer": {
                "explanation": "Mass is matter quantity.",
                "key_formula_fact": "N/A",
                "real_example": "N/A",
                "is_domain_match": True,
            },
        }
        mock_service.solve_doubt.return_value = mock_response

        result = ai_engine.solve_doubt("What is mass?", "Science", 9)
        assert result["question"] == "What is mass?"
        assert result["subject"] == "Science"
        assert result["grade"] == 9
        assert "practice_questions" in result

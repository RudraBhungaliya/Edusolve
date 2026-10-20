"""
Unit tests for structured answer and practice question parsers.
"""

from services.models import PracticeQuestion, StructuredAnswer
from services.parser import (
    clean_json_string,
    is_out_of_domain,
    parse_practice_questions,
    parse_structured_answer,
)


class TestStructuredAnswerParser:
    """Tests for parse_structured_answer."""

    def test_parse_standard_3_part_answer(self):
        raw_text = """
EXPLANATION:
Photosynthesis is the process by which green plants make their own food using sunlight, water, and carbon dioxide.

KEY FORMULA / FACT:
6CO2 + 6H2O + Sunlight -> C6H12O6 + 6O2

REAL EXAMPLE:
A plant kept in a dark room turns pale because it cannot perform photosynthesis without sunlight.
"""
        parsed = parse_structured_answer(raw_text)
        assert isinstance(parsed, StructuredAnswer)
        assert parsed.is_domain_match is True
        assert "green plants make their own food" in parsed.explanation
        assert "6CO2" in parsed.key_formula_fact
        assert "plant kept in a dark room" in parsed.real_example

    def test_parse_markdown_header_formatting(self):
        raw_text = """
**EXPLANATION:**
Ohm's Law states that current is proportional to voltage.

### KEY FORMULA / FACT:
V = I * R

**REAL LIFE EXAMPLE:**
Turning up the volume dial increases electrical resistance, lowering output current.
"""
        parsed = parse_structured_answer(raw_text)
        assert parsed.is_domain_match is True
        assert "Ohm's Law" in parsed.explanation
        assert "V = I * R" in parsed.key_formula_fact
        assert "volume dial" in parsed.real_example

    def test_parse_out_of_domain_rejection(self):
        raw_text = 'I only help with Science and Maths doubts!'
        parsed = parse_structured_answer(raw_text)
        assert parsed.is_domain_match is False
        assert "I only help with Science and Maths doubts!" in parsed.explanation
        assert parsed.key_formula_fact == "N/A"
        assert parsed.real_example == "N/A"

    def test_parse_empty_string(self):
        parsed = parse_structured_answer("")
        assert parsed.is_domain_match is True
        assert "No explanation was provided" in parsed.explanation

    def test_parse_missing_headers_graceful_fallback(self):
        raw_text = "Friction is a contact force that opposes the relative motion between two surfaces."
        parsed = parse_structured_answer(raw_text)
        assert parsed.is_domain_match is True
        assert "Friction is a contact force" in parsed.explanation
        assert parsed.key_formula_fact != ""
        assert parsed.real_example != ""


class TestPracticeQuestionsParser:
    """Tests for parse_practice_questions and clean_json_string."""

    def test_clean_json_string_with_markdown(self):
        raw = '```json\n[{"question": "Q1", "answer": "A1", "type": "mcq"}]\n```'
        cleaned = clean_json_string(raw)
        assert cleaned == '[{"question": "Q1", "answer": "A1", "type": "mcq"}]'

    def test_clean_json_string_removes_trailing_commas(self):
        raw = '[{"question": "Q1", "answer": "A1", "type": "short",},]'
        cleaned = clean_json_string(raw)
        assert cleaned == '[{"question": "Q1", "answer": "A1", "type": "short"}]'

    def test_parse_valid_questions(self):
        raw = """
[
  {"question": "What is the SI unit of force?", "answer": "Newton (N)", "type": "short"},
  {"question": "Which of the following is a vector quantity?", "answer": "Velocity", "type": "mcq"},
  {"question": "Define acceleration.", "answer": "Rate of change of velocity.", "type": "short"}
]
"""
        questions = parse_practice_questions(raw)
        assert len(questions) == 3
        assert isinstance(questions[0], PracticeQuestion)
        assert questions[0].question == "What is the SI unit of force?"
        assert questions[0].answer == "Newton (N)"
        assert questions[0].type == "short"
        assert questions[1].type == "mcq"

    def test_parse_malformed_json_returns_empty_list(self):
        raw = "Sorry, I could not generate JSON [unclosed array"
        questions = parse_practice_questions(raw)
        assert questions == []

    def test_parse_empty_input_returns_empty_list(self):
        assert parse_practice_questions("") == []
        assert parse_practice_questions("   ") == []


class TestDomainCheck:
    """Tests for is_out_of_domain helper."""

    def test_detects_out_of_domain_phrases(self):
        assert is_out_of_domain("I only help with Science and Maths doubts!") is True
        assert is_out_of_domain("Sorry, I only answer Science and Mathematics questions.") is True
        assert is_out_of_domain("Here is how gravity works:") is False

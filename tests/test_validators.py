"""
Unit tests for EduSolve input validation utilities.
"""

import pytest
from services.exceptions import ValidationError
from services.validators import (
    validate_doubt_input,
    validate_grade,
    validate_question,
    validate_subject,
)


class TestGradeValidation:
    """Tests for validate_grade function."""

    @pytest.mark.parametrize("valid_input,expected", [
        (9, 9),
        (10, 10),
        ("9", 9),
        ("10", 10),
        ("Class 9", 9),
        ("class 10", 10),
        ("Grade 9", 9),
        ("9th", 9),
        ("10th", 10),
        ("  10  ", 10),
    ])
    def test_valid_grades(self, valid_input, expected):
        assert validate_grade(valid_input) == expected

    @pytest.mark.parametrize("invalid_input", [
        8,
        11,
        "7",
        "12",
        "Class 8",
        "Grade 11",
        "",
        "   ",
        None,
        "kindergarten",
        "grade",
        True,  # booleans are ints in Python, should be rejected
    ])
    def test_invalid_grades(self, invalid_input):
        with pytest.raises(ValidationError) as exc_info:
            validate_grade(invalid_input)
        assert exc_info.value.field == "grade"
        assert exc_info.value.status_code == 400


class TestSubjectValidation:
    """Tests for validate_subject function."""

    @pytest.mark.parametrize("valid_input,expected", [
        ("Science", "Science"),
        ("science", "Science"),
        ("SCIENCE", "Science"),
        ("sci", "Science"),
        ("physics", "Science"),
        ("chemistry", "Science"),
        ("biology", "Science"),
        ("Maths", "Maths"),
        ("maths", "Maths"),
        ("math", "Maths"),
        ("mathematics", "Maths"),
        ("MATHEMATICS", "Maths"),
        ("algebra", "Maths"),
        ("geometry", "Maths"),
        ("trigonometry", "Maths"),
        ("  science  ", "Science"),
    ])
    def test_valid_subjects(self, valid_input, expected):
        assert validate_subject(valid_input) == expected

    @pytest.mark.parametrize("invalid_input", [
        "History",
        "Geography",
        "English",
        "Hindi",
        "Economics",
        "",
        "   ",
        None,
        "Art",
    ])
    def test_invalid_subjects(self, invalid_input):
        with pytest.raises(ValidationError) as exc_info:
            validate_subject(invalid_input)
        assert exc_info.value.field == "subject"
        assert exc_info.value.status_code == 400


class TestQuestionValidation:
    """Tests for validate_question function."""

    def test_valid_question(self):
        question = "What is Newton's second law of motion?"
        assert validate_question(question) == question

    def test_trims_whitespace(self):
        question = "   Why does ice float on water?   "
        assert validate_question(question) == "Why does ice float on water?"

    def test_empty_question_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_question("")
        assert exc_info.value.field == "question"

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_question("    \n\t   ")
        assert exc_info.value.field == "question"

    def test_none_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_question(None)
        assert exc_info.value.field == "question"

    def test_too_short_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_question("hi")
        assert exc_info.value.field == "question"
        assert "too short" in exc_info.value.message

    def test_punctuation_only_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_question("??????!!")
        assert exc_info.value.field == "question"
        assert "contain letters or numbers" in exc_info.value.message

    def test_exceeding_max_length_raises(self):
        huge_question = "A" * 1501
        with pytest.raises(ValidationError) as exc_info:
            validate_question(huge_question)
        assert exc_info.value.field == "question"
        assert "exceeds maximum length" in exc_info.value.message


class TestCombinedDoubtValidation:
    """Tests for validate_doubt_input function."""

    def test_valid_combined_input(self):
        q, s, g = validate_doubt_input(
            question="What is photosynthesis?",
            subject="biology",
            grade="Class 10",
        )
        assert q == "What is photosynthesis?"
        assert s == "Science"
        assert g == 10

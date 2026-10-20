"""
Input validation utilities for the EduSolve AI Tutor.
Ensures student inputs conform to curriculum scope, grade boundaries, and safety constraints.
"""

import re
from typing import Any, Tuple, Union

from services.config import (
    MAX_QUESTION_LENGTH,
    MIN_QUESTION_LENGTH,
    SUBJECT_ALIASES,
    SUPPORTED_GRADES,
    SUPPORTED_SUBJECTS,
)
from services.exceptions import ValidationError


def validate_grade(grade: Any) -> int:
    """
    Validate and normalize class grade.

    Accepts integer (9, 10) or string representations ("9", "10", "Class 9", "9th", "Grade 10").
    Raises ValidationError if grade is missing or outside supported grades (9, 10).
    """
    if grade is None:
        raise ValidationError("Class grade is required. Please specify Class 9 or 10.", field="grade")

    # If it's already an int
    if isinstance(grade, int) and not isinstance(grade, bool):
        if grade in SUPPORTED_GRADES:
            return grade
        raise ValidationError(
            f"Class {grade} is not supported. EduSolve is currently specialized for Class 9 and 10 only.",
            field="grade",
        )

    # Convert string representation
    grade_str = str(grade).strip().lower()
    if not grade_str:
        raise ValidationError("Class grade cannot be empty. Please specify Class 9 or 10.", field="grade")

    # Match numeric patterns: '9', '10', 'class 9', 'grade 10', '9th', '10th'
    match = re.search(r"\b(9|10)(?:th)?\b", grade_str)
    if match:
        return int(match.group(1))

    raise ValidationError(
        f"Invalid class '{grade}'. EduSolve is specialized for Class 9 and 10 students only.",
        field="grade",
    )


def validate_subject(subject: Any) -> str:
    """
    Validate and normalize academic subject.

    Maps variations ('math', 'mathematics', 'sci', 'physics', 'chemistry', etc.)
    to canonical names ('Science' or 'Maths').
    Raises ValidationError if subject is empty or unsupported.
    """
    if not subject or not str(subject).strip():
        raise ValidationError(
            "Subject is required. Please choose either 'Science' or 'Maths'.",
            field="subject",
        )

    clean_subj = str(subject).strip().lower()

    # Check direct canonical match first
    for canon in SUPPORTED_SUBJECTS:
        if clean_subj == canon.lower():
            return canon

    # Check alias dictionary
    if clean_subj in SUBJECT_ALIASES:
        return SUBJECT_ALIASES[clean_subj]

    # Partial substring check for common compounds like 'computer science' vs 'general science'
    if "math" in clean_subj:
        return "Maths"
    if "sci" in clean_subj:
        return "Science"

    raise ValidationError(
        f"Unsupported subject '{subject}'. EduSolve currently supports 'Science' and 'Maths' only.",
        field="subject",
    )


def validate_question(question: Any) -> str:
    """
    Validate question content and length.

    Ensures question is non-empty, contains meaningful alphanumeric content,
    and adheres to min/max character limits.
    """
    if question is None:
        raise ValidationError("Question cannot be empty. Please enter your academic doubt.", field="question")

    clean_question = str(question).strip()

    if not clean_question:
        raise ValidationError("Question cannot be empty. Please enter your academic doubt.", field="question")

    if len(clean_question) < MIN_QUESTION_LENGTH:
        raise ValidationError(
            f"Question is too short ({len(clean_question)} chars). Please provide more context (minimum {MIN_QUESTION_LENGTH} characters).",
            field="question",
        )

    if len(clean_question) > MAX_QUESTION_LENGTH:
        raise ValidationError(
            f"Question exceeds maximum length of {MAX_QUESTION_LENGTH} characters.",
            field="question",
        )

    # Verify that the input has actual words or symbols, not solely punctuation/whitespace
    if not re.search(r"[\w\d]", clean_question):
        raise ValidationError(
            "Question must contain letters or numbers, not just punctuation.",
            field="question",
        )

    return clean_question


def validate_doubt_input(question: Any, subject: Any, grade: Any) -> Tuple[str, str, int]:
    """
    Validate and normalize all three components of a student doubt.
    Returns (cleaned_question, canonical_subject, grade_int).
    """
    clean_grade = validate_grade(grade)
    clean_subj = validate_subject(subject)
    clean_q = validate_question(question)
    return clean_q, clean_subj, clean_grade

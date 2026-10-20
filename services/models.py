"""
Data models and schemas for EduSolve AI tutor.
Uses Pydantic for validation, serializability, and clean integration with web frameworks.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class PracticeQuestion(BaseModel):
    """Represents a generated practice question with answer and optional choices."""

    question: str = Field(..., description="The practice question prompt")
    answer: str = Field(..., description="The verified answer and step explanation")
    type: Literal["mcq", "short"] = Field(
        default="short", description="Question format: multiple choice ('mcq') or short answer ('short')"
    )
    options: Optional[List[str]] = Field(
        default=None, description="Optional choices for MCQ questions"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert practice question to dictionary."""
        data = {
            "question": self.question,
            "answer": self.answer,
            "type": self.type,
        }
        if self.options:
            data["options"] = self.options
        return data


class StructuredAnswer(BaseModel):
    """Structured breakdown of the AI tutor's pedagogical explanation."""

    explanation: str = Field(..., description="Clear, age-appropriate conceptual walkthrough")
    key_formula_fact: str = Field(..., description="Most critical formula, theorem, or scientific fact")
    real_example: str = Field(..., description="Simple, relatable real-world application or analogy")
    is_domain_match: bool = Field(
        default=True,
        description="Whether the student's doubt belongs to the supported Science/Maths curriculum",
    )

    def to_formatted_text(self) -> str:
        """Render the structured answer into the canonical human-readable format."""
        if not self.is_domain_match:
            return self.explanation

        return (
            f"EXPLANATION:\n{self.explanation}\n\n"
            f"KEY FORMULA / FACT:\n{self.key_formula_fact}\n\n"
            f"REAL EXAMPLE:\n{self.real_example}"
        )


class StudentDoubtRequest(BaseModel):
    """Validated incoming request representing a student doubt."""

    question: str = Field(..., min_length=3, max_length=1500, description="The academic doubt text")
    subject: str = Field(..., description="Subject: 'Science' or 'Maths'")
    grade: int = Field(..., description="Class level: 9 or 10")


class TutorResponse(BaseModel):
    """Comprehensive response returned by the EduSolve AI Tutor Service."""

    success: bool = Field(default=True, description="Indicates whether the request was successfully processed")
    question: str = Field(..., description="Original student question")
    subject: str = Field(..., description="Standardized subject ('Science' or 'Maths')")
    grade: int = Field(..., description="Class grade (9 or 10)")
    structured_answer: StructuredAnswer = Field(..., description="Parsed 3-part structured answer")
    raw_answer: str = Field(..., description="Raw text response from the LLM")
    practice_questions: List[PracticeQuestion] = Field(
        default_factory=list, description="3 practice questions testing comprehension"
    )
    model_used: str = Field(default="llama-3.1-8b-instant", description="LLM identifier used for generation")
    error: Optional[str] = Field(default=None, description="Error message if processing encountered issues")

    def to_legacy_dict(self) -> Dict[str, Any]:
        """Backward-compatible dictionary format for existing ai_engine callers."""
        return {
            "question": self.question,
            "subject": self.subject,
            "grade": self.grade,
            "answer": self.raw_answer,
            "practice_questions": [q.to_dict() for q in self.practice_questions],
            "structured_answer": self.structured_answer.model_dump(),
        }

    def to_api_response(self) -> Dict[str, Any]:
        """Clean dictionary format optimized for REST API responses."""
        return self.model_dump()

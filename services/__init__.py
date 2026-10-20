"""
EduSolve AI Services Package.
Provides reusable domain logic, validation, typed schemas, and Groq LLM integration.
"""

from services.config import DEFAULT_MODEL, GROQ_API_KEY, SUPPORTED_GRADES, SUPPORTED_SUBJECTS
from services.exceptions import (
    AIProviderError,
    AuthenticationError,
    EduSolveError,
    ParsingError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)
from services.groq_client import GroqService
from services.models import (
    PracticeQuestion,
    StructuredAnswer,
    StudentDoubtRequest,
    TutorResponse,
)
from services.parser import parse_practice_questions, parse_structured_answer
from services.tutor_service import TutorService
from services.validators import (
    validate_doubt_input,
    validate_grade,
    validate_question,
    validate_subject,
)

__all__ = [
    # Core Services
    "TutorService",
    "GroqService",
    # Data Models
    "StructuredAnswer",
    "PracticeQuestion",
    "StudentDoubtRequest",
    "TutorResponse",
    # Validation
    "validate_grade",
    "validate_subject",
    "validate_question",
    "validate_doubt_input",
    # Parsers
    "parse_structured_answer",
    "parse_practice_questions",
    # Exceptions
    "EduSolveError",
    "ValidationError",
    "AIProviderError",
    "AuthenticationError",
    "RateLimitError",
    "ServiceUnavailableError",
    "ParsingError",
    # Config
    "DEFAULT_MODEL",
    "GROQ_API_KEY",
    "SUPPORTED_GRADES",
    "SUPPORTED_SUBJECTS",
]

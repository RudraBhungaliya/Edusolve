"""
Custom exceptions for the EduSolve AI Engine.
Provides clean HTTP status code mappings for web applications (Django / FastAPI).
"""

from typing import Any, Dict, Optional


class EduSolveError(Exception):
    """Base exception for all EduSolve AI engine errors."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception details to dictionary for API responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }


class ValidationError(EduSolveError):
    """Raised when student input fails validation."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        merged_details = details or {}
        if field:
            merged_details["field"] = field
        super().__init__(message, status_code=400, details=merged_details)
        self.field = field


class AIProviderError(EduSolveError):
    """Base error for AI provider (Groq) integration issues."""

    def __init__(self, message: str, status_code: int = 502, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=status_code, details=details)


class AuthenticationError(AIProviderError):
    """Raised when Groq API key is missing or invalid."""

    def __init__(
        self,
        message: str = "Invalid or missing GROQ_API_KEY. Please verify your Groq API credentials.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=401, details=details)


class RateLimitError(AIProviderError):
    """Raised when Groq API rate limit or quota is exceeded."""

    def __init__(
        self,
        message: str = "Groq API rate limit reached. Please wait a moment before trying again.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=429, details=details)


class ServiceUnavailableError(AIProviderError):
    """Raised when Groq AI service is unreachable, times out, or fails internally."""

    def __init__(
        self,
        message: str = "Groq AI service is currently unavailable. Please try again shortly.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=503, details=details)


class ParsingError(EduSolveError):
    """Raised when LLM output cannot be parsed into expected structured format."""

    def __init__(self, message: str, raw_content: str = "", details: Optional[Dict[str, Any]] = None):
        merged_details = details or {}
        if raw_content:
            merged_details["raw_content"] = raw_content[:300]
        super().__init__(message, status_code=502, details=merged_details)

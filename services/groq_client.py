"""
Groq API integration service with robust error handling and client abstraction.
Translates provider-specific SDK exceptions into clean, typed application exceptions.
"""

from typing import Any, Dict, List, Optional
import groq
from groq import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError as GroqAuthError,
    InternalServerError as GroqServerError,
    RateLimitError as GroqRateLimitError,
)

from services.config import DEFAULT_MODEL, DEFAULT_TIMEOUT_SECONDS, GROQ_API_KEY
from services.exceptions import (
    AIProviderError,
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
)


class GroqService:
    """Wrapper around Groq Cloud Python SDK providing resilient error management."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        client: Optional[Any] = None,
        default_model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.api_key = api_key if api_key is not None else GROQ_API_KEY
        self.default_model = default_model
        self.timeout = timeout
        self._client = client

    def get_client(self) -> Any:
        """Lazily initialize or return the underlying Groq client."""
        if self._client is not None:
            return self._client

        if not self.api_key or not self.api_key.strip():
            raise AuthenticationError(
                "GROQ_API_KEY is missing. Please set your GROQ_API_KEY in .env or as an environment variable."
            )

        try:
            self._client = groq.Groq(api_key=self.api_key, timeout=self.timeout)
            return self._client
        except Exception as exc:
            raise AuthenticationError(
                f"Failed to initialize Groq client: {str(exc)}"
            ) from exc

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """
        Execute chat completion with comprehensive error handling.

        Translates raw Groq errors into typed EduSolve exceptions:
          - AuthenticationError (401)
          - RateLimitError (429)
          - ServiceUnavailableError (503)
          - AIProviderError (502)
        """
        active_client = self.get_client()
        active_model = model or self.default_model

        try:
            response = active_client.chat.completions.create(
                model=active_model,
                messages=messages,
                temperature=temperature,
            )
            if not response.choices or not response.choices[0].message:
                raise AIProviderError("Groq returned an empty response with no completion choices.")
            return response.choices[0].message.content or ""

        except GroqAuthError as exc:
            raise AuthenticationError(
                "Groq authentication failed. Please verify that your GROQ_API_KEY is valid.",
                details={"original_error": str(exc)},
            ) from exc

        except GroqRateLimitError as exc:
            raise RateLimitError(
                "Groq API rate limit or quota exceeded. Please wait a moment before asking another doubt.",
                details={"original_error": str(exc)},
            ) from exc

        except (APIConnectionError, APITimeoutError) as exc:
            raise ServiceUnavailableError(
                "Could not establish a connection to Groq AI servers. Please check your network connection.",
                details={"original_error": str(exc)},
            ) from exc

        except GroqServerError as exc:
            raise ServiceUnavailableError(
                "Groq AI service is currently encountering server difficulties. Please retry shortly.",
                details={"original_error": str(exc)},
            ) from exc

        except APIError as exc:
            status_code = getattr(exc, "status_code", 502) or 502
            raise AIProviderError(
                f"Groq API encountered an error: {getattr(exc, 'message', str(exc))}",
                status_code=status_code,
                details={"original_error": str(exc)},
            ) from exc

        except (AuthenticationError, RateLimitError, ServiceUnavailableError, AIProviderError):
            # Re-raise already typed exceptions
            raise

        except Exception as exc:
            raise AIProviderError(
                f"Unexpected error communicating with AI tutor: {str(exc)}",
                details={"original_error": str(exc)},
            ) from exc

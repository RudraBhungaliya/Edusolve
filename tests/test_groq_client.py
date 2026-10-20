"""
Unit tests for GroqService and error handling abstraction.
"""

from unittest.mock import MagicMock
import httpx
import pytest
from groq import (
    APIConnectionError,
    APIError,
    AuthenticationError as GroqAuthError,
    InternalServerError as GroqServerError,
    RateLimitError as GroqRateLimitError,
)

from services.exceptions import (
    AIProviderError,
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
)
from services.groq_client import GroqService


class TestGroqServiceInitialization:
    """Tests for initialization and API key validation."""

    def test_missing_api_key_raises_authentication_error(self):
        service = GroqService(api_key="", client=None)
        with pytest.raises(AuthenticationError) as exc_info:
            service.get_client()
        assert "GROQ_API_KEY is missing" in exc_info.value.message
        assert exc_info.value.status_code == 401

    def test_custom_injected_client_used(self):
        mock_client = MagicMock()
        service = GroqService(client=mock_client)
        assert service.get_client() is mock_client


class TestGroqChatCompletion:
    """Tests for chat completion and exception translation."""

    def test_successful_completion(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Hello from Groq!"))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        service = GroqService(client=mock_client)
        result = service.generate_chat_completion(
            messages=[{"role": "user", "content": "Test"}]
        )

        assert result == "Hello from Groq!"
        mock_client.chat.completions.create.assert_called_once()

    def test_handles_authentication_error(self):
        mock_client = MagicMock()
        dummy_req = httpx.Request("POST", "https://api.groq.com")
        dummy_resp = httpx.Response(401, request=dummy_req)
        mock_client.chat.completions.create.side_effect = GroqAuthError(
            message="Invalid API Key",
            response=dummy_resp,
            body={"error": "invalid_api_key"},
        )

        service = GroqService(client=mock_client)
        with pytest.raises(AuthenticationError) as exc_info:
            service.generate_chat_completion(messages=[])
        assert exc_info.value.status_code == 401
        assert "GROQ_API_KEY is valid" in exc_info.value.message

    def test_handles_rate_limit_error(self):
        mock_client = MagicMock()
        dummy_req = httpx.Request("POST", "https://api.groq.com")
        dummy_resp = httpx.Response(429, request=dummy_req)
        mock_client.chat.completions.create.side_effect = GroqRateLimitError(
            message="Rate limit reached",
            response=dummy_resp,
            body={"error": "rate_limit_exceeded"},
        )

        service = GroqService(client=mock_client)
        with pytest.raises(RateLimitError) as exc_info:
            service.generate_chat_completion(messages=[])
        assert exc_info.value.status_code == 429
        assert "rate limit" in exc_info.value.message.lower()

    def test_handles_connection_error(self):
        mock_client = MagicMock()
        dummy_req = httpx.Request("POST", "https://api.groq.com")
        mock_client.chat.completions.create.side_effect = APIConnectionError(
            request=dummy_req,
            message="Connection failed",
        )

        service = GroqService(client=mock_client)
        with pytest.raises(ServiceUnavailableError) as exc_info:
            service.generate_chat_completion(messages=[])
        assert exc_info.value.status_code == 503
        assert "connection" in exc_info.value.message.lower()

    def test_handles_server_error(self):
        mock_client = MagicMock()
        dummy_req = httpx.Request("POST", "https://api.groq.com")
        dummy_resp = httpx.Response(500, request=dummy_req)
        mock_client.chat.completions.create.side_effect = GroqServerError(
            message="Internal Server Error",
            response=dummy_resp,
            body={"error": "server_error"},
        )

        service = GroqService(client=mock_client)
        with pytest.raises(ServiceUnavailableError) as exc_info:
            service.generate_chat_completion(messages=[])
        assert exc_info.value.status_code == 503

    def test_handles_generic_api_error(self):
        mock_client = MagicMock()
        dummy_req = httpx.Request("POST", "https://api.groq.com")
        mock_client.chat.completions.create.side_effect = APIError(
            message="Some API error",
            request=dummy_req,
            body=None,
        )

        service = GroqService(client=mock_client)
        with pytest.raises(AIProviderError) as exc_info:
            service.generate_chat_completion(messages=[])
        assert exc_info.value.status_code == 502

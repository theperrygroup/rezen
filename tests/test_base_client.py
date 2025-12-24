"""Tests for the base client."""

import os
from unittest.mock import patch

import pytest
import requests
import responses

from rezen.base_client import BaseClient
from rezen.exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    RezenError,
    ServerError,
    ValidationError,
)


class TestBaseClientInit:
    """Test BaseClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = BaseClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://arrakis.therealbrokerage.com/api/v1"
        assert client.timeout_seconds == 30.0
        assert client.max_retries == 0
        assert client.retry_backoff_seconds == 0.5
        assert "X-API-KEY" in client.session.headers
        assert client.session.headers["X-API-KEY"] == "test_key"

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = BaseClient(
            api_key="test_key", base_url="https://test.example.com/api/v1"
        )
        assert client.api_key == "test_key"
        assert client.base_url == "https://test.example.com/api/v1"

    @patch.dict(os.environ, {"REZEN_API_KEY": "env_test_key"})
    def test_init_with_env_api_key(self) -> None:
        """Test initialization with API key from environment."""
        client = BaseClient()
        assert client.api_key == "env_test_key"

    @patch.dict(
        os.environ,
        {
            "REZEN_TIMEOUT_SECONDS": "12.5",
            "REZEN_MAX_RETRIES": "2",
            "REZEN_RETRY_BACKOFF_SECONDS": "0.1",
        },
    )
    def test_init_uses_env_timeout_and_retry_config(self) -> None:
        """Test that timeout/retry settings can be read from env vars."""
        client = BaseClient(api_key="test_key")
        assert client.timeout_seconds == 12.5
        assert client.max_retries == 2
        assert client.retry_backoff_seconds == 0.1

    @patch.dict(
        os.environ,
        {
            "REZEN_TIMEOUT_SECONDS": "not-a-number",
            "REZEN_MAX_RETRIES": "nope",
            "REZEN_RETRY_BACKOFF_SECONDS": "bad",
        },
    )
    def test_init_invalid_env_timeout_and_retry_config_falls_back_to_defaults(
        self,
    ) -> None:
        """Test invalid env var values fall back to defaults."""
        client = BaseClient(api_key="test_key")
        assert client.timeout_seconds == 30.0
        assert client.max_retries == 0
        assert client.retry_backoff_seconds == 0.5

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_raises_error(self) -> None:
        """Test that missing API key raises AuthenticationError."""
        with pytest.raises(AuthenticationError, match="API key is required"):
            BaseClient()

    def test_session_headers(self) -> None:
        """Test that session headers are set correctly."""
        client = BaseClient(api_key="test_key")
        headers = client.session.headers
        assert headers["X-API-KEY"] == "test_key"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"


class TestBaseClientResponseHandling:
    """Test response handling and error mapping."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = BaseClient(api_key="test_key")

    @responses.activate
    def test_handle_response_200(self) -> None:
        """Test successful 200 response handling."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"success": True},
            status=200,
        )

        result = self.client.get("test")
        assert result == {"success": True}

    @responses.activate
    def test_handle_response_200_list(self) -> None:
        """Test that list JSON responses are supported."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json=[{"id": "a"}, {"id": "b"}],
            status=200,
        )

        result = self.client.get("test")
        assert result == [{"id": "a"}, {"id": "b"}]

    @responses.activate
    def test_handle_response_200_json_string(self) -> None:
        """Test that JSON string responses are supported."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json="some-id",
            status=200,
        )

        result = self.client.get("test")
        assert result == "some-id"

    @responses.activate
    def test_handle_response_201(self) -> None:
        """Test successful 201 response handling."""
        responses.add(
            responses.POST,
            f"{self.client.base_url}/test",
            json={"created": True},
            status=201,
        )

        result = self.client.post("test", json_data={"data": "test"})
        assert result == {"created": True}

    @responses.activate
    def test_handle_response_204(self) -> None:
        """Test 204 No Content response handling."""
        responses.add(responses.DELETE, f"{self.client.base_url}/test", status=204)

        result = self.client.delete("test")
        assert result == {}

    @responses.activate
    def test_handle_response_400_validation_error(self) -> None:
        """Test 400 Bad Request raises ValidationError."""
        responses.add(
            responses.POST,
            f"{self.client.base_url}/test",
            json={"message": "Invalid data"},
            status=400,
        )

        with pytest.raises(ValidationError, match="Bad request: Invalid data"):
            self.client.post("test", json_data={"invalid": "data"})

    @responses.activate
    def test_handle_response_400_non_dict_json(self) -> None:
        """Test 400 errors where the API returns non-dict JSON payloads."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json=["some-error"],
            status=400,
        )

        with pytest.raises(ValidationError, match="Bad request: \\['some-error'\\]"):
            self.client.get("test")

    @responses.activate
    def test_handle_response_400_owner_info_invalid_request_adds_context(self) -> None:
        """Owner-agent sequencing errors should include extra context."""
        endpoint = "transaction-builder/tx-1/owner-info"
        responses.add(
            responses.PUT,
            f"{self.client.base_url}/{endpoint}",
            json={"message": "Invalid request"},
            status=400,
        )

        with pytest.raises(ValidationError) as exc:
            self.client.put(endpoint, json_data={"ownerAgent": {"agentId": "x"}})

        assert "Owner agent endpoint requires proper transaction setup" in str(
            exc.value
        )

    @responses.activate
    def test_handle_response_401_authentication_error(self) -> None:
        """Test 401 Unauthorized raises AuthenticationError."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"message": "Invalid credentials"},
            status=401,
        )

        with pytest.raises(
            AuthenticationError, match="Authentication failed: Invalid credentials"
        ):
            self.client.get("test")

    @responses.activate
    def test_handle_response_404_not_found_error(self) -> None:
        """Test 404 Not Found raises NotFoundError."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"message": "Not found"},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found: Not found"):
            self.client.get("test")

    @responses.activate
    def test_handle_response_429_rate_limit_error(self) -> None:
        """Test 429 Too Many Requests raises RateLimitError."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"message": "Too many requests"},
            status=429,
        )

        with pytest.raises(
            RateLimitError, match="Rate limit exceeded: Too many requests"
        ):
            self.client.get("test")

    @responses.activate
    def test_handle_response_500_server_error(self) -> None:
        """Test 500 Internal Server Error raises ServerError."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"message": "Internal server error"},
            status=500,
        )

        with pytest.raises(ServerError, match="Server error: Internal server error"):
            self.client.get("test")

    @responses.activate
    def test_handle_response_503_server_error(self) -> None:
        """Test 503 Service Unavailable raises ServerError."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"message": "Service unavailable"},
            status=503,
        )

        with pytest.raises(ServerError, match="Server error: Service unavailable"):
            self.client.get("test")

    @responses.activate
    def test_handle_response_unexpected_error(self) -> None:
        """Test unexpected status code raises RezenError."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"message": "Unexpected error"},
            status=418,  # I'm a teapot
        )

        with pytest.raises(RezenError, match="Unexpected error: Unexpected error"):
            self.client.get("test")

    @responses.activate
    def test_handle_response_empty_content(self) -> None:
        """Test response with empty content."""
        responses.add(
            responses.GET, f"{self.client.base_url}/test", body="", status=200
        )

        result = self.client.get("test")
        assert result == {}

    @responses.activate
    def test_handle_response_invalid_json(self) -> None:
        """Test response with invalid JSON."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            body="invalid json",
            status=400,
        )

        with pytest.raises(ValidationError):
            self.client.get("test")


class TestBaseClientHttpMethods:
    """Test HTTP method wrappers."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = BaseClient(api_key="test_key")

    @responses.activate
    def test_get_method(self) -> None:
        """Test GET method."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"method": "GET"},
            status=200,
        )

        result = self.client.get("test")
        assert result == {"method": "GET"}

    @responses.activate
    def test_get_method_with_params(self) -> None:
        """Test GET method with query parameters."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test?param1=value1&param2=value2",
            json={"method": "GET"},
            status=200,
        )

        params = {"param1": "value1", "param2": "value2"}
        result = self.client.get("test", params=params)
        assert result == {"method": "GET"}

    @responses.activate
    def test_post_method_with_json(self) -> None:
        """Test POST method with JSON data."""
        responses.add(
            responses.POST,
            f"{self.client.base_url}/test",
            json={"method": "POST"},
            status=201,
        )

        result = self.client.post("test", json_data={"key": "value"})
        assert result == {"method": "POST"}

    @responses.activate
    def test_post_method_with_form_data(self) -> None:
        """Test POST method with form data."""
        responses.add(
            responses.POST,
            f"{self.client.base_url}/test",
            json={"method": "POST"},
            status=201,
        )

        result = self.client.post("test", data={"key": "value"})
        assert result == {"method": "POST"}

    @responses.activate
    def test_put_method(self) -> None:
        """Test PUT method."""
        responses.add(
            responses.PUT,
            f"{self.client.base_url}/test",
            json={"method": "PUT"},
            status=200,
        )

        result = self.client.put("test", json_data={"key": "value"})
        assert result == {"method": "PUT"}

    @responses.activate
    def test_delete_method(self) -> None:
        """Test DELETE method."""
        responses.add(
            responses.DELETE,
            f"{self.client.base_url}/test",
            json={"method": "DELETE"},
            status=200,
        )

        result = self.client.delete("test")
        assert result == {"method": "DELETE"}

    @responses.activate
    def test_patch_method(self) -> None:
        """Test PATCH method."""
        responses.add(
            responses.PATCH,
            f"{self.client.base_url}/test",
            json={"method": "PATCH"},
            status=200,
        )

        result = self.client.patch("test", json_data={"key": "value"})
        assert result == {"method": "PATCH"}

    def test_network_error(self) -> None:
        """Test network error handling."""
        with patch.object(
            self.client.session,
            "request",
            side_effect=requests.exceptions.ConnectionError("Connection failed"),
        ):
            with pytest.raises(NetworkError, match="Network error"):
                self.client.get("test")

    def test_default_timeout_is_passed_to_requests(self) -> None:
        """Test that BaseClient applies a default timeout to requests."""
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"ok": true}'
        mock_response.url = f"{self.client.base_url}/test"

        with patch.object(
            self.client.session, "request", return_value=mock_response
        ) as m:
            result = self.client.get("test")
            assert result == {"ok": True}

            assert m.call_args.kwargs["timeout"] == 30.0

    def test_timeout_override_is_passed_to_requests(self) -> None:
        """Test per-request timeout override."""
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"ok": true}'
        mock_response.url = f"{self.client.base_url}/test"

        with patch.object(
            self.client.session, "request", return_value=mock_response
        ) as m:
            result = self.client.get("test", timeout_seconds=5.0)
            assert result == {"ok": True}
            assert m.call_args.kwargs["timeout"] == 5.0

    def test_files_requests_use_requests_request_with_timeout(self) -> None:
        """Test multipart/file requests use requests.request and include timeout."""
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"ok": true}'
        mock_response.url = f"{self.client.base_url}/upload"

        with patch(
            "rezen.base_client.requests.request", return_value=mock_response
        ) as m:
            result = self.client.post("upload", files={"file": ("x.txt", b"x")})
            assert result == {"ok": True}
            assert m.call_args.kwargs["timeout"] == 30.0

    def test_retry_on_5xx_status(self) -> None:
        """Test retry behavior for transient 5xx responses."""
        client = BaseClient(
            api_key="test_key", max_retries=2, retry_backoff_seconds=0.0
        )

        resp_503 = requests.Response()
        resp_503.status_code = 503
        resp_503._content = b'{"message": "Service unavailable"}'
        resp_503.url = f"{client.base_url}/test"

        resp_200 = requests.Response()
        resp_200.status_code = 200
        resp_200._content = b'{"ok": true}'
        resp_200.url = f"{client.base_url}/test"

        with patch.object(
            client.session, "request", side_effect=[resp_503, resp_503, resp_200]
        ) as m, patch("rezen.base_client.time.sleep") as sleep:
            result = client.get("test")
            assert result == {"ok": True}
            assert m.call_count == 3
            assert sleep.call_count == 2

    def test_retry_on_request_exception(self) -> None:
        """Test retry behavior for transient network errors."""
        client = BaseClient(
            api_key="test_key", max_retries=1, retry_backoff_seconds=0.0
        )

        resp_200 = requests.Response()
        resp_200.status_code = 200
        resp_200._content = b'{"ok": true}'
        resp_200.url = f"{client.base_url}/test"

        with patch.object(
            client.session,
            "request",
            side_effect=[
                requests.exceptions.ConnectionError("Connection failed"),
                resp_200,
            ],
        ) as m, patch("rezen.base_client.time.sleep") as sleep:
            result = client.get("test")
            assert result == {"ok": True}
            assert m.call_count == 2
            assert sleep.call_count == 1

    @responses.activate
    def test_endpoint_url_formatting(self) -> None:
        """Test endpoint URL formatting with leading slashes."""
        responses.add(
            responses.GET,
            f"{self.client.base_url}/test",
            json={"success": True},
            status=200,
        )

        # Test with and without leading slash
        result1 = self.client.get("test")
        result2 = self.client.get("/test")

        assert result1 == {"success": True}
        assert result2 == {"success": True}

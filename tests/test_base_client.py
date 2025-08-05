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

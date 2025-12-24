"""Tests for ReZEN API exceptions."""

from rezen.exceptions import (
    AuthenticationError,
    InvalidFieldNameError,
    InvalidFieldValueError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    RezenError,
    ServerError,
    TransactionSequenceError,
    ValidationError,
)


class TestRezenError:
    """Test the base RezenError exception."""

    def test_init_with_message_only(self) -> None:
        """Test RezenError initialization with message only."""
        error = RezenError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code is None
        assert error.response_data is None

    def test_init_with_all_parameters(self) -> None:
        """Test RezenError initialization with all parameters."""
        response_data = {"error": "Test error", "code": 400}
        error = RezenError("Test error", status_code=400, response_data=response_data)

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.response_data == response_data

    def test_inheritance(self) -> None:
        """Test that RezenError inherits from Exception."""
        error = RezenError("Test error")
        assert isinstance(error, Exception)


class TestAuthenticationError:
    """Test the AuthenticationError exception."""

    def test_inheritance(self) -> None:
        """Test that AuthenticationError inherits from RezenError."""
        error = AuthenticationError("Auth error")
        assert isinstance(error, RezenError)
        assert isinstance(error, Exception)

    def test_init(self) -> None:
        """Test AuthenticationError initialization."""
        error = AuthenticationError("Auth failed", status_code=401)
        assert str(error) == "Auth failed"
        assert error.status_code == 401


class TestValidationError:
    """Test the ValidationError exception."""

    def test_inheritance(self) -> None:
        """Test that ValidationError inherits from RezenError."""
        error = ValidationError("Validation error")
        assert isinstance(error, RezenError)
        assert isinstance(error, Exception)

    def test_init(self) -> None:
        """Test ValidationError initialization."""
        error = ValidationError("Invalid data", status_code=400)
        assert str(error) == "Invalid data"
        assert error.status_code == 400


class TestNotFoundError:
    """Test the NotFoundError exception."""

    def test_inheritance(self) -> None:
        """Test that NotFoundError inherits from RezenError."""
        error = NotFoundError("Not found error")
        assert isinstance(error, RezenError)
        assert isinstance(error, Exception)

    def test_init(self) -> None:
        """Test NotFoundError initialization."""
        error = NotFoundError("Resource not found", status_code=404)
        assert str(error) == "Resource not found"
        assert error.status_code == 404


class TestRateLimitError:
    """Test the RateLimitError exception."""

    def test_inheritance(self) -> None:
        """Test that RateLimitError inherits from RezenError."""
        error = RateLimitError("Rate limit error")
        assert isinstance(error, RezenError)
        assert isinstance(error, Exception)

    def test_init(self) -> None:
        """Test RateLimitError initialization."""
        error = RateLimitError("Rate limit exceeded", status_code=429)
        assert str(error) == "Rate limit exceeded"
        assert error.status_code == 429


class TestServerError:
    """Test the ServerError exception."""

    def test_inheritance(self) -> None:
        """Test that ServerError inherits from RezenError."""
        error = ServerError("Server error")
        assert isinstance(error, RezenError)
        assert isinstance(error, Exception)

    def test_init(self) -> None:
        """Test ServerError initialization."""
        error = ServerError("Internal server error", status_code=500)
        assert str(error) == "Internal server error"
        assert error.status_code == 500


class TestNetworkError:
    """Test the NetworkError exception."""

    def test_inheritance(self) -> None:
        """Test that NetworkError inherits from RezenError."""
        error = NetworkError("Network error")
        assert isinstance(error, RezenError)
        assert isinstance(error, Exception)

    def test_init(self) -> None:
        """Test NetworkError initialization."""
        error = NetworkError("Connection failed")
        assert str(error) == "Connection failed"
        assert error.status_code is None


class TestTransactionSequenceError:
    """Test the TransactionSequenceError exception."""

    def test_init_with_required_steps(self) -> None:
        """Test message formatting with required steps."""
        error = TransactionSequenceError(
            "Sequence error", required_steps=["Step A", "Step B"]
        )
        assert "Required sequence" in str(error)
        assert "1. Step A" in str(error)
        assert "2. Step B" in str(error)
        assert error.required_steps == ["Step A", "Step B"]


class TestInvalidFieldNameError:
    """Test the InvalidFieldNameError exception."""

    def test_message_contains_correct_field_name(self) -> None:
        """Test that the error suggests the correct field name."""
        error = InvalidFieldNameError("first_name", "firstName", "Use camelCase.")
        assert "first_name" in str(error)
        assert "firstName" in str(error)


class TestInvalidFieldValueError:
    """Test the InvalidFieldValueError exception."""

    def test_message_contains_expected_format(self) -> None:
        """Test that the error includes expected format information."""
        error = InvalidFieldValueError("state", "Utah", "ALL CAPS")
        assert "state" in str(error)
        assert "ALL CAPS" in str(error)

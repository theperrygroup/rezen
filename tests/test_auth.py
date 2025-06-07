"""Tests for authentication client."""

from unittest.mock import Mock, patch

import pytest
import requests

from rezen.auth import AuthClient
from rezen.exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    ValidationError,
)


class TestAuthClient:
    """Test cases for AuthClient."""

    @pytest.fixture
    def auth_client(self) -> AuthClient:
        """Create AuthClient instance for testing."""
        return AuthClient(api_key="test_api_key")

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Create mock session for testing."""
        return Mock()

    def test_auth_client_initialization(self) -> None:
        """Test AuthClient initialization."""
        client = AuthClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert "keymaker.therealbrokerage.com" in client.base_url

    def test_auth_client_with_custom_base_url(self) -> None:
        """Test AuthClient with custom base URL."""
        custom_url = "https://test.example.com/api/v1"
        client = AuthClient(api_key="test_key", base_url=custom_url)
        assert client.base_url == custom_url

    @patch("rezen.auth.AuthClient.post")
    def test_signin_success(self, mock_post: Mock, auth_client: AuthClient) -> None:
        """Test successful signin."""
        mock_response = {
            "accessToken": "jwt_token_here",
            "tokenType": "Bearer",
            "expiresIn": 3600,
        }
        mock_post.return_value = mock_response

        result = auth_client.signin("user@example.com", "password123")

        mock_post.assert_called_once_with(
            "auth/signin",
            json_data={
                "username": "user@example.com",
                "password": "password123",
            },
        )
        assert result == mock_response

    @patch("rezen.auth.AuthClient.post")
    def test_signin_with_app_name(
        self, mock_post: Mock, auth_client: AuthClient
    ) -> None:
        """Test signin with app name header."""
        mock_response = {"accessToken": "jwt_token_here"}
        mock_post.return_value = mock_response

        with patch.object(auth_client.session, "headers") as mock_headers:
            mock_headers.get.return_value = "Bearer test_api_key"
            mock_headers.__contains__ = Mock(return_value=True)
            mock_headers.__delitem__ = Mock()
            mock_headers.__setitem__ = Mock()
            mock_headers.copy = Mock(
                return_value={"Authorization": "Bearer test_api_key"}
            )
            mock_headers.update = Mock()
            mock_headers.clear = Mock()

            result = auth_client.signin(
                "user@example.com", "password123", app_name="TestApp"
            )

        assert result == mock_response

    @patch("rezen.auth.AuthClient.post")
    def test_signin_authentication_error(
        self, mock_post: Mock, auth_client: AuthClient
    ) -> None:
        """Test signin with authentication error."""
        mock_post.side_effect = AuthenticationError("Invalid credentials")

        with pytest.raises(AuthenticationError):
            auth_client.signin("user@example.com", "wrong_password")

    @patch("rezen.auth.AuthClient.post")
    def test_signout_success(self, mock_post: Mock, auth_client: AuthClient) -> None:
        """Test successful signout."""
        mock_response = {"message": "Successfully signed out"}
        mock_post.return_value = mock_response

        result = auth_client.signout()

        mock_post.assert_called_once_with("auth/signout")
        assert result == mock_response

    @patch("rezen.auth.AuthClient.post")
    def test_update_password_success(
        self, mock_post: Mock, auth_client: AuthClient
    ) -> None:
        """Test successful password update."""
        mock_response = {"message": "Password updated successfully"}
        mock_post.return_value = mock_response

        result = auth_client.update_password("old_password", "new_password")

        mock_post.assert_called_once_with(
            "auth/updatepassword",
            json_data={
                "currentPassword": "old_password",
                "newPassword": "new_password",
            },
        )
        assert result == mock_response

    @patch("rezen.auth.AuthClient.post")
    def test_update_password_with_app_name(self, mock_post, auth_client):
        """Test password update with app name header."""
        mock_response = {"message": "Password updated successfully"}
        mock_post.return_value = mock_response

        with patch.object(auth_client.session, "headers") as mock_headers:
            mock_headers.copy = Mock(
                return_value={"Authorization": "Bearer test_api_key"}
            )
            mock_headers.update = Mock()
            mock_headers.clear = Mock()

            result = auth_client.update_password(
                "old_password", "new_password", app_name="TestApp"
            )

        assert result == mock_response

    @patch("rezen.auth.AuthClient.post")
    def test_reset_password_success(self, mock_post, auth_client):
        """Test successful password reset."""
        mock_response = {"message": "Password reset successfully"}
        mock_post.return_value = mock_response

        result = auth_client.reset_password(
            "user@example.com", "new_password", "reset_token_123"
        )

        mock_post.assert_called_once_with(
            "auth/resetpassword",
            json_data={
                "email": "user@example.com",
                "newPassword": "new_password",
                "resetToken": "reset_token_123",
            },
        )
        assert result == mock_response

    @patch("rezen.auth.AuthClient.post")
    def test_change_password_success(self, mock_post, auth_client):
        """Test successful password change."""
        mock_response = {"message": "Password changed successfully"}
        mock_post.return_value = mock_response

        with patch.object(auth_client.session, "headers") as mock_headers:
            mock_headers.get.return_value = "Bearer test_api_key"
            mock_headers.__contains__ = Mock(return_value=True)
            mock_headers.__delitem__ = Mock()
            mock_headers.__setitem__ = Mock()

            result = auth_client.change_password(
                "user@example.com", "new_password", "change_token_123"
            )

        mock_post.assert_called_once_with(
            "auth/changepassword",
            json_data={
                "username": "user@example.com",
                "newPassword": "new_password",
                "resetToken": "change_token_123",
            },
        )
        assert result == mock_response

    @patch("rezen.auth.AuthClient.get")
    def test_verify_token_success(self, mock_get, auth_client):
        """Test successful token verification."""
        mock_response = {
            "id": "user123",
            "username": "user@example.com",
            "roles": ["USER"],
        }
        mock_get.return_value = mock_response

        with patch.object(auth_client.session, "headers") as mock_headers:
            mock_headers.get.return_value = "Bearer test_api_key"
            mock_headers.__contains__ = Mock(return_value=True)
            mock_headers.__delitem__ = Mock()
            mock_headers.__setitem__ = Mock()

            result = auth_client.verify_token("auth_token_123")

        mock_get.assert_called_once_with("auth/verify/auth_token_123")
        assert result == mock_response

    @patch("rezen.auth.AuthClient.get")
    def test_check_username_availability_success(self, mock_get, auth_client):
        """Test successful username availability check."""
        mock_response = {"available": True}
        mock_get.return_value = mock_response

        with patch.object(auth_client.session, "headers") as mock_headers:
            mock_headers.get.return_value = "Bearer test_api_key"
            mock_headers.__contains__ = Mock(return_value=True)
            mock_headers.__delitem__ = Mock()
            mock_headers.__setitem__ = Mock()

            result = auth_client.check_username_availability("new_username")

        mock_get.assert_called_once_with(
            "auth/checkusernameavailability", params={"username": "new_username"}
        )
        assert result == mock_response

    @patch("rezen.auth.AuthClient.get")
    def test_check_email_availability_success(self, mock_get, auth_client):
        """Test successful email availability check."""
        mock_response = {"available": False}
        mock_get.return_value = mock_response

        with patch.object(auth_client.session, "headers") as mock_headers:
            mock_headers.get.return_value = "Bearer test_api_key"
            mock_headers.__contains__ = Mock(return_value=True)
            mock_headers.__delitem__ = Mock()
            mock_headers.__setitem__ = Mock()

            result = auth_client.check_email_availability("user@example.com")

        mock_get.assert_called_once_with(
            "auth/checkemailavailability", params={"email": "user@example.com"}
        )
        assert result == mock_response

    @patch("rezen.auth.AuthClient.get")
    def test_get_current_user_success(self, mock_get, auth_client):
        """Test successful current user retrieval."""
        mock_response = {
            "id": "user123",
            "username": "user@example.com",
            "email": "user@example.com",
            "roles": ["USER"],
        }
        mock_get.return_value = mock_response

        result = auth_client.get_current_user()

        mock_get.assert_called_once_with("keymaker/myself")
        assert result == mock_response

    @patch("rezen.auth.AuthClient.get")
    def test_get_user_identity_success(self, mock_get, auth_client):
        """Test successful user identity retrieval."""
        mock_response = {
            "id": "user123",
            "username": "user@example.com",
            "email": "user@example.com",
        }
        mock_get.return_value = mock_response

        result = auth_client.get_user_identity("user123")

        mock_get.assert_called_once_with("users/user123")
        assert result == mock_response

    @patch("rezen.auth.AuthClient.get")
    def test_get_user_identity_not_found(self, mock_get, auth_client):
        """Test user identity not found."""
        mock_get.side_effect = NotFoundError("User not found")

        with pytest.raises(NotFoundError):
            auth_client.get_user_identity("nonexistent_user")

    def test_network_error_handling(self, auth_client):
        """Test network error handling."""
        with patch.object(auth_client.session, "request") as mock_request:
            mock_request.side_effect = requests.exceptions.ConnectionError(
                "Network error"
            )

            with pytest.raises(NetworkError):
                auth_client.signin("user@example.com", "password123")

    def test_validation_error_handling(self, auth_client):
        """Test validation error handling."""
        with patch("rezen.auth.AuthClient.post") as mock_post:
            mock_post.side_effect = ValidationError("Invalid parameters")

            with pytest.raises(ValidationError):
                auth_client.update_password("", "")  # Empty passwords

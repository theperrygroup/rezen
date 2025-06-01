"""Integration tests for authentication clients with RezenClient."""

from unittest.mock import Mock, patch

import pytest

from rezen import ApiKeysClient, AuthClient, MfaClient, RezenClient


class TestClientAuthIntegration:
    """Test authentication client integration with main RezenClient."""

    @pytest.fixture
    def client(self) -> RezenClient:
        """Create RezenClient instance for testing."""
        return RezenClient(api_key="test_api_key")

    def test_auth_client_property(self, client: RezenClient) -> None:
        """Test auth client property access."""
        auth_client = client.auth
        assert isinstance(auth_client, AuthClient)
        assert auth_client.api_key == "test_api_key"
        assert "keymaker.therealbrokerage.com" in auth_client.base_url

    def test_mfa_client_property(self, client: RezenClient) -> None:
        """Test MFA client property access."""
        mfa_client = client.mfa
        assert isinstance(mfa_client, MfaClient)
        assert mfa_client.api_key == "test_api_key"
        assert "keymaker.therealbrokerage.com" in mfa_client.base_url

    def test_api_keys_client_property(self, client: RezenClient) -> None:
        """Test API keys client property access."""
        api_keys_client = client.api_keys
        assert isinstance(api_keys_client, ApiKeysClient)
        assert api_keys_client.api_key == "test_api_key"
        assert "keymaker.therealbrokerage.com" in api_keys_client.base_url

    def test_auth_client_singleton_behavior(self, client: RezenClient) -> None:
        """Test that auth client properties return the same instance."""
        auth1 = client.auth
        auth2 = client.auth
        assert auth1 is auth2

        mfa1 = client.mfa
        mfa2 = client.mfa
        assert mfa1 is mfa2

        api_keys1 = client.api_keys
        api_keys2 = client.api_keys
        assert api_keys1 is api_keys2

    @patch("rezen.auth.AuthClient.signin")
    def test_auth_signin_integration(
        self, mock_signin: Mock, client: RezenClient
    ) -> None:
        """Test authentication signin integration."""
        mock_response = {"accessToken": "test_token", "tokenType": "Bearer"}
        mock_signin.return_value = mock_response

        result = client.auth.signin("user@example.com", "password123")

        mock_signin.assert_called_once_with("user@example.com", "password123")
        assert result == mock_response

    @patch("rezen.mfa.MfaClient.get_mfa_qr_code")
    def test_mfa_qr_code_integration(
        self, mock_qr_code: Mock, client: RezenClient
    ) -> None:
        """Test MFA QR code integration."""
        mock_response = {"qrCode": "test_qr_code_data"}
        mock_qr_code.return_value = mock_response

        result = client.mfa.get_mfa_qr_code()

        mock_qr_code.assert_called_once()
        assert result == mock_response

    @patch("rezen.api_keys.ApiKeysClient.get_api_keys")
    def test_api_keys_list_integration(
        self, mock_get_keys: Mock, client: RezenClient
    ) -> None:
        """Test API keys listing integration."""
        mock_response = [
            {"id": "key1", "name": "Test Key 1"},
            {"id": "key2", "name": "Test Key 2"},
        ]
        mock_get_keys.return_value = mock_response

        result = client.api_keys.get_api_keys()

        mock_get_keys.assert_called_once()
        assert result == mock_response

    def test_all_clients_accessible(self, client: RezenClient) -> None:
        """Test that all clients (old and new) are accessible."""
        # Original clients
        assert hasattr(client, "transaction_builder")
        assert hasattr(client, "transactions")
        assert hasattr(client, "teams")
        assert hasattr(client, "agents")
        assert hasattr(client, "directory")

        # New authentication clients
        assert hasattr(client, "auth")
        assert hasattr(client, "mfa")
        assert hasattr(client, "api_keys")

        # Verify they're all working
        assert client.transaction_builder is not None
        assert client.transactions is not None
        assert client.teams is not None
        assert client.agents is not None
        assert client.directory is not None
        assert client.auth is not None
        assert client.mfa is not None
        assert client.api_keys is not None

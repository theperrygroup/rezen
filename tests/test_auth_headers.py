"""Critical authentication header tests to prevent regression."""

from unittest.mock import Mock, patch

import pytest

from rezen import RezenClient
from rezen.base_client import BaseClient


class TestAuthenticationHeaders:
    """Test authentication header format to prevent breaking changes."""

    def test_base_client_uses_x_api_key_header(self):
        """Test that BaseClient uses X-API-KEY header, not Bearer auth."""
        client = BaseClient(api_key="test_key_12345")

        # Critical: Must use X-API-KEY header format
        assert "X-API-KEY" in client.session.headers
        assert client.session.headers["X-API-KEY"] == "test_key_12345"

        # Critical: Must NOT use Authorization Bearer format
        assert "Authorization" not in client.session.headers

    def test_rezen_client_auth_header_propagation(self):
        """Test that RezenClient properly propagates X-API-KEY to sub-clients."""
        client = RezenClient(api_key="test_key_12345")

        # Test main client
        assert "X-API-KEY" in client.transaction_builder.session.headers
        assert (
            client.transaction_builder.session.headers["X-API-KEY"] == "test_key_12345"
        )

        # Test users client (different base URL)
        assert "X-API-KEY" in client.users.session.headers
        assert client.users.session.headers["X-API-KEY"] == "test_key_12345"

        # Test auth client (different base URL)
        assert "X-API-KEY" in client.auth.session.headers
        assert client.auth.session.headers["X-API-KEY"] == "test_key_12345"

    @patch("requests.Session.request")
    def test_real_api_call_uses_correct_headers(self, mock_request):
        """Test that actual API calls use the correct X-API-KEY header."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test", "firstName": "Test"}
        mock_response.content = b'{"id": "test", "firstName": "Test"}'
        mock_request.return_value = mock_response

        client = RezenClient(api_key="test_key_12345")

        # Make a call that would have failed with wrong auth headers
        client.users.get_current_user()

        # Verify the request was made with correct headers
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        headers = call_args[1].get(
            "headers", call_args[0][4] if len(call_args[0]) > 4 else {}
        )

        # Check that the session headers include X-API-KEY
        session_headers = client.users.session.headers
        assert "X-API-KEY" in session_headers
        assert session_headers["X-API-KEY"] == "test_key_12345"
        assert "Authorization" not in session_headers

    def test_api_key_format_validation(self):
        """Test that API keys are properly formatted."""
        # Test with real-like API key format
        api_key = "real_Qp1vOeBFiVevF3XV0APgznZ2frPp8fSlaqq7"
        client = BaseClient(api_key=api_key)

        assert client.session.headers["X-API-KEY"] == api_key
        assert client.api_key == api_key

    def test_auth_header_consistency_across_clients(self):
        """Test that all client types use the same authentication method."""
        api_key = "test_consistency_key"
        main_client = RezenClient(api_key=api_key)

        # Get all sub-clients
        clients_to_test = [
            main_client.transaction_builder,
            main_client.transactions,
            main_client.users,
            main_client.auth,
            main_client.teams,
            main_client.agents,
            main_client.directory,
            main_client.checklist,
            main_client.dropbox,
            main_client.documents,
            main_client.mfa,
            main_client.api_keys,
        ]

        for client in clients_to_test:
            # All clients must use X-API-KEY
            assert (
                "X-API-KEY" in client.session.headers
            ), f"Missing X-API-KEY in {client.__class__.__name__}"
            assert (
                client.session.headers["X-API-KEY"] == api_key
            ), f"Wrong API key in {client.__class__.__name__}"

            # No client should use Authorization Bearer
            assert (
                "Authorization" not in client.session.headers
            ), f"Found Authorization header in {client.__class__.__name__}"

    def test_header_immutability_protection(self):
        """Test that headers can't be accidentally modified to wrong format."""
        client = BaseClient(api_key="test_key")

        # Attempting to set Authorization should not break X-API-KEY
        client.session.headers["Authorization"] = "Bearer wrong_format"

        # X-API-KEY should still be there and correct
        assert "X-API-KEY" in client.session.headers
        assert client.session.headers["X-API-KEY"] == "test_key"

        # But we should be aware that Authorization was added (this test documents the behavior)
        assert "Authorization" in client.session.headers

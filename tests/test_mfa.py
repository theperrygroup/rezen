"""Tests for MfaClient."""

import responses

from rezen.mfa import MfaClient


class TestMfaClient:
    """Test cases for MfaClient."""

    def setup_method(self) -> None:
        """Set up client for tests."""
        self.client = MfaClient(api_key="test_key")
        self.base_url = "https://keymaker.therealbrokerage.com/api/v1"

    def test_client_initialization(self) -> None:
        """Client should use the keymaker base URL by default."""
        assert self.client.base_url == self.base_url

    @responses.activate
    def test_signin_with_mfa_without_app_name(self) -> None:
        """Test signin_with_mfa without X-real-app-name header."""
        responses.add(
            responses.POST,
            f"{self.base_url}/mfa/signin-with-mfa",
            json={"accessToken": "t"},
            status=200,
        )

        result = self.client.signin_with_mfa("u@example.com", "123456")
        assert result["accessToken"] == "t"

    @responses.activate
    def test_signin_with_mfa_with_app_name_header_is_temporary(self) -> None:
        """Test signin_with_mfa uses X-real-app-name and restores headers."""
        responses.add(
            responses.POST,
            f"{self.base_url}/mfa/signin-with-mfa",
            json={"accessToken": "t"},
            status=200,
        )

        result = self.client.signin_with_mfa(
            "u@example.com", "123456", app_name="my-app"
        )
        assert result["accessToken"] == "t"
        assert responses.calls[0].request.headers.get("X-real-app-name") == "my-app"
        # Header should not persist after the call.
        assert "X-real-app-name" not in self.client.session.headers

    @responses.activate
    def test_enable_mfa(self) -> None:
        """Test enable_mfa endpoint."""
        responses.add(
            responses.POST,
            f"{self.base_url}/mfa/enable-mfa",
            json={"ok": True},
            status=200,
        )

        assert self.client.enable_mfa("secret", "123456") == {"ok": True}

    @responses.activate
    def test_enable_mfa_and_signin_without_app_name(self) -> None:
        """Test enable_mfa_and_signin without app name."""
        responses.add(
            responses.POST,
            f"{self.base_url}/mfa/enable-mfa-and-signin",
            json={"accessToken": "t"},
            status=200,
        )

        assert self.client.enable_mfa_and_signin("secret", "123456") == {
            "accessToken": "t"
        }

    @responses.activate
    def test_enable_mfa_and_signin_with_app_name_header_is_temporary(self) -> None:
        """Test enable_mfa_and_signin uses X-real-app-name and restores headers."""
        responses.add(
            responses.POST,
            f"{self.base_url}/mfa/enable-mfa-and-signin",
            json={"accessToken": "t"},
            status=200,
        )

        result = self.client.enable_mfa_and_signin(
            "secret", "123456", app_name="my-app"
        )
        assert result["accessToken"] == "t"
        assert responses.calls[0].request.headers.get("X-real-app-name") == "my-app"
        assert "X-real-app-name" not in self.client.session.headers

    @responses.activate
    def test_send_mfa_sms_without_phone(self) -> None:
        """Test send_mfa_sms without specifying phone number."""
        responses.add(
            responses.GET,
            f"{self.base_url}/mfa/send-mfa-sms",
            json={"ok": True},
            status=200,
        )

        assert self.client.send_mfa_sms() == {"ok": True}

    @responses.activate
    def test_send_mfa_sms_with_phone(self) -> None:
        """Test send_mfa_sms includes phoneNumber param when provided."""
        responses.add(
            responses.GET,
            f"{self.base_url}/mfa/send-mfa-sms?phoneNumber=%2B1234567890",
            json={"ok": True},
            status=200,
        )

        assert self.client.send_mfa_sms(phone_number="+1234567890") == {"ok": True}

    @responses.activate
    def test_get_mfa_qr_code(self) -> None:
        """Test get_mfa_qr_code endpoint."""
        responses.add(
            responses.GET,
            f"{self.base_url}/mfa/mfa-qr-code",
            json={"qr": "data"},
            status=200,
        )

        assert self.client.get_mfa_qr_code() == {"qr": "data"}

    @responses.activate
    def test_get_mfa_status(self) -> None:
        """Test get_mfa_status endpoint."""
        responses.add(
            responses.GET,
            f"{self.base_url}/mfa",
            json={"enabled": True},
            status=200,
        )

        assert self.client.get_mfa_status() == {"enabled": True}

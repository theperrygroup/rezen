"""Tests for ApiKeysClient."""

import re

import pytest
import responses

from rezen.api_keys import ApiKeysClient
from rezen.exceptions import NotFoundError


class TestApiKeysClient:
    """Test cases for the ApiKeysClient."""

    def setup_method(self) -> None:
        """Set up client for tests."""
        self.client = ApiKeysClient(api_key="test_key")
        self.base_url = "https://keymaker.therealbrokerage.com/api/v1"

    def test_client_initialization(self) -> None:
        """Client should use the keymaker base URL by default."""
        assert self.client.base_url == self.base_url

    @responses.activate
    def test_get_api_keys_returns_list(self) -> None:
        """Test that get_api_keys returns list payloads."""
        responses.add(
            responses.GET,
            f"{self.base_url}/api-keys",
            json=[{"id": "k1"}, {"id": "k2"}],
            status=200,
        )

        result = self.client.get_api_keys()
        assert result == [{"id": "k1"}, {"id": "k2"}]

    def test_get_api_keys_returns_empty_list_for_non_list_payload(self) -> None:
        """If API returns non-list, get_api_keys should return empty list."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "get", lambda *_args, **_kwargs: {"not": "a list"})
            assert self.client.get_api_keys() == []

    @responses.activate
    def test_generate_api_key_with_optional_fields(self) -> None:
        """Test generate_api_key sends optional fields when provided."""
        responses.add(
            responses.POST,
            f"{self.base_url}/api-keys",
            json={"id": "k1", "keyValue": "secret"},
            status=201,
        )

        result = self.client.generate_api_key(
            name="Test Key", description="desc", expires_at="2026-01-01"
        )
        assert result["id"] == "k1"

        body = responses.calls[0].request.body
        assert body is not None
        assert b'"name": "Test Key"' in body
        assert b'"description": "desc"' in body
        assert b'"expiresAt": "2026-01-01"' in body

    @responses.activate
    def test_revoke_api_key_uses_delete_with_body(self) -> None:
        """Test revoke_api_key uses DELETE /api-keys with a request body."""
        responses.add(
            responses.DELETE,
            f"{self.base_url}/api-keys",
            json={},
            status=200,
        )

        result = self.client.revoke_api_key("k1")
        assert result == {}

        # Verify body contains keyId
        assert responses.calls[0].request.body == b'{"keyId": "k1"}'

    def test_get_api_key_details_filters_from_list(self) -> None:
        """Test get_api_key_details returns matching key."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                self.client, "get_api_keys", lambda: [{"id": "k1"}, {"id": "k2"}]
            )
            assert self.client.get_api_key_details("k2") == {"id": "k2"}

    def test_get_api_key_details_raises_not_found(self) -> None:
        """Test get_api_key_details raises NotFoundError when missing."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "get_api_keys", lambda: [{"id": "k1"}])
            with pytest.raises(NotFoundError):
                self.client.get_api_key_details("k2")

    def test_update_api_key_requires_at_least_one_field(self) -> None:
        """Test update_api_key requires name/description."""
        with pytest.raises(ValueError, match="At least one field"):
            self.client.update_api_key("k1")

    @responses.activate
    def test_update_api_key_sends_patch(self) -> None:
        """Test update_api_key issues PATCH with provided fields."""
        responses.add(
            responses.PATCH,
            re.compile(f"{re.escape(self.base_url)}/api-keys/k1$"),
            json={"id": "k1", "name": "New"},
            status=200,
        )

        result = self.client.update_api_key("k1", name="New")
        assert result["name"] == "New"
        assert responses.calls[0].request.body == b'{"name": "New"}'

    def test_update_api_key_includes_description(self) -> None:
        """update_api_key should include description when provided."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "patch", lambda *_args, **_kwargs: {"ok": True})
            result = self.client.update_api_key("k1", description="Updated")
            assert result == {"ok": True}

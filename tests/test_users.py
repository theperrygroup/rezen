"""Tests for UsersClient."""

import re

import pytest
import responses

from rezen.users import UsersClient


class TestUsersClient:
    """Test cases for the UsersClient."""

    def setup_method(self) -> None:
        """Set up client for tests."""
        self.client = UsersClient(api_key="test_key")
        self.base_url = "https://yenta.therealbrokerage.com/api/v1"

    def test_client_initialization(self) -> None:
        """Client should use the yenta base URL by default."""
        assert self.client.base_url == self.base_url

    @responses.activate
    def test_get_user_by_id(self) -> None:
        """Test get_user_by_id calls /users/{id}."""
        user_id = "user-123"
        responses.add(
            responses.GET,
            f"{self.base_url}/users/{user_id}",
            json={"id": user_id, "firstName": "A"},
            status=200,
        )

        assert self.client.get_user_by_id(user_id)["id"] == user_id

    @responses.activate
    def test_get_generic_user_by_id(self) -> None:
        """Test get_generic_user_by_id calls /users/generic/{id}."""
        user_id = "user-123"
        responses.add(
            responses.GET,
            f"{self.base_url}/users/generic/{user_id}",
            json={"id": user_id, "username": "u"},
            status=200,
        )

        assert self.client.get_generic_user_by_id(user_id)["username"] == "u"

    @responses.activate
    def test_get_current_generic_user(self) -> None:
        """Test get_current_generic_user calls /users/generic/me."""
        responses.add(
            responses.GET,
            f"{self.base_url}/users/generic/me",
            json={"id": "me"},
            status=200,
        )

        assert self.client.get_current_generic_user()["id"] == "me"

    @responses.activate
    def test_get_keymaker_ids(self) -> None:
        """Test get_keymaker_ids includes yentaIds query params."""
        responses.add(
            responses.GET,
            re.compile(f"{re.escape(self.base_url)}/users/keymaker-ids.*"),
            json=["k1", "k2"],
            status=200,
        )

        result = self.client.get_keymaker_ids(["y1", "y2"])
        assert result == ["k1", "k2"]
        request_url = responses.calls[0].request.url
        assert "yentaIds=y1" in request_url
        assert "yentaIds=y2" in request_url

    def test_get_keymaker_ids_accepts_wrapped_payload(self) -> None:
        """get_keymaker_ids should accept wrapped list payloads for robustness."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "get", lambda *_args, **_kwargs: {"ids": ["k1"]})
            assert self.client.get_keymaker_ids("y1") == ["k1"]

    def test_get_keymaker_ids_raises_for_unexpected_payload(self) -> None:
        """get_keymaker_ids should raise when the payload isn't recognized."""
        with pytest.raises(ValueError):
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(
                    self.client, "get", lambda *_args, **_kwargs: {"ids": "nope"}
                )
                self.client.get_keymaker_ids("y1")

    def test_get_agent_id_for_current_user(self) -> None:
        """Test convenience helper that returns user.id."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "get_current_user", lambda: {"id": "agent-1"})
            assert self.client.get_agent_id_for_current_user() == "agent-1"

    @responses.activate
    def test_get_principal_user(self) -> None:
        """Test get_principal_user calls /users/myprincipal."""
        responses.add(
            responses.GET,
            f"{self.base_url}/users/myprincipal",
            json={"id": "p1"},
            status=200,
        )

        assert self.client.get_principal_user()["id"] == "p1"

    @responses.activate
    def test_get_user_count_with_and_without_params(self) -> None:
        """Test get_user_count includes optional terminatedOnly param."""
        responses.add(
            responses.GET,
            re.compile(f"{re.escape(self.base_url)}/users/count.*"),
            json={"count": 10},
            status=200,
        )

        assert self.client.get_user_count() == {"count": 10}
        assert self.client.get_user_count(terminated_only=True) == {"count": 10}

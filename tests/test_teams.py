"""Tests for teams client."""

import json
from datetime import date
from typing import Any, Dict
from unittest.mock import patch

import pytest
import responses

from rezen.exceptions import AuthenticationError, NotFoundError, ValidationError
from rezen.teams import SortDirection, SortField, TeamsClient, TeamStatus, TeamType


class TestTeamsClient:
    """Test cases for TeamsClient."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TeamsClient(api_key="test_api_key")

    def test_init_with_api_key(self) -> None:
        """Test client initialization with API key."""
        client = TeamsClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://yenta.therealbrokerage.com/api/v1"

    def test_init_with_custom_base_url(self) -> None:
        """Test client initialization with custom base URL."""
        client = TeamsClient(
            api_key="test_key", base_url="https://custom.example.com/api/v1"
        )
        assert client.base_url == "https://custom.example.com/api/v1"

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_api_key"})
    def test_init_with_env_api_key(self) -> None:
        """Test client initialization with environment variable API key."""
        client = TeamsClient()
        assert client.api_key == "env_api_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test client initialization without API key raises error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(AuthenticationError, match="API key is required"):
                TeamsClient()

    @responses.activate
    def test_search_teams_minimal(self) -> None:
        """Test search teams with minimal parameters."""
        mock_response: Dict[str, Any] = {
            "content": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Test Team",
                    "status": "ACTIVE",
                    "teamType": "NORMAL",
                }
            ],
            "pageable": {"pageNumber": 0, "pageSize": 20},
            "totalElements": 1,
        }

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        result = self.client.search_teams()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_search_teams_with_all_parameters(self) -> None:
        """Test search teams with all parameters."""
        mock_response: Dict[str, Any] = {
            "content": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Platinum Team",
                    "status": "ACTIVE",
                    "teamType": "PLATINUM",
                }
            ],
            "pageable": {"pageNumber": 1, "pageSize": 50},
            "totalElements": 1,
        }

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        result = self.client.search_teams(
            page_number=1,
            page_size=50,
            sort_direction=SortDirection.DESC,
            sort_by=[SortField.NAME, SortField.CREATED_AT],
            team_id="550e8400-e29b-41d4-a716-446655440000",
            name="Platinum Team",
            search_text="platinum",
            status=TeamStatus.ACTIVE,
            created_at_start=date(2023, 1, 1),
            created_at_end=date(2023, 12, 31),
            team_type=TeamType.PLATINUM,
        )

        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify query parameters
        request = responses.calls[0].request
        assert "pageNumber=1" in request.url
        assert "pageSize=50" in request.url
        assert "sortDirection=DESC" in request.url
        assert "sortBy=NAME" in request.url
        assert "sortBy=CREATED_AT" in request.url
        assert "id=550e8400-e29b-41d4-a716-446655440000" in request.url
        assert "name=Platinum+Team" in request.url
        assert "searchText=platinum" in request.url
        assert "status=ACTIVE" in request.url
        assert "createdAtStart=2023-01-01" in request.url
        assert "createdAtEnd=2023-12-31" in request.url
        assert "teamType=PLATINUM" in request.url

    @responses.activate
    def test_search_teams_with_string_enums(self) -> None:
        """Test search teams with string values instead of enums."""
        mock_response: Dict[str, Any] = {"content": []}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        result = self.client.search_teams(
            sort_direction="ASC",
            sort_by="NAME",
            status="INACTIVE",
            team_type="GROUP",
        )

        assert result == mock_response

        # Verify query parameters
        request = responses.calls[0].request
        assert "sortDirection=ASC" in request.url
        assert "sortBy=NAME" in request.url
        assert "status=INACTIVE" in request.url
        assert "teamType=GROUP" in request.url

    @responses.activate
    def test_search_teams_with_single_sort_field(self) -> None:
        """Test search teams with single sort field."""
        mock_response: Dict[str, Any] = {"content": []}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        result = self.client.search_teams(sort_by=SortField.STATUS)

        assert result == mock_response

        # Verify query parameters
        request = responses.calls[0].request
        assert "sortBy=STATUS" in request.url

    @responses.activate
    def test_search_teams_with_single_sort_field_string(self) -> None:
        """Test search teams with single sort field as string."""
        mock_response: Dict[str, Any] = {"content": []}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        # This should hit the missing line (single string sort field)
        result = self.client.search_teams(sort_by="LEADER_NAME")

        assert result == mock_response

        # Verify query parameters
        request = responses.calls[0].request
        assert "sortBy=LEADER_NAME" in request.url

    @responses.activate
    def test_search_teams_with_single_sort_field_string_isolated(self) -> None:
        """Test search teams with only single sort field as string."""
        mock_response: Dict[str, Any] = {"content": []}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        # Only pass sort_by as string, nothing else, to ensure we hit the else branch
        result = self.client.search_teams(sort_by="ID")

        assert result == mock_response

        # Verify query parameters
        request = responses.calls[0].request
        assert "sortBy=ID" in request.url

    @responses.activate
    def test_search_teams_with_string_dates(self) -> None:
        """Test search teams with string dates."""
        mock_response: Dict[str, Any] = {"content": []}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        result = self.client.search_teams(
            created_at_start="2023-01-01",
            created_at_end="2023-12-31",
        )

        assert result == mock_response

        # Verify query parameters
        request = responses.calls[0].request
        assert "createdAtStart=2023-01-01" in request.url
        assert "createdAtEnd=2023-12-31" in request.url

    @responses.activate
    def test_search_teams_pagination_only(self) -> None:
        """Test search teams with only pagination parameters."""
        mock_response: Dict[str, Any] = {
            "content": [],
            "pageable": {"pageNumber": 2, "pageSize": 10},
            "totalElements": 0,
        }

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        result = self.client.search_teams(page_number=2, page_size=10)

        assert result == mock_response

        # Verify query parameters
        request = responses.calls[0].request
        assert "pageNumber=2" in request.url
        assert "pageSize=10" in request.url

    @responses.activate
    def test_search_teams_validation_error(self) -> None:
        """Test search teams with validation error response."""
        error_response: Dict[str, Any] = {
            "message": "Invalid page size",
            "details": "Page size must be between 1 and 100",
        }

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=error_response,
            status=400,
        )

        with pytest.raises(ValidationError, match="Bad request: Invalid page size"):
            self.client.search_teams(page_size=0)

    @responses.activate
    def test_search_teams_authentication_error(self) -> None:
        """Test search teams with authentication error."""
        error_response: Dict[str, Any] = {"message": "Invalid API key"}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=error_response,
            status=401,
        )

        with pytest.raises(
            AuthenticationError, match="Authentication failed: Invalid API key"
        ):
            self.client.search_teams()

    @responses.activate
    def test_get_team_without_agents_success(self) -> None:
        """Test get team without agents success."""
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_response: Dict[str, Any] = {
            "id": team_id,
            "name": "Test Team",
            "status": "ACTIVE",
            "teamType": "NORMAL",
            "description": "A test team",
            "createdAt": "2023-01-01T00:00:00Z",
        }

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}/without-agents",
            json=mock_response,
            status=200,
        )

        result = self.client.get_team_without_agents(team_id)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_team_without_agents_not_found(self) -> None:
        """Test get team without agents not found."""
        team_id = "nonexistent-team-id"
        error_response: Dict[str, Any] = {"message": "Team not found"}

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}/without-agents",
            json=error_response,
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found: Team not found"):
            self.client.get_team_without_agents(team_id)

    def test_enum_values(self) -> None:
        """Test enum values are correct."""
        # Test SortDirection
        assert SortDirection.ASC.value == "ASC"
        assert SortDirection.DESC.value == "DESC"

        # Test SortField
        assert SortField.ID.value == "ID"
        assert SortField.NAME.value == "NAME"
        assert SortField.STATUS.value == "STATUS"
        assert SortField.TEAM_TYPE.value == "TEAM_TYPE"
        assert SortField.LEADER_NAME.value == "LEADER_NAME"
        assert SortField.CREATED_AT.value == "CREATED_AT"

        # Test TeamStatus
        assert TeamStatus.ACTIVE.value == "ACTIVE"
        assert TeamStatus.INACTIVE.value == "INACTIVE"

        # Test TeamType
        assert TeamType.NORMAL.value == "NORMAL"
        assert TeamType.PLATINUM.value == "PLATINUM"
        assert TeamType.GROUP.value == "GROUP"
        assert TeamType.DOMESTIC.value == "DOMESTIC"
        assert TeamType.PRO.value == "PRO"

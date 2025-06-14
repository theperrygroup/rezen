"""Tests for teams client."""

from datetime import date
from typing import Any, Dict
from unittest.mock import patch

import pytest
import responses

from rezen.enums import SortDirection
from rezen.exceptions import AuthenticationError, NotFoundError, ValidationError
from rezen.teams import (
    InvitationStatus,
    TeamsClient,
    TeamSortField,
    TeamStatus,
    TeamType,
)


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
            sort_by=[TeamSortField.NAME, TeamSortField.CREATED_AT],
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

        result = self.client.search_teams(sort_by=TeamSortField.STATUS)

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
    def test_search_teams_with_string_end_date_only(self) -> None:
        """Test search teams with string end date only to hit specific branch."""
        mock_response: Dict[str, Any] = {"content": []}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        result = self.client.search_teams(
            created_at_end="2023-12-31",  # String end date without start date
        )

        assert result == mock_response

        # Verify query parameters - this should hit the missing line 145
        request = responses.calls[0].request
        assert request.url is not None
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

        # Test TeamSortField
        assert TeamSortField.ID.value == "ID"
        assert TeamSortField.NAME.value == "NAME"
        assert TeamSortField.STATUS.value == "STATUS"
        assert TeamSortField.TEAM_TYPE.value == "TEAM_TYPE"
        assert TeamSortField.LEADER_NAME.value == "LEADER_NAME"
        assert TeamSortField.CREATED_AT.value == "CREATED_AT"

        # Test TeamStatus
        assert TeamStatus.ACTIVE.value == "ACTIVE"
        assert TeamStatus.INACTIVE.value == "INACTIVE"

        # Test TeamType
        assert TeamType.NORMAL.value == "NORMAL"
        assert TeamType.PLATINUM.value == "PLATINUM"
        assert TeamType.GROUP.value == "GROUP"
        assert TeamType.DOMESTIC.value == "DOMESTIC"
        assert TeamType.PRO.value == "PRO"

        # Test InvitationStatus
        assert InvitationStatus.EMAILED.value == "EMAILED"
        assert InvitationStatus.PENDING.value == "PENDING"
        assert InvitationStatus.ACCEPTED.value == "ACCEPTED"
        assert InvitationStatus.DECLINED.value == "DECLINED"
        assert InvitationStatus.EXPIRED.value == "EXPIRED"

    @responses.activate
    def test_search_teams_with_string_sort_by_list(self) -> None:
        """Test search teams with list of string sort fields to hit line 145."""
        mock_response: Dict[str, Any] = {"content": []}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/teams",
            json=mock_response,
            status=200,
        )

        # Use a list with string values (not enum values) to hit the else branch in line 145
        result = self.client.search_teams(
            sort_by=["NAME", "TEAM_TYPE"],  # List of strings instead of enums
        )

        assert result == mock_response

        # Verify query parameters - this should hit line 145
        request = responses.calls[0].request
        assert request.url is not None
        assert "sortBy=NAME" in request.url
        assert "sortBy=TEAM_TYPE" in request.url

    @responses.activate
    def test_invite_agent_to_team_success(self) -> None:
        """Test invite agent to team success."""
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_response: Dict[str, Any] = {
            "invitationId": "660e8400-e29b-41d4-a716-446655440001",
            "teamId": team_id,
            "firstName": "John",
            "lastName": "Doe",
            "emailAddress": "john.doe@example.com",
            "capLevel": 50000,
            "waiveFees": True,
            "status": "EMAILED",
            "pending": True,
        }

        responses.add(
            responses.POST,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}/invitation",
            json=mock_response,
            status=200,
        )

        result = self.client.invite_agent_to_team(
            team_id=team_id,
            first_name="John",
            last_name="Doe",
            email_address="john.doe@example.com",
            cap_level=50000,
            waive_fees=True,
        )

        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == {
            "firstName": "John",
            "lastName": "Doe",
            "emailAddress": "john.doe@example.com",
            "capLevel": 50000,
            "waiveFees": True,
        }

    @responses.activate
    def test_invite_agent_to_team_with_defaults(self) -> None:
        """Test invite agent to team with default waive_fees."""
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_response: Dict[str, Any] = {
            "invitationId": "660e8400-e29b-41d4-a716-446655440001",
            "teamId": team_id,
            "firstName": "Jane",
            "lastName": "Smith",
            "emailAddress": "jane.smith@example.com",
            "capLevel": 75000,
            "waiveFees": False,
            "status": "EMAILED",
        }

        responses.add(
            responses.POST,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}/invitation",
            json=mock_response,
            status=200,
        )

        result = self.client.invite_agent_to_team(
            team_id=team_id,
            first_name="Jane",
            last_name="Smith",
            email_address="jane.smith@example.com",
            cap_level=75000,
            # waive_fees defaults to False
        )

        assert result == mock_response

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body["waiveFees"] is False

    @responses.activate
    def test_invite_agent_to_team_validation_error(self) -> None:
        """Test invite agent to team with validation error."""
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        error_response: Dict[str, Any] = {
            "message": "Invalid email address format",
            "details": "Email must be a valid email address",
        }

        responses.add(
            responses.POST,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}/invitation",
            json=error_response,
            status=400,
        )

        with pytest.raises(
            ValidationError, match="Bad request: Invalid email address format"
        ):
            self.client.invite_agent_to_team(
                team_id=team_id,
                first_name="John",
                last_name="Doe",
                email_address="invalid-email",
                cap_level=50000,
            )

    @responses.activate
    def test_generate_generic_invitation_link_success(self) -> None:
        """Test generate generic invitation link success."""
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_response: Dict[str, Any] = {
            "invitationId": "770e8400-e29b-41d4-a716-446655440002",
            "invitationCreatedByAgentId": "880e8400-e29b-41d4-a716-446655440003",
            "teamId": team_id,
            "capLevel": 60000,
            "waiveFees": True,
            "expirationTime": 1640995200000,
            "couponCode": "TEAM123",
        }

        responses.add(
            responses.POST,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}/generic-link/generate",
            json=mock_response,
            status=200,
        )

        result = self.client.generate_generic_invitation_link(
            team_id=team_id,
            cap_level=60000,
            waive_fees=True,
        )

        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == {
            "teamId": team_id,
            "capLevel": 60000,
            "waiveFees": True,
        }

    @responses.activate
    def test_generate_generic_invitation_link_with_defaults(self) -> None:
        """Test generate generic invitation link with default waive_fees."""
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_response: Dict[str, Any] = {
            "invitationId": "770e8400-e29b-41d4-a716-446655440002",
            "teamId": team_id,
            "capLevel": 80000,
            "waiveFees": False,
            "couponCode": "TEAM456",
        }

        responses.add(
            responses.POST,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}/generic-link/generate",
            json=mock_response,
            status=200,
        )

        result = self.client.generate_generic_invitation_link(
            team_id=team_id,
            cap_level=80000,
            # waive_fees defaults to False
        )

        assert result == mock_response

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body["waiveFees"] is False

    @responses.activate
    def test_redeem_team_invitation_success(self) -> None:
        """Test redeem team invitation success."""
        mock_response: Dict[str, Any] = {"success": True}

        responses.add(
            responses.POST,
            "https://yenta.therealbrokerage.com/api/v1/teams/invitations/redeem",
            json=mock_response,
            status=200,
        )

        result = self.client.redeem_team_invitation(
            invitation_id="660e8400-e29b-41d4-a716-446655440001",
            application_id="990e8400-e29b-41d4-a716-446655440004",
        )

        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == {
            "invitationId": "660e8400-e29b-41d4-a716-446655440001",
            "applicationId": "990e8400-e29b-41d4-a716-446655440004",
        }

    @responses.activate
    def test_redeem_team_invitation_not_found(self) -> None:
        """Test redeem team invitation not found."""
        error_response: Dict[str, Any] = {"message": "Invitation not found"}

        responses.add(
            responses.POST,
            "https://yenta.therealbrokerage.com/api/v1/teams/invitations/redeem",
            json=error_response,
            status=404,
        )

        with pytest.raises(
            NotFoundError, match="Resource not found: Invitation not found"
        ):
            self.client.redeem_team_invitation(
                invitation_id="nonexistent-invitation-id",
                application_id="990e8400-e29b-41d4-a716-446655440004",
            )

    @responses.activate
    def test_redeem_generic_invitation_link_success(self) -> None:
        """Test redeem generic invitation link success."""
        mock_response: Dict[str, Any] = {"success": True}

        responses.add(
            responses.POST,
            "https://yenta.therealbrokerage.com/api/v1/teams/generic-link/redeem",
            json=mock_response,
            status=200,
        )

        result = self.client.redeem_generic_invitation_link(
            invitation_id="770e8400-e29b-41d4-a716-446655440002",
            application_id="990e8400-e29b-41d4-a716-446655440004",
        )

        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == {
            "invitationId": "770e8400-e29b-41d4-a716-446655440002",
            "applicationId": "990e8400-e29b-41d4-a716-446655440004",
        }

    @responses.activate
    def test_redeem_generic_invitation_link_validation_error(self) -> None:
        """Test redeem generic invitation link validation error."""
        error_response: Dict[str, Any] = {
            "message": "Invalid application ID",
            "details": "Application must be approved",
        }

        responses.add(
            responses.POST,
            "https://yenta.therealbrokerage.com/api/v1/teams/generic-link/redeem",
            json=error_response,
            status=400,
        )

        with pytest.raises(
            ValidationError, match="Bad request: Invalid application ID"
        ):
            self.client.redeem_generic_invitation_link(
                invitation_id="770e8400-e29b-41d4-a716-446655440002",
                application_id="invalid-app-id",
            )

    @responses.activate
    def test_update_invitation_with_status_enum(self) -> None:
        """Test update invitation with status enum."""
        invitation_id = "660e8400-e29b-41d4-a716-446655440001"
        mock_response: Dict[str, Any] = {
            "invitationId": invitation_id,
            "status": "ACCEPTED",
            "teamInvitationEmailStatus": "EMAILED",
            "pending": False,
        }

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/teams/invitation/{invitation_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.update_invitation(
            invitation_id=invitation_id,
            status=InvitationStatus.ACCEPTED,
            team_invitation_email_status=InvitationStatus.EMAILED,
        )

        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == {
            "invitationId": invitation_id,
            "status": "ACCEPTED",
            "teamInvitationEmailStatus": "EMAILED",
        }

    @responses.activate
    def test_update_invitation_with_status_string(self) -> None:
        """Test update invitation with status string."""
        invitation_id = "660e8400-e29b-41d4-a716-446655440001"
        mock_response: Dict[str, Any] = {
            "invitationId": invitation_id,
            "status": "DECLINED",
            "pending": False,
        }

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/teams/invitation/{invitation_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.update_invitation(
            invitation_id=invitation_id,
            status="DECLINED",
        )

        assert result == mock_response

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == {
            "invitationId": invitation_id,
            "status": "DECLINED",
        }

    @responses.activate
    def test_update_invitation_minimal(self) -> None:
        """Test update invitation with minimal parameters."""
        invitation_id = "660e8400-e29b-41d4-a716-446655440001"
        mock_response: Dict[str, Any] = {
            "invitationId": invitation_id,
            "status": "PENDING",
        }

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/teams/invitation/{invitation_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.update_invitation(invitation_id=invitation_id)

        assert result == mock_response

        # Verify request body contains only invitation ID
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == {"invitationId": invitation_id}

    @responses.activate
    def test_update_invitation_with_email_status_only(self) -> None:
        """Test update invitation with only email status."""
        invitation_id = "660e8400-e29b-41d4-a716-446655440001"
        mock_response: Dict[str, Any] = {
            "invitationId": invitation_id,
            "teamInvitationEmailStatus": "PENDING",
        }

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/teams/invitation/{invitation_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.update_invitation(
            invitation_id=invitation_id,
            team_invitation_email_status="PENDING",
        )

        assert result == mock_response

        # Verify request body
        import json

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == {
            "invitationId": invitation_id,
            "teamInvitationEmailStatus": "PENDING",
        }

    @responses.activate
    def test_get_team_success(self) -> None:
        """Test get team with full information success."""
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_response: Dict[str, Any] = {
            "id": team_id,
            "name": "Test Team",
            "status": "ACTIVE",
            "teamType": "NORMAL",
            "agents": [
                {
                    "id": "agent-1",
                    "agent": {
                        "firstName": "John",
                        "lastName": "Doe",
                        "emailAddress": "john.doe@example.com",
                    },
                    "roles": ["MEMBER"],
                }
            ],
        }

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.get_team(team_id)
        assert result == mock_response

    @responses.activate
    def test_get_team_members_success(self) -> None:
        """Test get team members success."""
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_response: Dict[str, Any] = {
            "members": [
                {
                    "id": "member-1",
                    "name": "John Doe",
                    "role": "MEMBER",
                    "email": "john.doe@example.com",
                }
            ]
        }

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/teams/{team_id}/members",
            json=mock_response,
            status=200,
        )

        result = self.client.get_team_members(team_id)
        assert result == mock_response

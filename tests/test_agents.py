"""Tests for AgentsClient."""

from datetime import date

import pytest
import responses

from rezen.agents import AgentsClient, AgentSortField, AgentStatus
from rezen.enums import Country, SortDirection, StateOrProvince
from rezen.exceptions import AuthenticationError, ValidationError


class TestAgentsClient:
    """Test cases for AgentsClient."""

    @pytest.fixture
    def client(self) -> AgentsClient:
        """Create AgentsClient instance for testing."""
        return AgentsClient(api_key="test_api_key")

    def test_client_initialization(self) -> None:
        """Test AgentsClient initialization."""
        client = AgentsClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://yenta.therealbrokerage.com/api/v1"

    def test_client_initialization_with_custom_base_url(self) -> None:
        """Test AgentsClient initialization with custom base URL."""
        custom_url = "https://test.example.com/api/v1"
        client = AgentsClient(api_key="test_key", base_url=custom_url)
        assert client.base_url == custom_url

    @responses.activate
    def test_get_agents_by_email(self, client: AgentsClient) -> None:
        """Test getting agents by email address."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents",
            json=[{"id": "agent-123", "email": "test@example.com", "name": "John Doe"}],
            status=200,
        )

        result = client.get_agents_by_email("test@example.com")

        assert len(responses.calls) == 1
        assert "emailAddress=test%40example.com" in responses.calls[0].request.url
        # Cast result to list for test - the mocked API returns a list directly
        agents_list = result  # type: ignore[assignment]
        assert agents_list[0]["id"] == "agent-123"
        assert agents_list[0]["email"] == "test@example.com"

    @responses.activate
    def test_get_sponsor_tree(self, client: AgentsClient) -> None:
        """Test getting agent's sponsor tree."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/sponsor-tree",
            json={"agentId": agent_id, "sponsorTree": []},
            status=200,
        )

        result = client.get_sponsor_tree(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_profile_score(self, client: AgentsClient) -> None:
        """Test getting user's profile score."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/profile-score",
            json={"agentId": agent_id, "score": 85},
            status=200,
        )

        result = client.get_profile_score(agent_id)

        assert len(responses.calls) == 1
        assert result["score"] == 85

    @responses.activate
    def test_get_front_line_agents_info(self, client: AgentsClient) -> None:
        """Test getting front line agents info."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/front-line-agents-info",
            json={"agentId": agent_id, "frontLineAgents": []},
            status=200,
        )

        result = client.get_front_line_agents_info(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_down_line_agents(self, client: AgentsClient) -> None:
        """Test getting downline agents with various parameters."""
        agent_id = "agent-123"
        tier = 1

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/down-line/{tier}",
            json={"agentId": agent_id, "tier": tier, "agents": []},
            status=200,
        )

        # Test with minimal parameters
        result = client.get_down_line_agents(agent_id, tier)
        assert result["tier"] == tier

        # Test with all parameters
        result = client.get_down_line_agents(
            agent_id=agent_id,
            tier=tier,
            updated_at_from=date(2025, 1, 1),
            updated_at_to=date(2025, 1, 31),
            status_in=[AgentStatus.ACTIVE, AgentStatus.INACTIVE],
            page_number=0,
            page_size=20,
        )

        # Verify parameters were included in request
        request_url = responses.calls[-1].request.url
        assert "updatedAtFrom=2025-01-01" in request_url
        assert "updatedAtTo=2025-01-31" in request_url
        assert "statusIn=ACTIVE" in request_url
        assert "statusIn=INACTIVE" in request_url
        assert "pageNumber=0" in request_url
        assert "pageSize=20" in request_url

    @responses.activate
    def test_get_will_beneficiary_typed(self, client: AgentsClient) -> None:
        """Test getting agent's will beneficiary."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/will-beneficiary-typed",
            json={"agentId": agent_id, "beneficiary": "John Doe"},
            status=200,
        )

        result = client.get_will_beneficiary_typed(agent_id)

        assert len(responses.calls) == 1
        assert result["beneficiary"] == "John Doe"

    @responses.activate
    def test_get_tax_forms_summary(self, client: AgentsClient) -> None:
        """Test getting tax forms summary."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/tax-forms/summary",
            json={"agentId": agent_id, "summary": {}},
            status=200,
        )

        result = client.get_tax_forms_summary(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_tax_forms_lite(self, client: AgentsClient) -> None:
        """Test getting all tax forms lite."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/tax-forms-lite",
            json={"agentId": agent_id, "taxForms": []},
            status=200,
        )

        result = client.get_tax_forms_lite(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_tax_form_lite(self, client: AgentsClient) -> None:
        """Test getting specific tax form lite."""
        agent_id = "agent-123"
        tax_form_id = "form-456"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/tax-forms-lite/{tax_form_id}",
            json={"agentId": agent_id, "taxFormId": tax_form_id},
            status=200,
        )

        result = client.get_tax_form_lite(agent_id, tax_form_id)

        assert len(responses.calls) == 1
        assert result["taxFormId"] == tax_form_id

    @responses.activate
    def test_get_latest_personal_tax_form_lite(self, client: AgentsClient) -> None:
        """Test getting latest personal tax form lite."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/tax-forms-lite/latest-personal",
            json={"agentId": agent_id, "latestForm": {}},
            status=200,
        )

        result = client.get_latest_personal_tax_form_lite(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_search_payment_settings(self, client: AgentsClient) -> None:
        """Test searching payment settings history."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/payment-settings/history",
            json={"agentId": agent_id, "history": []},
            status=200,
        )

        result = client.search_payment_settings(
            agent_id=agent_id,
            page_number=0,
            page_size=10,
            sort_direction=SortDirection.DESC,
        )

        request_url = responses.calls[0].request.url
        assert "pageNumber=0" in request_url
        assert "pageSize=10" in request_url
        assert "sortDirection=DESC" in request_url
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_payment_details(self, client: AgentsClient) -> None:
        """Test getting payment details."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/payment-details",
            json={"agentId": agent_id, "paymentDetails": {}},
            status=200,
        )

        result = client.get_payment_details(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_payment_details_payable_info(self, client: AgentsClient) -> None:
        """Test getting payment details payable info."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/payment-details/payable-info",
            json={"agentId": agent_id, "payableInfo": {}},
            status=200,
        )

        result = client.get_payment_details_payable_info(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_network_size_by_tier(self, client: AgentsClient) -> None:
        """Test getting network size by tier."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/network-size-by-tier",
            json={"agentId": agent_id, "networkSizes": {}},
            status=200,
        )

        result = client.get_network_size_by_tier(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_masked_tax_forms_lite(self, client: AgentsClient) -> None:
        """Test getting masked tax forms lite."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/masked-tax-forms-lite",
            json={"agentId": agent_id, "maskedForms": []},
            status=200,
        )

        result = client.get_masked_tax_forms_lite(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_masked_payment_methods(self, client: AgentsClient) -> None:
        """Test getting masked payment methods."""
        agent_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}/masked-payment-methods",
            json={"agentId": agent_id, "paymentMethods": []},
            status=200,
        )

        result = client.get_masked_payment_methods(agent_id)

        assert len(responses.calls) == 1
        assert result["agentId"] == agent_id

    @responses.activate
    def test_get_tipalti_url(self, client: AgentsClient) -> None:
        """Test getting Tipalti URL."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/tipaltiUrl",
            json={"url": "https://example.tipalti.com"},
            status=200,
        )

        result = client.get_tipalti_url()

        assert len(responses.calls) == 1
        assert result["url"] == "https://example.tipalti.com"

    @responses.activate
    def test_is_slug_available(self, client: AgentsClient) -> None:
        """Test checking slug availability."""
        slug = "test-slug"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/slugs/{slug}/available",
            json={"slug": slug, "available": True},
            status=200,
        )

        result = client.is_slug_available(slug)

        assert len(responses.calls) == 1
        assert result["available"] is True

    @responses.activate
    def test_search_active_agents(self, client: AgentsClient) -> None:
        """Test searching active agents with various filters."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json={"agents": [], "totalCount": 0},
            status=200,
        )

        result = client.search_active_agents(
            page_number=0,
            page_size=50,
            sort_direction=SortDirection.ASC,
            sort_by=[AgentSortField.FIRST_NAME, AgentSortField.LAST_NAME],
            name="John",
            non_reportable=[False],
            country=[Country.UNITED_STATES],
            state_or_province=[StateOrProvince.CALIFORNIA, StateOrProvince.NEW_YORK],
        )

        request_url = responses.calls[0].request.url
        assert "pageNumber=0" in request_url
        assert "pageSize=50" in request_url
        assert "sortDirection=ASC" in request_url
        assert "sortBy=FIRST_NAME" in request_url
        assert "sortBy=LAST_NAME" in request_url
        assert "name=John" in request_url
        assert "nonReportable=False" in request_url
        assert "country=UNITED_STATES" in request_url
        assert "stateOrProvince=CALIFORNIA" in request_url
        assert "stateOrProvince=NEW_YORK" in request_url

    @responses.activate
    def test_get_agents_referral_central_details(self, client: AgentsClient) -> None:
        """Test getting agents referral central details."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/referral-central",
            json={"agents": [], "totalCount": 0},
            status=200,
        )

        result = client.get_agents_referral_central_details(
            agent_ids=["agent-123", "agent-456"], page_number=0, page_size=20
        )

        request_url = responses.calls[0].request.url
        assert "agentIds=agent-123" in request_url
        assert "agentIds=agent-456" in request_url
        assert "pageNumber=0" in request_url
        assert "pageSize=20" in request_url

    @responses.activate
    def test_get_revenue_share_plan(self, client: AgentsClient) -> None:
        """Test getting revenue share plan."""
        plan_id = "plan-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/plans/revenue_share/{plan_id}",
            json={"planId": plan_id, "type": "revenue_share"},
            status=200,
        )

        result = client.get_revenue_share_plan(plan_id)

        assert len(responses.calls) == 1
        assert result["planId"] == plan_id

    @responses.activate
    def test_get_equity_purchase_plan(self, client: AgentsClient) -> None:
        """Test getting equity purchase plan."""
        plan_id = "plan-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/plans/equity_purchase/{plan_id}",
            json={"planId": plan_id, "type": "equity_purchase"},
            status=200,
        )

        result = client.get_equity_purchase_plan(plan_id)

        assert len(responses.calls) == 1
        assert result["planId"] == plan_id

    @responses.activate
    def test_get_equity_award_plan(self, client: AgentsClient) -> None:
        """Test getting equity award plan."""
        plan_id = "plan-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/plans/equity_award/{plan_id}",
            json={"planId": plan_id, "type": "equity_award"},
            status=200,
        )

        result = client.get_equity_award_plan(plan_id)

        assert len(responses.calls) == 1
        assert result["planId"] == plan_id

    @responses.activate
    def test_get_elite_equity_award_plan(self, client: AgentsClient) -> None:
        """Test getting elite equity award plan."""
        plan_id = "plan-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/plans/elite_equity_award/{plan_id}",
            json={"planId": plan_id, "type": "elite_equity_award"},
            status=200,
        )

        result = client.get_elite_equity_award_plan(plan_id)

        assert len(responses.calls) == 1
        assert result["planId"] == plan_id

    @responses.activate
    def test_get_commission_plan(self, client: AgentsClient) -> None:
        """Test getting commission plan."""
        plan_id = "plan-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/plans/commission/{plan_id}",
            json={"planId": plan_id, "type": "commission"},
            status=200,
        )

        result = client.get_commission_plan(plan_id)

        assert len(responses.calls) == 1
        assert result["planId"] == plan_id

    @responses.activate
    def test_get_official_commission_plan(self, client: AgentsClient) -> None:
        """Test getting official commission plan."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/plans/commission/official",
            json={"type": "official_commission"},
            status=200,
        )

        result = client.get_official_commission_plan()

        assert len(responses.calls) == 1
        assert result["type"] == "official_commission"

    @responses.activate
    def test_get_commission_plan_basic_info(self, client: AgentsClient) -> None:
        """Test getting commission plan basic info."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/plans/commission/basic-info",
            json={"type": "commission_basic_info"},
            status=200,
        )

        result = client.get_commission_plan_basic_info()

        assert len(responses.calls) == 1
        assert result["type"] == "commission_basic_info"

    @responses.activate
    def test_get_opcity_info(self, client: AgentsClient) -> None:
        """Test getting OpCity info."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/opcity",
            json={"opcityInfo": {}},
            status=200,
        )

        result = client.get_opcity_info()

        assert len(responses.calls) == 1
        assert "opcityInfo" in result

    @responses.activate
    def test_get_me(self, client: AgentsClient) -> None:
        """Test getting current user's agent info."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/me",
            json={"id": "current-agent", "name": "Current User"},
            status=200,
        )

        result = client.get_me()

        assert len(responses.calls) == 1
        assert result["id"] == "current-agent"

    @responses.activate
    def test_get_loi_agent(self, client: AgentsClient) -> None:
        """Test getting LOI agent."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/loiAgent",
            json={"id": "loi-agent", "name": "LOI Agent"},
            status=200,
        )

        result = client.get_loi_agent()

        assert len(responses.calls) == 1
        assert result["id"] == "loi-agent"

    @responses.activate
    def test_get_license_images(self, client: AgentsClient) -> None:
        """Test getting license images."""
        license_id = "license-123"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/license/{license_id}/images",
            json={"licenseId": license_id, "images": []},
            status=200,
        )

        result = client.get_license_images(license_id)

        assert len(responses.calls) == 1
        assert result["licenseId"] == license_id

    @responses.activate
    def test_get_agents_by_ids(self, client: AgentsClient) -> None:
        """Test getting agents by IDs."""
        agent_ids = ["agent-123", "agent-456"]
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/ids",
            json={"agents": [{"id": "agent-123"}, {"id": "agent-456"}]},
            status=200,
        )

        result = client.get_agents_by_ids(agent_ids)

        request_url = responses.calls[0].request.url
        assert "agentIds=agent-123" in request_url
        assert "agentIds=agent-456" in request_url

    def test_get_agents_by_ids_too_many(self, client: AgentsClient) -> None:
        """Test validation error when too many agent IDs provided."""
        agent_ids = [f"agent-{i}" for i in range(25)]  # More than 20

        with pytest.raises(ValidationError) as exc_info:
            client.get_agents_by_ids(agent_ids)

        assert "Maximum of 20 agent IDs allowed" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        assert exc_info.value.response_data is not None
        assert exc_info.value.response_data["agent_ids_count"] == 25

    @responses.activate
    def test_get_comment_details(self, client: AgentsClient) -> None:
        """Test getting comment details."""
        keymaker_ids = "key1,key2,key3"
        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/agents/comment-details/{keymaker_ids}",
            json={"keymakerIds": keymaker_ids, "comments": []},
            status=200,
        )

        result = client.get_comment_details(keymaker_ids)

        assert len(responses.calls) == 1
        assert result["keymakerIds"] == keymaker_ids

    @responses.activate
    def test_get_agents_by_anniversary(self, client: AgentsClient) -> None:
        """Test getting agents by anniversary."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/by-anniversary",
            json={"agents": [], "totalCount": 0},
            status=200,
        )

        result = client.get_agents_by_anniversary(page_number=0, page_size=10)

        request_url = responses.calls[0].request.url
        assert "pageNumber=0" in request_url
        assert "pageSize=10" in request_url

    @responses.activate
    def test_get_active_agents(self, client: AgentsClient) -> None:
        """Test getting active agents."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/active",
            json={"agents": [], "totalCount": 0},
            status=200,
        )

        result = client.get_active_agents(page_number=1, page_size=25)

        request_url = responses.calls[0].request.url
        assert "pageNumber=1" in request_url
        assert "pageSize=25" in request_url

    @responses.activate
    def test_get_active_agent_ids(self, client: AgentsClient) -> None:
        """Test getting active agent IDs."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/active-agent-ids",
            json={"agentIds": ["agent-123", "agent-456"]},
            status=200,
        )

        result = client.get_active_agent_ids()

        assert len(responses.calls) == 1
        assert len(result["agentIds"]) == 2

    @responses.activate
    def test_authentication_error(self, client: AgentsClient) -> None:
        """Test authentication error handling."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/me",
            json={"error": "Unauthorized"},
            status=401,
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client.get_me()

        assert exc_info.value.status_code == 401

    def test_agents_enums(self) -> None:
        """Test agent enums have correct values."""
        assert AgentStatus.ACTIVE.value == "ACTIVE"
        assert AgentStatus.INACTIVE.value == "INACTIVE"
        assert SortDirection.ASC.value == "ASC"
        assert AgentSortField.FIRST_NAME.value == "FIRST_NAME"
        assert Country.UNITED_STATES.value == "UNITED_STATES"
        assert StateOrProvince.CALIFORNIA.value == "CALIFORNIA"

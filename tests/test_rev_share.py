"""Tests for RevShareClient."""

from datetime import date

import pytest
import responses

from rezen.exceptions import NotFoundError
from rezen.rev_share import RevShareClient


class TestRevShareClient:
    """Test cases for RevShareClient."""

    @pytest.fixture
    def client(self) -> RevShareClient:
        """Create RevShareClient instance for testing."""
        return RevShareClient(api_key="test_api_key")

    def test_client_initialization(self) -> None:
        """Test RevShareClient initialization."""
        client = RevShareClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://arrakis.therealbrokerage.com/api/v1"

    @responses.activate
    def test_get_payments_for_agent(self, client: RevShareClient) -> None:
        """get_payments_for_agent should call the correct endpoint."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://arrakis.therealbrokerage.com/api/v1/revshares/{yenta_id}/payments",
            json={"payments": []},
            status=200,
        )

        result = client.get_payments_for_agent(yenta_id)

        assert result == {"payments": []}
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_payments_for_agent_with_pagination(
        self, client: RevShareClient
    ) -> None:
        """get_payments_for_agent should include optional pagination params."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://arrakis.therealbrokerage.com/api/v1/revshares/{yenta_id}/payments",
            json={"payments": []},
            status=200,
        )

        result = client.get_payments_for_agent(yenta_id, page_number=1, page_size=50)

        assert result == {"payments": []}
        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "pageNumber=1" in request_url
        assert "pageSize=50" in request_url

    @responses.activate
    def test_get_payment_by_id(self, client: RevShareClient) -> None:
        """get_payment_by_id should call the correct endpoint."""
        yenta_id = "agent-123"
        outgoing_payment_id = "payment-456"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/{outgoing_payment_id}",
            json={"id": outgoing_payment_id},
            status=200,
        )

        result = client.get_payment_by_id(yenta_id, outgoing_payment_id)

        assert result == {"id": outgoing_payment_id}
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_payment_by_id_with_pagination(self, client: RevShareClient) -> None:
        """get_payment_by_id should include optional pagination params."""
        yenta_id = "agent-123"
        outgoing_payment_id = "payment-456"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/{outgoing_payment_id}",
            json={"id": outgoing_payment_id},
            status=200,
        )

        result = client.get_payment_by_id(
            yenta_id, outgoing_payment_id, page_number=2, page_size=25
        )

        assert result == {"id": outgoing_payment_id}
        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "pageNumber=2" in request_url
        assert "pageSize=25" in request_url

    @responses.activate
    def test_get_payment_export_for_agent(self, client: RevShareClient) -> None:
        """get_payment_export_for_agent should return CSV as text."""
        yenta_id = "agent-123"
        outgoing_payment_id = "payment-456"
        csv_body = "a,b\n1,2\n"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/{outgoing_payment_id}/export",
            body=csv_body,
            status=200,
            content_type="text/csv",
        )

        result = client.get_payment_export_for_agent(yenta_id, outgoing_payment_id)

        assert result == csv_body
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_payment_export_for_agent_empty(self, client: RevShareClient) -> None:
        """Export endpoints should safely handle a 204 empty response."""
        yenta_id = "agent-123"
        outgoing_payment_id = "payment-456"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/{outgoing_payment_id}/export",
            status=204,
        )

        assert client.get_payment_export_for_agent(yenta_id, outgoing_payment_id) == ""

    @responses.activate
    def test_get_pending_payment_for_agent(self, client: RevShareClient) -> None:
        """get_pending_payment_for_agent should call the correct endpoint."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/pending",
            json={"pending": True},
            status=200,
        )

        result = client.get_pending_payment_for_agent(yenta_id)
        assert result == {"pending": True}

    @responses.activate
    def test_get_pending_payment_for_agent_with_pagination(
        self, client: RevShareClient
    ) -> None:
        """get_pending_payment_for_agent should include optional pagination params."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/pending",
            json={"pending": True},
            status=200,
        )

        result = client.get_pending_payment_for_agent(
            yenta_id, page_number=1, page_size=10
        )
        assert result == {"pending": True}

        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "pageNumber=1" in request_url
        assert "pageSize=10" in request_url

    @responses.activate
    def test_get_pending_payment_export_for_agent(self, client: RevShareClient) -> None:
        """get_pending_payment_export_for_agent should return CSV as text."""
        yenta_id = "agent-123"
        csv_body = "pending\n"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/pending/export",
            body=csv_body,
            status=200,
            content_type="text/csv",
        )

        assert client.get_pending_payment_export_for_agent(yenta_id) == csv_body

    @responses.activate
    def test_get_pending_payment_preview_for_agent(
        self, client: RevShareClient
    ) -> None:
        """get_pending_payment_preview_for_agent should call the correct endpoint."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/pending-overview",
            json={"overview": True},
            status=200,
        )

        assert client.get_pending_payment_preview_for_agent(yenta_id) == {
            "overview": True
        }

    @responses.activate
    def test_get_contributors_by_tier(self, client: RevShareClient) -> None:
        """get_contributors_by_tier should include pagination + date filters when provided."""
        yenta_id = "agent-123"
        tier = 1
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/contributors/{tier}",
            json={"contributors": []},
            status=200,
        )

        result = client.get_contributors_by_tier(
            yenta_id,
            tier,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            page_number=0,
            page_size=20,
        )

        assert result == {"contributors": []}
        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "startDate=2025-01-01" in request_url
        assert "endDate=2025-01-31" in request_url
        assert "pageNumber=0" in request_url
        assert "pageSize=20" in request_url

    @responses.activate
    def test_get_contributions_by_tier(self, client: RevShareClient) -> None:
        """get_contributions_by_tier should support the missed filter."""
        yenta_id = "agent-123"
        tier = 2
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/contributions/{tier}",
            json={"contributions": []},
            status=200,
        )

        result = client.get_contributions_by_tier(
            yenta_id,
            tier,
            start_date=date(2025, 2, 1),
            end_date=date(2025, 2, 28),
            missed=True,
        )

        assert result == {"contributions": []}
        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "startDate=2025-02-01" in request_url
        assert "endDate=2025-02-28" in request_url
        assert "missed=True" in request_url

    @responses.activate
    def test_get_by_tier(self, client: RevShareClient) -> None:
        """get_by_tier should omit date filters when not provided."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://arrakis.therealbrokerage.com/api/v1/revshares/{yenta_id}/by-tier",
            json={"tiers": []},
            status=200,
        )

        result = client.get_by_tier(yenta_id)
        assert result == {"tiers": []}

        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "startDate=" not in request_url
        assert "endDate=" not in request_url

    @responses.activate
    def test_get_by_tier_with_date_filters(self, client: RevShareClient) -> None:
        """get_by_tier should include date filters when provided."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://arrakis.therealbrokerage.com/api/v1/revshares/{yenta_id}/by-tier",
            json={"tiers": []},
            status=200,
        )

        result = client.get_by_tier(
            yenta_id, start_date=date(2025, 3, 1), end_date=date(2025, 3, 31)
        )
        assert result == {"tiers": []}

        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "startDate=2025-03-01" in request_url
        assert "endDate=2025-03-31" in request_url

    @responses.activate
    def test_get_history(self, client: RevShareClient) -> None:
        """get_history should include required date filters."""
        agent_yenta_id = "agent-123"
        responses.add(
            responses.GET,
            f"https://arrakis.therealbrokerage.com/api/v1/revshares/{agent_yenta_id}/history",
            json={"history": []},
            status=200,
        )

        result = client.get_history(
            agent_yenta_id, start_date=date(2025, 1, 1), end_date=date(2025, 12, 31)
        )
        assert result == {"history": []}

        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "startDate=2025-01-01" in request_url
        assert "endDate=2025-12-31" in request_url

    @responses.activate
    def test_get_monthly_performance(self, client: RevShareClient) -> None:
        """get_monthly_performance should support the optional month filter."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share",
            json={"month": "current"},
            status=200,
        )

        result = client.get_monthly_performance(yenta_id, month="current")
        assert result == {"month": "current"}

        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "month=current" in request_url

    @responses.activate
    def test_get_monthly_performance_without_month(
        self, client: RevShareClient
    ) -> None:
        """get_monthly_performance should omit month when not provided."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share",
            json={"month": "current"},
            status=200,
        )

        result = client.get_monthly_performance(yenta_id)
        assert result == {"month": "current"}

        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "month=" not in request_url

    @responses.activate
    def test_get_current_performance(self, client: RevShareClient) -> None:
        """get_current_performance should call the correct endpoint."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={"overview": True},
            status=200,
        )

        assert client.get_current_performance(yenta_id) == {"overview": True}

    @responses.activate
    def test_export_raises_for_not_found(self, client: RevShareClient) -> None:
        """Export helpers should raise Rezen exceptions for non-2xx responses."""
        yenta_id = "agent-123"
        outgoing_payment_id = "payment-456"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/{yenta_id}/payments/{outgoing_payment_id}/export",
            json={"message": "Not found"},
            status=404,
        )

        with pytest.raises(NotFoundError):
            client.get_payment_export_for_agent(yenta_id, outgoing_payment_id)

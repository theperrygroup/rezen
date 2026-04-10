"""Tests for RevShareClient."""

from datetime import date
import json
from typing import Any
from urllib.parse import parse_qs, urlparse

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
        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "pageNumber=0" in request_url
        assert "pageSize=20" in request_url

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
        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "pageNumber=0" in request_url
        assert "pageSize=20" in request_url

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
        """get_contributors_by_tier should include required date filters + pagination."""
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
        assert request_url.index("startDate=") < request_url.index("endDate=")
        assert request_url.index("endDate=") < request_url.index("pageNumber=")
        assert request_url.index("pageNumber=") < request_url.index("pageSize=")

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
    def test_get_earnings_per_agent_per_tier_aggregates_contributions(
        self, client: RevShareClient
    ) -> None:
        """Earnings helpers should aggregate contribution amounts per agent per tier."""
        yenta_id = "agent-123"
        base_url = "https://arrakis.therealbrokerage.com/api/v1"
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)

        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/1",
            json={
                "contributions": [
                    {"agentYentaId": "a1", "payout": 100},
                    {"agentYentaId": "a2", "payout": {"amount": "50.00", "currency": "USD"}},
                    {"agentYentaId": "a1", "payoutAmount": 25},
                ]
            },
            status=200,
        )
        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/2",
            json={
                "contributions": [
                    {"contributorYentaId": "a1", "paymentAmount": 10},
                    {"contributorYentaId": "a3", "amount": "5"},
                ]
            },
            status=200,
        )

        result = client.get_earnings_per_agent_per_tier(
            yenta_id,
            tiers=[1, 2],
            start_date=start_date,
            end_date=end_date,
            page_size=50,
        )

        assert result == {
            1: {"a1": 125.0, "a2": 50.0},
            2: {"a1": 10.0, "a3": 5.0},
        }
        assert len(responses.calls) == 2

        request_url_1 = responses.calls[0].request.url
        request_url_2 = responses.calls[1].request.url
        assert request_url_1 is not None
        assert request_url_2 is not None
        assert "pageNumber=0" in request_url_1
        assert "pageSize=50" in request_url_1
        assert "startDate=2025-01-01" in request_url_1
        assert "endDate=2025-01-31" in request_url_1
        assert "pageNumber=0" in request_url_2
        assert "pageSize=50" in request_url_2

    @responses.activate
    def test_get_earnings_per_tier_aggregates_across_agents_in_tier(
        self, client: RevShareClient
    ) -> None:
        """get_earnings_per_tier should roll up all agents within each tier."""
        yenta_id = "agent-123"
        base_url = "https://arrakis.therealbrokerage.com/api/v1"
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)

        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/1",
            json={
                "contributions": [
                    {"agentYentaId": "a1", "payout": 100},
                    {"agentYentaId": "a2", "payout": {"amount": "50.00", "currency": "USD"}},
                    {"agentYentaId": "a1", "payoutAmount": 25},
                ]
            },
            status=200,
        )
        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/2",
            json={
                "contributions": [
                    {"contributorYentaId": "a1", "paymentAmount": 10},
                    {"contributorYentaId": "a3", "amount": "5"},
                ]
            },
            status=200,
        )

        totals_by_tier = client.get_earnings_per_tier(
            yenta_id,
            tiers=[1, 2],
            start_date=start_date,
            end_date=end_date,
            page_size=50,
        )
        assert totals_by_tier == {1: 175.0, 2: 15.0}

    @responses.activate
    def test_get_earnings_per_agent_aggregates_across_tiers(
        self, client: RevShareClient
    ) -> None:
        """get_earnings_per_agent should roll up per-tier earnings into totals."""
        yenta_id = "agent-123"
        base_url = "https://arrakis.therealbrokerage.com/api/v1"

        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/1",
            json={"contributions": [{"agentYentaId": "a1", "payout": 100}]},
            status=200,
        )
        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/2",
            json={"contributions": [{"agentYentaId": "a1", "payout": 25}, {"agentYentaId": "a2", "payout": 10}]},
            status=200,
        )

        totals = client.get_earnings_per_agent(yenta_id, tiers=[1, 2], page_size=200)
        assert totals == {"a1": 125.0, "a2": 10.0}

    @responses.activate
    def test_get_earnings_per_agent_per_tier_paginates_until_empty(
        self, client: RevShareClient
    ) -> None:
        """Earnings helpers should request subsequent pages when needed."""
        yenta_id = "agent-123"
        base_url = "https://arrakis.therealbrokerage.com/api/v1"
        url = f"{base_url}/revshares/{yenta_id}/contributions/1"

        def callback(request: Any) -> Any:
            query = parse_qs(urlparse(request.url).query)
            page = int(query.get("pageNumber", ["0"])[0])
            if page == 0:
                payload = {
                    "contributions": [
                        {"agentYentaId": "a1", "payout": 1},
                        {"agentYentaId": "a1", "payout": 2},
                    ]
                }
            else:
                payload = {"contributions": []}
            return (200, {"Content-Type": "application/json"}, json.dumps(payload))

        responses.add_callback(responses.GET, url, callback=callback)

        result = client.get_earnings_per_agent_per_tier(
            yenta_id, tiers=[1], page_size=2, max_pages=10
        )
        assert result == {1: {"a1": 3.0}}
        assert len(responses.calls) == 2

    @responses.activate
    def test_get_earnings_per_agent_per_tier_supports_list_payload_and_nested_agent(
        self, client: RevShareClient
    ) -> None:
        """Earnings helpers should support list payloads and nested agent identifiers."""
        yenta_id = "agent-123"
        base_url = "https://arrakis.therealbrokerage.com/api/v1"
        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/1",
            json=[
                {"agent": {"yentaId": "nested-1"}, "payout": 10},
                {"contributor": {"id": "nested-2"}, "payoutAmount": "5"},
            ],
            status=200,
        )

        result = client.get_earnings_per_agent_per_tier(yenta_id, tiers=[1], page_size=50)
        assert result == {1: {"nested-1": 10.0, "nested-2": 5.0}}

    @responses.activate
    def test_get_earnings_per_agent_per_tier_skips_missing_agent_or_amount(
        self, client: RevShareClient
    ) -> None:
        """Records without an agent id or amount should be ignored."""
        yenta_id = "agent-123"
        base_url = "https://arrakis.therealbrokerage.com/api/v1"
        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/1",
            json={
                "contributions": [
                    {"payout": 1},  # missing agent identifier
                    {"agentYentaId": "a1"},  # missing amount
                    {"agentYentaId": "a1", "payout": 2},
                ]
            },
            status=200,
        )

        result = client.get_earnings_per_agent_per_tier(yenta_id, tiers=[1], page_size=50)
        assert result == {1: {"a1": 2.0}}

    @responses.activate
    def test_get_earnings_per_agent_per_tier_handles_null_and_unexpected_payloads(
        self, client: RevShareClient
    ) -> None:
        """Null/unexpected shapes should result in empty tier mappings."""
        yenta_id = "agent-123"
        base_url = "https://arrakis.therealbrokerage.com/api/v1"
        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/1",
            body="null",
            status=200,
            content_type="application/json",
        )
        responses.add(
            responses.GET,
            f"{base_url}/revshares/{yenta_id}/contributions/2",
            json={"foo": []},
            status=200,
        )

        result = client.get_earnings_per_agent_per_tier(yenta_id, tiers=[1, 2], page_size=50)
        assert result == {1: {}, 2: {}}

    @responses.activate
    def test_get_by_tier(self, client: RevShareClient) -> None:
        """get_by_tier should include required date filters."""
        yenta_id = "bd465129-b224-43e3-b92f-524ea5f53783"
        start_date = date(2025, 11, 30)
        end_date = date(2025, 12, 30)
        responses.add(
            responses.GET,
            f"https://arrakis.therealbrokerage.com/api/v1/revshares/{yenta_id}/by-tier",
            json={"tiers": []},
            status=200,
        )

        result = client.get_by_tier(yenta_id, start_date=start_date, end_date=end_date)
        assert result == {"tiers": []}

        request_url = responses.calls[0].request.url
        assert request_url is not None
        assert "startDate=2025-11-30" in request_url
        assert "endDate=2025-12-30" in request_url

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
    def test_get_current_performance_adds_average_monthly_payout_from_list(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should add averageMonthlyPayout when derivable."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={
                "monthlyPayouts": [
                    {
                        "month": "2025-01",
                        "payout": {"amount": "1000.00", "currency": "USD"},
                    },
                    {"month": "2025-02", "payout": 500},
                ]
            },
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert result["averageMonthlyPayout"] == pytest.approx(750.0)

    @responses.activate
    def test_get_current_performance_adds_average_monthly_payout_from_mapping(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should support month->payout mapping payloads."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={"payoutsByMonth": {"2025-01": 1000, "2025-02": 500}},
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert result["averageMonthlyPayout"] == pytest.approx(750.0)

    @responses.activate
    def test_get_current_performance_adds_average_monthly_payout_from_totals(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should support total payout / month count payloads."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={"totalPayout": 1200, "monthCount": 3},
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert result["averageMonthlyPayout"] == pytest.approx(400.0)

    @responses.activate
    def test_get_current_performance_does_not_override_existing_average(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should not override averageMonthlyPayout if present."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={
                "averageMonthlyPayout": 999.0,
                "payoutsByMonth": {"2025-01": 1000, "2025-02": 500},
            },
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert result["averageMonthlyPayout"] == 999.0

    @responses.activate
    def test_get_current_performance_non_dict_payload_passthrough(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should return non-dict payloads unchanged."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json=["unexpected", "shape"],
            status=200,
        )

        result: Any = client.get_current_performance(yenta_id)
        assert result == ["unexpected", "shape"]

    def test_coerce_number_handles_bool_and_bad_string(self) -> None:
        """_coerce_number should defensively ignore bools and non-numeric strings."""
        assert RevShareClient._coerce_number(True) is None
        assert RevShareClient._coerce_number("not-a-number") is None

    @responses.activate
    def test_get_current_performance_average_from_numeric_list_payloads(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should handle monthlyPayouts as numeric scalars."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={"monthlyPayouts": [1000, "500"]},
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert result["averageMonthlyPayout"] == pytest.approx(750.0)

    @responses.activate
    def test_get_current_performance_average_from_amount_key(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should extract amounts even without a 'payout' key."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={"monthlyPayouts": [{"amount": 1000}, {"payoutAmount": 500}]},
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert result["averageMonthlyPayout"] == pytest.approx(750.0)

    @responses.activate
    def test_get_current_performance_scalar_payouts_value(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should support scalar payout fields."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={"payouts": 1000},
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert result["averageMonthlyPayout"] == pytest.approx(1000.0)

    @responses.activate
    def test_get_current_performance_invalid_month_count_does_not_add_average(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should not add average when month count is invalid."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={"totalPayout": 1200, "monthCount": "abc"},
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert "averageMonthlyPayout" not in result

    @responses.activate
    def test_get_current_performance_zero_month_count_does_not_add_average(
        self, client: RevShareClient
    ) -> None:
        """get_current_performance should not add average for a zero month count."""
        yenta_id = "agent-123"
        responses.add(
            responses.GET,
            "https://arrakis.therealbrokerage.com/api/v1/"
            f"revshares/performance/{yenta_id}/revenue-share/current",
            json={"totalPayout": 1200, "monthCount": 0},
            status=200,
        )

        result = client.get_current_performance(yenta_id)
        assert "averageMonthlyPayout" not in result

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

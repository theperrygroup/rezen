"""Revenue share (revshare) client for the ReZEN Arrakis API."""

from datetime import date
from typing import Any, Dict, List, Optional, Sequence

from .base_client import BaseClient


class RevShareClient(BaseClient):
    """Client for revenue share (revshare) endpoints."""

    def _get_text(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Perform a GET request and return the raw text response.

        This is used for endpoints that return CSV/text payloads instead of JSON.

        Args:
            endpoint: API endpoint path (relative to base_url).
            params: Optional query parameters.

        Returns:
            Response text body.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout_seconds)

        if response.status_code in (200, 201):
            return response.text

        # Delegate error handling to the shared response handler (raises on error).
        self._handle_response(response)
        return ""

    @staticmethod
    def _coerce_number(value: Any) -> Optional[float]:
        """Coerce a value into a float when possible.

        This helper supports numeric types, numeric strings, and money-shaped dicts
        like ``{"amount": 123.45, "currency": "USD"}``.

        Args:
            value: Value to coerce into a numeric type.

        Returns:
            Float value if coercible, otherwise None.
        """
        if value is None:
            return None

        # bool is a subclass of int, so explicitly exclude it.
        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None

        if isinstance(value, dict):
            if "amount" in value:
                return RevShareClient._coerce_number(value.get("amount"))

        return None

    @classmethod
    def _extract_amounts(cls, value: Any) -> List[float]:
        """Extract numeric payout-like amounts from a list/dict payload.

        Args:
            value: A list, dict, or scalar potentially containing payout values.

        Returns:
            List of extracted numeric values.
        """
        amounts: List[float] = []

        if value is None:
            return amounts

        if isinstance(value, list):
            for item in value:
                direct = cls._coerce_number(item)
                if direct is not None:
                    amounts.append(direct)
                    continue

                if isinstance(item, dict):
                    for key in (
                        "payout",
                        "payoutAmount",
                        "amount",
                        "paymentAmount",
                        "totalPayout",
                    ):
                        if key not in item:
                            continue
                        coerced = cls._coerce_number(item.get(key))
                        if coerced is not None:
                            amounts.append(coerced)
                            break
            return amounts

        if isinstance(value, dict):
            # Treat as month->amount mapping or as nested objects containing amounts.
            for item in value.values():
                coerced = cls._coerce_number(item)
                if coerced is not None:
                    amounts.append(coerced)
            return amounts

        coerced = cls._coerce_number(value)
        return [coerced] if coerced is not None else []

    @staticmethod
    def _extract_records(value: Any, list_keys: Sequence[str]) -> List[Dict[str, Any]]:
        """Extract a list of dict records from common API payload shapes.

        Args:
            value: Raw API response payload (dict/list/etc.).
            list_keys: Keys to try when value is a dict wrapper.

        Returns:
            List of record dictionaries. Non-dict list elements are ignored.
        """
        if value is None:
            return []

        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

        if isinstance(value, dict):
            for key in list_keys:
                candidate = value.get(key)
                if isinstance(candidate, list):
                    return [item for item in candidate if isinstance(item, dict)]

        return []

    @staticmethod
    def _extract_agent_identifier(record: Dict[str, Any]) -> Optional[str]:
        """Extract a best-effort agent identifier from a contribution-like record.

        The revshare service has historically returned multiple shapes depending on
        backend version. This helper searches common field names and nested agent
        objects.

        Args:
            record: Contribution-like record.

        Returns:
            Agent identifier if found, otherwise None.
        """
        for key in (
            "agentYentaId",
            "contributorYentaId",
            "yentaId",
            "agentId",
            "contributorId",
        ):
            value = record.get(key)
            if isinstance(value, str) and value:
                return value

        for container_key in ("agent", "contributor", "contributingAgent"):
            container = record.get(container_key)
            if not isinstance(container, dict):
                continue
            for key in ("yentaId", "agentYentaId", "agentId", "id", "uuid"):
                value = container.get(key)
                if isinstance(value, str) and value:
                    return value

        return None

    @classmethod
    def _extract_earning_amount(cls, record: Dict[str, Any]) -> Optional[float]:
        """Extract a best-effort earning/payout amount from a contribution-like record.

        Args:
            record: Contribution-like record.

        Returns:
            Numeric earnings value if found, otherwise None.
        """
        for key in (
            "payout",
            "payoutAmount",
            "paymentAmount",
            "amount",
            "totalPayout",
            "earnings",
            "earning",
            "earnedAmount",
            "earningAmount",
        ):
            if key not in record:
                continue
            value = cls._coerce_number(record.get(key))
            if value is not None:
                return value

        return None

    @classmethod
    def _calculate_average_monthly_payout(
        cls, current_performance: Dict[str, Any]
    ) -> Optional[float]:
        """Compute average monthly payout from a current performance payload.

        The API response shape can vary by backend version/agent config. This method
        performs best-effort extraction from common structures like:
        - ``monthlyPayouts``: list of month entries containing payout amounts
        - ``payoutsByMonth``: mapping of month -> payout amount

        Args:
            current_performance: Raw current performance response payload.

        Returns:
            Average payout per month, or None if it cannot be derived.
        """
        for key in ("monthlyPayouts", "payoutsByMonth", "payouts", "payments"):
            amounts = cls._extract_amounts(current_performance.get(key))
            if amounts:
                return sum(amounts) / float(len(amounts))

        total_payout_raw = current_performance.get("totalPayout")
        if total_payout_raw is None:
            total_payout_raw = current_performance.get("totalPayoutAmount")
        total_payout = cls._coerce_number(total_payout_raw)

        months_raw = current_performance.get("months")
        if months_raw is None:
            months_raw = current_performance.get("monthCount")
        if months_raw is None:
            months_raw = current_performance.get("monthsCount")
        if total_payout is None or months_raw is None or isinstance(months_raw, bool):
            return None

        try:
            months = int(months_raw)
        except (TypeError, ValueError):
            return None

        if months <= 0:
            return None

        return total_payout / float(months)

    def get_payments_for_agent(
        self,
        yenta_id: str,
        page_number: int = 0,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Get all revshare payments for a particular agent.

        Args:
            yenta_id: Agent Yenta ID.
            page_number: Page number for pagination.
            page_size: Page size for pagination.

        Returns:
            Revshare payments response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {"pageNumber": page_number, "pageSize": page_size}

        endpoint = f"revshares/{yenta_id}/payments"
        return self.get(endpoint, params=params)

    def get_payment_by_id(
        self,
        yenta_id: str,
        outgoing_payment_id: str,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get details for a particular revshare payment.

        Args:
            yenta_id: Agent Yenta ID.
            outgoing_payment_id: Outgoing payment ID.
            page_number: Optional page number for pagination.
            page_size: Optional page size for pagination.

        Returns:
            Revshare payment response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size

        endpoint = f"revshares/{yenta_id}/payments/{outgoing_payment_id}"
        return self.get(endpoint, params=params if params else None)

    def get_payment_export_for_agent(
        self, yenta_id: str, outgoing_payment_id: str
    ) -> str:
        """Return a CSV file of all revshare contributions for a payment.

        Args:
            yenta_id: Agent Yenta ID.
            outgoing_payment_id: Outgoing payment ID.

        Returns:
            CSV content as a string.

        Raises:
            RezenError: If the API request fails.
        """
        endpoint = f"revshares/{yenta_id}/payments/{outgoing_payment_id}/export"
        return self._get_text(endpoint)

    def get_pending_payment_for_agent(
        self,
        yenta_id: str,
        page_number: int = 0,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Get all pending revshare payments for a particular agent.

        Args:
            yenta_id: Agent Yenta ID.
            page_number: Page number for pagination.
            page_size: Page size for pagination.

        Returns:
            Pending revshare payment response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {"pageNumber": page_number, "pageSize": page_size}

        endpoint = f"revshares/{yenta_id}/payments/pending"
        return self.get(endpoint, params=params)

    def get_pending_payment_export_for_agent(self, yenta_id: str) -> str:
        """Return a CSV file for all pending revshare payments for an agent.

        Args:
            yenta_id: Agent Yenta ID.

        Returns:
            CSV content as a string.

        Raises:
            RezenError: If the API request fails.
        """
        endpoint = f"revshares/{yenta_id}/payments/pending/export"
        return self._get_text(endpoint)

    def get_pending_payment_preview_for_agent(self, yenta_id: str) -> Dict[str, Any]:
        """Get pending revshare payments overview for a particular agent.

        Args:
            yenta_id: Agent Yenta ID.

        Returns:
            Pending payment overview payload.

        Raises:
            RezenError: If the API request fails.
        """
        endpoint = f"revshares/{yenta_id}/payments/pending-overview"
        return self.get(endpoint)

    def get_contributors_by_tier(
        self,
        yenta_id: str,
        tier: int,
        *,
        start_date: date,
        end_date: date,
        page_number: int = 0,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Get revshare contributors by tier.

        Args:
            yenta_id: Agent Yenta ID.
            tier: Tier number to fetch contributors for.
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            page_number: Page number for pagination.
            page_size: Page size for pagination.

        Returns:
            Contributors response payload.

        Raises:
            RezenError: If the API request fails.
        """
        # Keep query-string ordering consistent with docs/examples:
        # startDate, endDate, pageNumber, pageSize
        params: Dict[str, Any] = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        endpoint = f"revshares/{yenta_id}/contributors/{tier}"
        return self.get(endpoint, params=params)

    def get_contributions_by_tier(
        self,
        yenta_id: str,
        tier: int,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page_number: int = 0,
        page_size: int = 20,
        missed: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get agent-wise revshare contributions by tier.

        Args:
            yenta_id: Agent Yenta ID.
            tier: Tier number to fetch contributions for.
            start_date: Optional start date (inclusive) for filtering.
            end_date: Optional end date (inclusive) for filtering.
            page_number: Page number for pagination.
            page_size: Page size for pagination.
            missed: Optional flag to filter for missed contributions.

        Returns:
            Contributions-by-tier response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {"pageNumber": page_number, "pageSize": page_size}
        if start_date is not None:
            params["startDate"] = start_date.isoformat()
        if end_date is not None:
            params["endDate"] = end_date.isoformat()
        if missed is not None:
            params["missed"] = missed

        endpoint = f"revshares/{yenta_id}/contributions/{tier}"
        return self.get(endpoint, params=params)

    def get_earnings_per_agent_per_tier(
        self,
        yenta_id: str,
        *,
        tiers: Optional[List[int]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page_size: int = 200,
        missed: Optional[bool] = None,
        max_pages: int = 100,
    ) -> Dict[int, Dict[str, float]]:
        """Get revshare earnings per agent per tier.

        This is a convenience helper built on top of `get_contributions_by_tier`.
        It fetches contribution records per tier and aggregates them into a mapping
        of:

            tier -> contributorAgentId -> totalEarnings

        Args:
            yenta_id: Agent Yenta ID.
            tiers: Tiers to include. Defaults to the standard 7-tier revshare
                program: [1, 2, 3, 4, 5, 6, 7].
            start_date: Optional start date (inclusive) for filtering.
            end_date: Optional end date (inclusive) for filtering.
            page_size: Page size used when iterating through paginated results.
            missed: Optional flag to filter for missed contributions.
            max_pages: Safety limit for pagination to avoid infinite loops if the
                API returns unexpected pagination metadata.

        Returns:
            Mapping of tier number to a mapping of agent identifier -> earnings.

        Raises:
            RezenError: If the API request fails.
        """
        resolved_tiers = tiers if tiers is not None else [1, 2, 3, 4, 5, 6, 7]

        earnings_by_tier: Dict[int, Dict[str, float]] = {}

        for tier_value in resolved_tiers:
            tier_earnings: Dict[str, float] = {}

            page_number = 0
            for _ in range(max_pages):
                payload = self.get_contributions_by_tier(
                    yenta_id,
                    tier_value,
                    start_date=start_date,
                    end_date=end_date,
                    page_number=page_number,
                    page_size=page_size,
                    missed=missed,
                )

                records = self._extract_records(
                    payload, list_keys=("contributions", "content", "items", "results", "data")
                )
                if not records:
                    break

                for record in records:
                    agent_identifier = self._extract_agent_identifier(record)
                    amount = self._extract_earning_amount(record)
                    if agent_identifier is None or amount is None:
                        continue
                    tier_earnings[agent_identifier] = (
                        tier_earnings.get(agent_identifier, 0.0) + float(amount)
                    )

                if len(records) < page_size:
                    break

                page_number += 1

            earnings_by_tier[int(tier_value)] = tier_earnings

        return earnings_by_tier

    def get_earnings_per_tier(
        self,
        yenta_id: str,
        *,
        tiers: Optional[List[int]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page_size: int = 200,
        missed: Optional[bool] = None,
        max_pages: int = 100,
    ) -> Dict[int, float]:
        """Get total revshare earnings per tier.

        This aggregates `get_earnings_per_agent_per_tier` into a mapping of:

            tier -> totalEarningsForTier

        Args:
            yenta_id: Agent Yenta ID.
            tiers: Tiers to include. Defaults to the standard 7-tier revshare
                program: [1, 2, 3, 4, 5, 6, 7].
            start_date: Optional start date (inclusive) for filtering.
            end_date: Optional end date (inclusive) for filtering.
            page_size: Page size used when iterating through paginated results.
            missed: Optional flag to filter for missed contributions.
            max_pages: Safety limit for pagination to avoid infinite loops.

        Returns:
            Mapping of tier number -> total earnings for that tier.

        Raises:
            RezenError: If the API request fails.
        """
        earnings_by_agent_by_tier = self.get_earnings_per_agent_per_tier(
            yenta_id,
            tiers=tiers,
            start_date=start_date,
            end_date=end_date,
            page_size=page_size,
            missed=missed,
            max_pages=max_pages,
        )

        totals: Dict[int, float] = {}
        for tier_value, tier_map in earnings_by_agent_by_tier.items():
            totals[int(tier_value)] = sum(float(amount) for amount in tier_map.values())

        return totals

    def get_earnings_per_agent(
        self,
        yenta_id: str,
        *,
        tiers: Optional[List[int]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page_size: int = 200,
        missed: Optional[bool] = None,
        max_pages: int = 100,
    ) -> Dict[str, float]:
        """Get total revshare earnings per contributing agent across tiers.

        This aggregates `get_earnings_per_agent_per_tier` into a single mapping:

            contributorAgentId -> totalEarningsAcrossTiers

        Args:
            yenta_id: Agent Yenta ID.
            tiers: Tiers to include. Defaults to the standard 7-tier revshare
                program: [1, 2, 3, 4, 5, 6, 7].
            start_date: Optional start date (inclusive) for filtering.
            end_date: Optional end date (inclusive) for filtering.
            page_size: Page size used when iterating through paginated results.
            missed: Optional flag to filter for missed contributions.
            max_pages: Safety limit for pagination to avoid infinite loops.

        Returns:
            Mapping of agent identifier -> total earnings across selected tiers.

        Raises:
            RezenError: If the API request fails.
        """
        earnings_by_tier = self.get_earnings_per_agent_per_tier(
            yenta_id,
            tiers=tiers,
            start_date=start_date,
            end_date=end_date,
            page_size=page_size,
            missed=missed,
            max_pages=max_pages,
        )

        totals: Dict[str, float] = {}
        for tier_map in earnings_by_tier.values():
            for agent_identifier, amount in tier_map.items():
                totals[agent_identifier] = totals.get(agent_identifier, 0.0) + float(
                    amount
                )

        return totals

    def get_by_tier(
        self,
        yenta_id: str,
        *,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Get revshare by tier for a particular agent.

        Args:
            yenta_id: Agent Yenta ID.
            start_date: Start date (inclusive).
            end_date: End date (inclusive).

        Returns:
            Revshare-by-tier response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }

        endpoint = f"revshares/{yenta_id}/by-tier"
        return self.get(endpoint, params=params)

    def get_history(
        self, agent_yenta_id: str, *, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Get an agent's revshare history.

        Args:
            agent_yenta_id: Agent Yenta ID.
            start_date: Start date (inclusive).
            end_date: End date (inclusive).

        Returns:
            Revshare history response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }
        endpoint = f"revshares/{agent_yenta_id}/history"
        return self.get(endpoint, params=params)

    def get_monthly_performance(
        self, yenta_id: str, month: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get revshare performance for a particular month for an agent.

        Args:
            yenta_id: Agent Yenta ID.
            month: Month selector. If omitted, the API defaults to "current".

        Returns:
            Monthly performance response payload.

        Raises:
            RezenError: If the API request fails.
        """
        params: Dict[str, Any] = {}
        if month is not None:
            params["month"] = month

        endpoint = f"revshares/performance/{yenta_id}/revenue-share"
        return self.get(endpoint, params=params if params else None)

    def get_current_performance(self, yenta_id: str) -> Any:
        """Get the current revshare performance overview for an agent.

        Args:
            yenta_id: Agent Yenta ID.

        Returns:
            Current performance overview payload. When possible, this method adds
            a derived ``averageMonthlyPayout`` metric based on the returned data.

        Raises:
            RezenError: If the API request fails.
        """
        endpoint = f"revshares/performance/{yenta_id}/revenue-share/current"
        response = self.get(endpoint)

        if not isinstance(response, dict):
            return response

        if "averageMonthlyPayout" in response:
            return response

        avg = self._calculate_average_monthly_payout(response)
        if avg is None:
            return response

        enriched = dict(response)
        enriched["averageMonthlyPayout"] = avg
        return enriched

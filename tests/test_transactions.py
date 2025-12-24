"""Tests for the transactions client."""

from datetime import date

import pytest
import responses

from rezen.transactions import (
    NormalizedTransactionAddress,
    TransactionsClient,
    _parse_date,
    normalize_transaction,
)


class TestTransactionsClient:
    """Test the TransactionsClient class."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TransactionsClient(api_key="test_key")
        self.transaction_id = "tx-12345"
        self.base_url = "https://arrakis.therealbrokerage.com/api/v1"

    # ===== TRANSACTION MANAGEMENT TESTS =====

    @responses.activate
    def test_get_transaction(self) -> None:
        """Test get_transaction endpoint."""
        expected_response = {"id": self.transaction_id, "status": "ACTIVE"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction(self.transaction_id)

        assert result == expected_response

    def test_normalize_transaction_closed(self) -> None:
        """Test normalization of a closed transaction."""
        normalized = normalize_transaction(
            {
                "id": "tx-1",
                "status": "CLOSED",
                "closedAt": "2025-01-31",
                "closingDateEstimated": "2025-02-15",
                "contractAcceptanceDate": "2025-01-10T00:00:00Z",
                "address": {
                    "street": "123 Main St",
                    "street2": "Unit 4",
                    "city": "Salt Lake City",
                    "state": "UTAH",
                    "zip": "84101",
                },
            }
        )

        assert normalized.id == "tx-1"
        assert normalized.status == "closed"
        assert normalized.is_closed is True
        assert normalized.closing_date_actual == date(2025, 1, 31)
        assert normalized.closing_date_estimated == date(2025, 2, 15)
        assert normalized.under_contract_date == date(2025, 1, 10)
        assert normalized.address.street_line == "123 Main St, Unit 4"
        assert (
            normalized.address.one_line
            == "123 Main St, Unit 4, Salt Lake City, UTAH 84101"
        )
        assert normalized.closing_date == date(2025, 1, 31)

    def test_normalize_transaction_terminated(self) -> None:
        """Test normalization of a terminated transaction."""
        normalized = normalize_transaction(
            {"id": "tx-2", "status": "TERMINATED", "address": {"street": "1 A St"}}
        )
        assert normalized.status == "terminated"
        assert normalized.is_closed is False

    def test_normalize_transaction_active(self) -> None:
        """Test normalization of an active transaction."""
        normalized = normalize_transaction({"id": "tx-3", "status": "ACTIVE"})
        assert normalized.status == "active"
        assert normalized.is_closed is False

    def test_parse_date_variants(self) -> None:
        """Test _parse_date handles common API formats."""
        assert _parse_date(None) is None
        assert _parse_date("") is None
        assert _parse_date("1700000000") is not None
        assert _parse_date("2025-01-31") == date(2025, 1, 31)
        assert _parse_date("2025-01-31T00:00:00Z") == date(2025, 1, 31)
        assert _parse_date("not a date") is None
        assert _parse_date("2025-99-99T00:00:00Z") is None
        assert _parse_date({"unexpected": "type"}) is None

        # Seconds and milliseconds timestamps.
        assert _parse_date(1_700_000_000) is not None
        assert _parse_date(1_700_000_000_000) is not None

        # Extremely large values should safely return None.
        assert _parse_date(10**20) is None

    def test_normalized_transaction_address_empty(self) -> None:
        """Test address normalization when no fields are present."""
        addr = NormalizedTransactionAddress(
            street=None, street2=None, city=None, state=None, zip=None
        )
        assert addr.street_line is None
        assert addr.one_line is None

    @responses.activate
    def test_get_transaction_normalized(self) -> None:
        """Test get_transaction_normalized endpoint wrapper."""
        expected_response = {
            "id": self.transaction_id,
            "status": "CLOSED",
            "closedAt": "2025-01-31",
            "address": {"street": "123 Main St", "city": "SLC", "state": "UTAH"},
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}",
            json=expected_response,
            status=200,
        )

        normalized = self.client.get_transaction_normalized(self.transaction_id)
        assert normalized.status == "closed"
        assert normalized.closing_date_actual == date(2025, 1, 31)
        assert normalized.address.street_line == "123 Main St"

    def test_get_transaction_normalized_raises_for_non_dict_payload(self) -> None:
        """Test get_transaction_normalized raises if the API returns non-dict JSON."""
        with pytest.raises(ValueError):
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(
                    self.client, "get_transaction", lambda _tid: ["not", "a", "dict"]
                )
                self.client.get_transaction_normalized(self.transaction_id)

    def test_backward_compatibility_wrappers(self) -> None:
        """Test wrapper methods delegate to the newer endpoints."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                self.client,
                "get_participant_transactions",
                lambda yenta_id: {"yenta_id": yenta_id},
            )
            mp.setattr(
                self.client,
                "get_participant_current_transactions",
                lambda yenta_id: {"current": yenta_id},
            )
            mp.setattr(
                self.client,
                "get_participant_listing_transactions",
                lambda **kwargs: {"kwargs": kwargs},
            )

            assert self.client.get_agent_transactions("u1") == {"yenta_id": "u1"}
            assert self.client.get_agent_current_transactions("u2") == {"current": "u2"}
            listings = self.client.get_agent_current_listings("u3")
            assert listings["kwargs"]["lifecycle_group"] == "CURRENT"
            assert listings["kwargs"]["page_size"] == 100

    @responses.activate
    def test_request_termination(self) -> None:
        """Test request_termination endpoint."""
        responses.add(
            responses.POST,
            f"{self.base_url}/transactions/{self.transaction_id}/request-termination",
            json={"ok": True},
            status=200,
        )

        assert self.client.request_termination(self.transaction_id) == {"ok": True}

    @responses.activate
    def test_get_transaction_explanation(self) -> None:
        """Test get_transaction_explanation endpoint."""
        expected_response = {"explanation": "Transaction details", "amount": 500000}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/transaction-explanation",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_explanation(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_payout_explanation(self) -> None:
        """Test get_payout_explanation endpoint."""
        expected_response = {"payout_details": {"agent_commission": 15000}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/payout-explanation",
            json=expected_response,
            status=200,
        )

        result = self.client.get_payout_explanation(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_participant_payout_explanation(self) -> None:
        """Test get_participant_payout_explanation endpoint."""
        expected_response = {"participant_payout": {"amount": 10000, "percentage": 2.5}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/payout-explanation/participant-123",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_payout_explanation(
            self.transaction_id, "participant-123"
        )

        assert result == expected_response

    @responses.activate
    def test_get_metadata_for_participant_creation(self) -> None:
        """Test get_metadata_for_participant_creation endpoint."""
        expected_response = {"metadata": {"required_fields": ["name", "email"]}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/metadata-for-participant-creation/BUYER_AGENT",
            json=expected_response,
            status=200,
        )

        result = self.client.get_metadata_for_participant_creation(
            self.transaction_id, "BUYER_AGENT"
        )

        assert result == expected_response

    @responses.activate
    def test_get_transaction_features(self) -> None:
        """Test get_transaction_features endpoint."""
        expected_response = {"features": ["digital_signatures", "automated_reporting"]}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/features",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_features(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_transaction_permissions(self) -> None:
        """Test get_transaction_permissions endpoint."""
        expected_response = {"permissions": {"can_edit": True, "can_delete": False}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/permissions",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_permissions(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_check_transaction_permissions(self) -> None:
        """Test check_transaction_permissions endpoint."""
        expected_response = {"permission_check": {"status": "AUTHORIZED"}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/check-permissions",
            json=expected_response,
            status=200,
        )

        result = self.client.check_transaction_permissions(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_transaction_process(self) -> None:
        """Test get_transaction_process endpoint."""
        expected_response = {
            "process": {"current_stage": "UNDER_CONTRACT", "next_steps": ["appraisal"]}
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/process",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_process(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_transaction_summary_pdf(self) -> None:
        """Test get_transaction_summary_pdf endpoint."""
        expected_response = {"pdf_url": "https://example.com/summary.pdf"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/summary-pdf",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_summary_pdf(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_is_display_agent_reported_transaction_closed_dialog(self) -> None:
        """Test is_display_agent_reported_transaction_closed_dialog endpoint."""
        expected_response = {"display_dialog": True}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/is-display-agent-reported-transaction-closed-dialog",
            json=expected_response,
            status=200,
        )

        result = self.client.is_display_agent_reported_transaction_closed_dialog(
            self.transaction_id
        )

        assert result == expected_response

    @responses.activate
    def test_get_transaction_by_code(self) -> None:
        """Test get_transaction_by_code endpoint."""
        expected_response = {"id": self.transaction_id, "code": "TRX-001"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/code/TRX-001",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_by_code("TRX-001")

        assert result == expected_response

    # ===== TITLE MANAGEMENT TESTS =====

    @responses.activate
    def test_update_transaction_title(self) -> None:
        """Test update_transaction_title endpoint."""
        expected_response = {"success": True, "title_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/title",
            json=expected_response,
            status=200,
        )

        title_info = {"title_company": "First American Title", "policy_amount": 500000}
        result = self.client.update_transaction_title(self.transaction_id, title_info)

        assert result == expected_response

    @responses.activate
    def test_update_title_system_user(self) -> None:
        """Test update_title_system_user endpoint."""
        expected_response = {"success": True, "system_user_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/title/system-user",
            json=expected_response,
            status=200,
        )

        system_user_info = {"user_id": "title-user-123", "access_level": "FULL"}
        result = self.client.update_title_system_user(
            self.transaction_id, system_user_info
        )

        assert result == expected_response

    @responses.activate
    def test_update_title_order(self) -> None:
        """Test update_title_order endpoint."""
        expected_response = {"success": True, "title_order_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/title-order",
            json=expected_response,
            status=200,
        )

        title_order_info = {"order_number": "TO-789", "ordered_date": "2024-01-15"}
        result = self.client.update_title_order(self.transaction_id, title_order_info)

        assert result == expected_response

    @responses.activate
    def test_get_title_order_placement_eligibility(self) -> None:
        """Test get_title_order_placement_eligibility endpoint."""
        expected_response = {
            "eligible": True,
            "requirements_met": ["address", "purchase_price"],
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/title-order/placement-eligibility",
            json=expected_response,
            status=200,
        )

        result = self.client.get_title_order_placement_eligibility(self.transaction_id)

        assert result == expected_response

    # ===== PARTICIPANT MANAGEMENT TESTS =====

    @responses.activate
    def test_update_participant(self) -> None:
        """Test update_participant endpoint."""
        expected_response = {"success": True, "participant_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/participant",
            json=expected_response,
            status=200,
        )

        participant_info = {"role": "BUYER_AGENT", "commission_percentage": 2.5}
        result = self.client.update_participant(self.transaction_id, participant_info)

        assert result == expected_response

    @responses.activate
    def test_update_participant_opcity(self) -> None:
        """Test update_participant_opcity endpoint."""
        expected_response = {"success": True, "opcity_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/participant/opcity",
            json=expected_response,
            status=200,
        )

        opcity_info = {"opcity_enabled": True, "lead_source": "OPCITY"}
        result = self.client.update_participant_opcity(self.transaction_id, opcity_info)

        assert result == expected_response

    @responses.activate
    def test_create_participant(self) -> None:
        """Test create_participant endpoint."""
        expected_response = {"success": True, "participant_id": "participant-789"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transactions/{self.transaction_id}/create-participant",
            json=expected_response,
            status=200,
        )

        participant_data = {
            "role": "SELLER_AGENT",
            "name": "John Agent",
            "email": "john@example.com",
        }
        result = self.client.create_participant(self.transaction_id, participant_data)

        assert result == expected_response

    @responses.activate
    def test_get_participant_lite(self) -> None:
        """Test get_participant_lite endpoint."""
        expected_response = {
            "id": "participant-123",
            "name": "Agent Smith",
            "role": "BUYER_AGENT",
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/participant/participant-123/lite",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_lite(
            self.transaction_id, "participant-123"
        )

        assert result == expected_response

    @responses.activate
    def test_get_participant_payment(self) -> None:
        """Test get_participant_payment endpoint."""
        expected_response = {"payment_info": {"amount": 12500, "status": "PENDING"}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/participant/participant-123/payment",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_payment(
            self.transaction_id, "participant-123"
        )

        assert result == expected_response

    @responses.activate
    def test_get_agent_participants(self) -> None:
        """Test get_agent_participants endpoint."""
        expected_response = {"participants": [{"id": "agent-1", "role": "BUYER_AGENT"}]}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/agent-participants",
            json=expected_response,
            status=200,
        )

        result = self.client.get_agent_participants(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_comment_participants(self) -> None:
        """Test get_comment_participants endpoint."""
        expected_response = {
            "comment_participants": [{"id": "agent-2", "can_comment": True}]
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/comment-participants/agent-123",
            json=expected_response,
            status=200,
        )

        result = self.client.get_comment_participants(self.transaction_id, "agent-123")

        assert result == expected_response

    @responses.activate
    def test_get_checklist_assignees(self) -> None:
        """Test get_checklist_assignees endpoint."""
        expected_response = {
            "assignees": [{"id": "agent-1", "tasks": ["inspection", "appraisal"]}]
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/checklist-assignees",
            json=expected_response,
            status=200,
        )

        result = self.client.get_checklist_assignees(self.transaction_id)

        assert result == expected_response

    # ===== PAYMENT AND FINANCIAL TESTS =====

    @responses.activate
    def test_get_payment_info(self) -> None:
        """Test get_payment_info endpoint."""
        expected_response = {
            "payment_info": {"gross_commission": 15000, "net_commission": 12750}
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/payment-info/agent-123",
            json=expected_response,
            status=200,
        )

        result = self.client.get_payment_info(self.transaction_id, "agent-123")

        assert result == expected_response

    @responses.activate
    def test_get_paid_at_closing(self) -> None:
        """Test get_paid_at_closing endpoint."""
        expected_response = {
            "paid_at_closing": {"amount": 5000, "items": ["inspection_fee"]}
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/paid-at-closing",
            json=expected_response,
            status=200,
        )

        result = self.client.get_paid_at_closing(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_money_transfers(self) -> None:
        """Test get_money_transfers endpoint."""
        expected_response = {
            "transfers": [
                {"amount": 12500, "status": "COMPLETED", "date": "2024-01-20"}
            ]
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/money-transfers",
            json=expected_response,
            status=200,
        )

        result = self.client.get_money_transfers(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_update_attached_fee(self) -> None:
        """Test update_attached_fee endpoint."""
        expected_response = {"success": True, "fee_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/attached-fee",
            json=expected_response,
            status=200,
        )

        fee_info = {
            "fee_type": "ADMIN_FEE",
            "amount": 299,
            "description": "Administrative fee",
        }
        result = self.client.update_attached_fee(self.transaction_id, fee_info)

        assert result == expected_response

    # ===== ESCROW MANAGEMENT TESTS =====

    @responses.activate
    def test_create_escrow(self) -> None:
        """Test create_escrow endpoint."""
        expected_response = {"success": True, "escrow_id": "escrow-456"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transactions/{self.transaction_id}/escrow",
            json=expected_response,
            status=200,
        )

        escrow_data = {"escrow_company": "Chicago Title", "amount": 25000}
        result = self.client.create_escrow(self.transaction_id, escrow_data)

        assert result == expected_response

    @responses.activate
    def test_create_escrow_deposit(self) -> None:
        """Test create_escrow_deposit endpoint."""
        expected_response = {"success": True, "deposit_id": "deposit-789"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transactions/escrows/escrow-456/escrow-deposit",
            json=expected_response,
            status=200,
        )

        deposit_data = {"amount": 10000, "deposit_type": "EARNEST_MONEY"}
        result = self.client.create_escrow_deposit("escrow-456", deposit_data)

        assert result == expected_response

    @responses.activate
    def test_get_escrow_deposit(self) -> None:
        """Test get_escrow_deposit endpoint."""
        expected_response = {"id": "deposit-789", "amount": 10000, "status": "CLEARED"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/escrows/escrow-456/escrow-deposit/deposit-789",
            json=expected_response,
            status=200,
        )

        result = self.client.get_escrow_deposit("escrow-456", "deposit-789")

        assert result == expected_response

    @responses.activate
    def test_update_escrow_check_deposit(self) -> None:
        """Test update_escrow_check_deposit endpoint."""
        expected_response = {"success": True, "check_deposit_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/escrows/escrow-456/check-deposits/check-123",
            json=expected_response,
            status=200,
        )

        deposit_data = {"check_number": "1001", "amount": 5000, "status": "DEPOSITED"}
        result = self.client.update_escrow_check_deposit(
            "escrow-456", "check-123", deposit_data
        )

        assert result == expected_response

    # ===== CHECK DEPOSITS TESTS =====

    @responses.activate
    def test_update_check_deposit(self) -> None:
        """Test update_check_deposit endpoint."""
        expected_response = {"success": True, "check_deposit_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/check-deposits/check-456",
            json=expected_response,
            status=200,
        )

        deposit_data = {
            "amount": 2500,
            "memo": "Commission payment",
            "status": "PENDING",
        }
        result = self.client.update_check_deposit(
            self.transaction_id, "check-456", deposit_data
        )

        assert result == expected_response

    @responses.activate
    def test_get_check_deposits(self) -> None:
        """Test get_check_deposits endpoint."""
        expected_response = {
            "deposits": [{"id": "check-456", "amount": 2500, "status": "PENDING"}]
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/check-deposits",
            json=expected_response,
            status=200,
        )

        result = self.client.get_check_deposits(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_check_deposit_upload_link(self) -> None:
        """Test get_check_deposit_upload_link endpoint."""
        expected_response = {
            "upload_url": "https://upload.example.com/check",
            "expires_at": "2024-01-21T12:00:00Z",
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/check-deposits/EARNEST_MONEY/upload-link",
            json=expected_response,
            status=200,
        )

        result = self.client.get_check_deposit_upload_link(
            self.transaction_id, "EARNEST_MONEY"
        )

        assert result == expected_response

    @responses.activate
    def test_get_check_deposit_front_image_download_url(self) -> None:
        """Test get_check_deposit_front_image_download_url endpoint."""
        expected_response = {"download_url": "https://download.example.com/front.jpg"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/check-deposits/check-456/front-image/download-url",
            json=expected_response,
            status=200,
        )

        result = self.client.get_check_deposit_front_image_download_url(
            self.transaction_id, "check-456"
        )

        assert result == expected_response

    @responses.activate
    def test_get_check_deposit_back_image_download_url(self) -> None:
        """Test get_check_deposit_back_image_download_url endpoint."""
        expected_response = {"download_url": "https://download.example.com/back.jpg"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/check-deposits/check-456/back-image/download-url",
            json=expected_response,
            status=200,
        )

        result = self.client.get_check_deposit_back_image_download_url(
            self.transaction_id, "check-456"
        )

        assert result == expected_response

    # ===== BANK ACCOUNTS TESTS =====

    @responses.activate
    def test_get_canada_bank_accounts(self) -> None:
        """Test get_canada_bank_accounts endpoint."""
        expected_response = {
            "bank_accounts": [
                {"id": "ca-bank-1", "currency": "CAD", "routing": "123456"}
            ]
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/canada-bank-accounts",
            json=expected_response,
            status=200,
        )

        result = self.client.get_canada_bank_accounts(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_bank_accounts(self) -> None:
        """Test get_bank_accounts endpoint."""
        expected_response = {
            "bank_accounts": [{"id": "bank-1", "currency": "USD", "routing": "987654"}]
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}/bank-accounts",
            json=expected_response,
            status=200,
        )

        result = self.client.get_bank_accounts(self.transaction_id)

        assert result == expected_response

    # ===== DOUBLE ENDER TESTS =====

    @responses.activate
    def test_update_double_ender(self) -> None:
        """Test update_double_ender endpoint."""
        expected_response = {"success": True, "double_ender_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/double-ender",
            json=expected_response,
            status=200,
        )

        double_ender_info = {"agent_id": "agent-123", "represents_both_parties": True}
        result = self.client.update_double_ender(self.transaction_id, double_ender_info)

        assert result == expected_response

    @responses.activate
    def test_update_agent_reported_transaction_closed_dialog(self) -> None:
        """Test update_agent_reported_transaction_closed_dialog endpoint."""
        expected_response = {"success": True, "dialog_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transactions/{self.transaction_id}/agent-reported-transaction-closed-dialog",
            json=expected_response,
            status=200,
        )

        dialog_info = {"show_dialog": True, "closing_date": "2024-01-25"}
        result = self.client.update_agent_reported_transaction_closed_dialog(
            self.transaction_id, dialog_info
        )

        assert result == expected_response

    # ===== BATCH AND LIST OPERATIONS TESTS =====

    @responses.activate
    def test_get_transactions_lite_batch(self) -> None:
        """Test get_transactions_lite_batch endpoint."""
        expected_response = {
            "transactions": [
                {"id": "tx-1", "status": "ACTIVE"},
                {"id": "tx-2", "status": "CLOSED"},
            ]
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/lite/batch-get",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transactions_lite_batch(["tx-1", "tx-2"])

        assert result == expected_response
        request = responses.calls[0].request
        assert "transactionIds=tx-1%2Ctx-2" in request.url  # URL-encoded comma

    @responses.activate
    def test_get_rolling_transactions(self) -> None:
        """Test get_rolling_transactions endpoint."""
        expected_response = {"transactions": [], "total": 0, "page": 0}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/rolling",
            json=expected_response,
            status=200,
        )

        result = self.client.get_rolling_transactions(
            page_number=1,
            page_size=25,
            sort_by="CREATED_AT",
            sort_direction="DESC",
            status="ACTIVE",
        )

        assert result == expected_response
        request = responses.calls[0].request
        assert "pageNumber=1" in request.url
        assert "pageSize=25" in request.url
        assert "sortBy=CREATED_AT" in request.url
        assert "sortDirection=DESC" in request.url
        assert "status=ACTIVE" in request.url

    # ===== PARTICIPANT TRANSACTIONS TESTS =====

    @responses.activate
    def test_get_participant_transactions(self) -> None:
        """Test get_participant_transactions endpoint."""
        expected_response = {"transactions": [{"id": "tx-1", "role": "BUYER_AGENT"}]}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/participant/user-123",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_transactions("user-123")

        assert result == expected_response

    @responses.activate
    def test_get_participant_transactions_by_lifecycle_group(self) -> None:
        """Test get_participant_transactions_by_lifecycle_group endpoint."""
        expected_response = {"transactions": [], "total": 0}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/participant/user-123/transactions/OPEN",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_transactions_by_lifecycle_group(
            yenta_id="user-123",
            lifecycle_group="OPEN",
            page_number=0,
            page_size=20,
            search_text="search term",
            sort_by="CREATED_AT",
            sort_direction="ASC",
            transaction_type=["SALE", "LEASE"],
        )

        assert result == expected_response
        request = responses.calls[0].request
        assert "pageNumber=0" in request.url
        assert "pageSize=20" in request.url
        assert "searchText=search+term" in request.url
        assert "sortBy=CREATED_AT" in request.url
        assert "sortDirection=ASC" in request.url

    @responses.activate
    def test_get_participant_transaction_lifecycle_group_counts(self) -> None:
        """Test get_participant_transaction_lifecycle_group_counts endpoint."""
        expected_response = {"counts": {"OPEN": 5, "CLOSED": 12, "TERMINATED": 1}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/participant/user-123/transactions/lifecycle-group-counts",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_transaction_lifecycle_group_counts(
            "user-123"
        )

        assert result == expected_response

    @responses.activate
    def test_get_participant_listing_transactions(self) -> None:
        """Test get_participant_listing_transactions endpoint."""
        expected_response = {"listings": [], "total": 0}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/participant/user-123/listing-transactions/LISTING_ACTIVE",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_listing_transactions(
            yenta_id="user-123",
            lifecycle_group="LISTING_ACTIVE",
            page_number=0,
            page_size=10,
            search_text="listing search",
            sort_by="PRICE",
            sort_direction="DESC",
        )

        assert result == expected_response
        request = responses.calls[0].request
        assert "pageNumber=0" in request.url
        assert "pageSize=10" in request.url
        assert "searchText=listing+search" in request.url
        assert "sortBy=PRICE" in request.url
        assert "sortDirection=DESC" in request.url

    @responses.activate
    def test_get_participant_listing_transaction_lifecycle_group_counts(self) -> None:
        """Test get_participant_listing_transaction_lifecycle_group_counts endpoint."""
        expected_response = {"counts": {"LISTING_ACTIVE": 3, "LISTING_CLOSED": 8}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/participant/user-123/listing-transactions/lifecycle-group-counts",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_listing_transaction_lifecycle_group_counts(
            "user-123"
        )

        assert result == expected_response

    @responses.activate
    def test_get_participant_current_transactions(self) -> None:
        """Test get_participant_current_transactions endpoint."""
        expected_response = {
            "current_transactions": [{"id": "tx-active", "status": "IN_PROGRESS"}]
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/participant/user-123/current",
            json=expected_response,
            status=200,
        )

        result = self.client.get_participant_current_transactions("user-123")

        assert result == expected_response

    def test_client_inheritance(self) -> None:
        """Test that TransactionsClient inherits from BaseClient."""
        from rezen.base_client import BaseClient

        assert isinstance(self.client, BaseClient)
        assert hasattr(self.client, "get")
        assert hasattr(self.client, "post")
        assert hasattr(self.client, "put")
        assert hasattr(self.client, "delete")

    @responses.activate
    def test_error_handling_propagation(self) -> None:
        """Test that errors are properly propagated from base client."""
        from rezen.exceptions import NotFoundError

        responses.add(
            responses.GET,
            f"{self.base_url}/transactions/{self.transaction_id}",
            json={"message": "Transaction not found"},
            status=404,
        )

        with pytest.raises(NotFoundError):
            self.client.get_transaction(self.transaction_id)

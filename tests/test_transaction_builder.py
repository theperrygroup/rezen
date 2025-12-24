"""Tests for the transaction builder client."""

import io
from typing import Any, Dict

import pytest
import responses

from rezen.exceptions import (
    InvalidFieldNameError,
    InvalidFieldValueError,
    TransactionSequenceError,
    ValidationError,
)
from rezen.transaction_builder import TransactionBuilderClient


class TestTransactionBuilderClient:
    """Test the TransactionBuilderClient class."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TransactionBuilderClient(api_key="test_key")
        self.transaction_id = "test-transaction-123"
        self.base_url = "https://arrakis.therealbrokerage.com/api/v1"

    @responses.activate
    def test_update_title_info(self) -> None:
        """Test update_title_info endpoint."""
        expected_response = {"success": True, "id": self.transaction_id}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/title",
            json=expected_response,
            status=200,
        )

        title_info = {"title": "New Title"}
        result = self.client.update_title_info(self.transaction_id, title_info)

        assert result == expected_response
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url.endswith(
            f"/transaction-builder/{self.transaction_id}/title"
        )

    @responses.activate
    def test_add_seller(self) -> None:
        """Test add_seller endpoint."""
        expected_response = {"success": True, "seller_added": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/seller",
            json=expected_response,
            status=200,
        )

        seller_info = {"name": "John Doe", "email": "john@example.com"}
        result = self.client.add_seller(self.transaction_id, seller_info)

        assert result == expected_response

    def test_add_seller_rejects_snake_case_fields(self) -> None:
        """Test add_seller rejects snake_case field names."""
        with pytest.raises(InvalidFieldNameError):
            self.client.add_seller(self.transaction_id, {"first_name": "Jane"})

    @responses.activate
    def test_add_referral_info(self) -> None:
        """Test add_referral_info endpoint with all parameters."""
        expected_response = {"success": True, "referral_added": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/referral-info",
            json=expected_response,
            status=200,
        )

        # Test with all optional parameters
        result = self.client.add_referral_info(
            transaction_id=self.transaction_id,
            role="BUYERS_AGENT",
            receives_invoice=True,
            referral_type="AGENT",
            first_name="Jane",
            last_name="Smith",
            company_name="Real Estate Co",
            email="jane@example.com",
            ein="12-3456789",
            phone_number="555-1234",
            address="123 Main St",
            agent_id="agent-123",
        )

        assert result == expected_response

        # Check that query parameters were included
        request = responses.calls[0].request
        assert "role=BUYERS_AGENT" in request.url
        assert "receivesInvoice=True" in request.url
        assert "type=AGENT" in request.url
        assert "firstName=Jane" in request.url

    @responses.activate
    def test_add_referral_info_with_file(self) -> None:
        """Test add_referral_info endpoint with file upload."""
        expected_response = {"success": True, "file_uploaded": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/referral-info",
            json=expected_response,
            status=200,
        )

        file_content = b"test file content"
        file_obj = io.BytesIO(file_content)

        result = self.client.add_referral_info(
            transaction_id=self.transaction_id,
            role="EXTERNAL_AGENT",
            receives_invoice=False,
            referral_type="EXTERNAL_ENTITY",
            file=file_obj,
        )

        assert result == expected_response

    @responses.activate
    def test_upload_w9_to_referral_participant(self) -> None:
        """Test upload_w9_to_referral_participant endpoint."""
        participant_id = "participant-456"
        expected_response = {"success": True, "w9_uploaded": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/referral-info/{participant_id}/upload-w9",
            json=expected_response,
            status=200,
        )

        file_content = b"W9 file content"
        file_obj = io.BytesIO(file_content)

        result = self.client.upload_w9_to_referral_participant(
            self.transaction_id, participant_id, file_obj
        )

        assert result == expected_response

    def test_prepare_price_and_date_data(self) -> None:
        """Test the prepare_price_and_date_data helper method."""
        # Test with all parameters
        result = self.client.prepare_price_and_date_data(
            sale_price=500000,
            representation_type="BUYER",
            listing_commission_percent=2.5,
            sale_commission_percent=2.5,
            deal_type="SALE",
            property_type="RESIDENTIAL",
            acceptance_date="2024-06-16",
            closing_date="2024-07-16",
            earnest_money=10000,
            down_payment=100000,
            loan_amount=400000,
        )

        # Verify required fields
        assert result["dealType"] == "SALE"
        assert result["propertyType"] == "RESIDENTIAL"
        assert result["representationType"] == "BUYER"
        assert result["salePrice"]["amount"] == 500000
        assert result["salePrice"]["currency"] == "USD"

        # Verify commission objects have negativeOrEmpty field
        assert result["listingCommission"]["commissionPercent"] == 2.5
        assert result["listingCommission"]["percentEnabled"] is True
        assert result["listingCommission"]["negativeOrEmpty"] is False

        assert result["saleCommission"]["commissionPercent"] == 2.5
        assert result["saleCommission"]["percentEnabled"] is True
        assert result["saleCommission"]["negativeOrEmpty"] is False

        # Verify optional fields
        assert result["acceptanceDate"] == "2024-06-16"
        assert result["closingDate"] == "2024-07-16"
        assert result["earnestMoney"] == 10000
        assert result["downPayment"] == 100000
        assert result["loanAmount"] == 400000

        # Test with minimal parameters (defaults)
        result_minimal = self.client.prepare_price_and_date_data(
            sale_price=300000, representation_type="SELLER"
        )

        # Verify defaults
        assert result_minimal["dealType"] == "SALE"
        assert result_minimal["propertyType"] == "RESIDENTIAL"
        assert result_minimal["listingCommission"]["commissionPercent"] == 3.0
        assert result_minimal["saleCommission"]["commissionPercent"] == 3.0

        # Verify optional fields are not included when not provided
        assert "acceptanceDate" not in result_minimal
        assert "closingDate" not in result_minimal
        assert "earnestMoney" not in result_minimal
        assert "downPayment" not in result_minimal
        assert "loanAmount" not in result_minimal

    @responses.activate
    def test_update_price_and_date_info(self) -> None:
        """Test update_price_and_date_info endpoint."""
        expected_response = {"success": True, "price_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/price-date-info",
            json=expected_response,
            status=200,
        )

        price_info = {
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": {"amount": 500000, "currency": "USD"},
            "representationType": "BUYER",
            "closingDate": "2024-01-15",
            "listingCommission": {
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False,
            },
            "saleCommission": {
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False,
            },
        }
        result = self.client.update_price_and_date_info(self.transaction_id, price_info)

        assert result == expected_response

    def test_update_price_and_date_info_validations(self) -> None:
        """Test validation branches for update_price_and_date_info."""
        with pytest.raises(ValidationError, match="Missing required fields"):
            self.client.update_price_and_date_info(
                self.transaction_id, {"dealType": "SALE"}
            )

        with pytest.raises(InvalidFieldValueError, match="salePrice"):
            self.client.update_price_and_date_info(
                self.transaction_id,
                {
                    "dealType": "SALE",
                    "propertyType": "RESIDENTIAL",
                    "salePrice": 500000,
                    "representationType": "BUYER",
                    "listingCommission": {"commissionPercent": 3.0},
                    "saleCommission": {"commissionPercent": 3.0},
                },
            )

        with pytest.raises(InvalidFieldValueError, match="salePrice"):
            self.client.update_price_and_date_info(
                self.transaction_id,
                {
                    "dealType": "SALE",
                    "propertyType": "RESIDENTIAL",
                    "salePrice": {"amount": 500000},
                    "representationType": "BUYER",
                    "listingCommission": {"commissionPercent": 3.0},
                    "saleCommission": {"commissionPercent": 3.0},
                },
            )

        with pytest.raises(InvalidFieldValueError, match="representationType"):
            self.client.update_price_and_date_info(
                self.transaction_id,
                {
                    "dealType": "SALE",
                    "propertyType": "RESIDENTIAL",
                    "salePrice": {"amount": 500000, "currency": "USD"},
                    "representationType": "BUYERS_AGENT",
                    "listingCommission": {"commissionPercent": 3.0},
                    "saleCommission": {"commissionPercent": 3.0},
                },
            )

        with pytest.raises(InvalidFieldNameError):
            self.client.update_price_and_date_info(
                self.transaction_id,
                {
                    "dealType": "SALE",
                    "propertyType": "RESIDENTIAL",
                    "salePrice": {"amount": 500000, "currency": "USD"},
                    "representationType": "BUYER",
                    "listingCommission": {"commissionPercent": 3.0},
                    "saleCommission": {"commissionPercent": 3.0},
                    "acceptance_date": "2025-01-01",
                },
            )

    def test_update_price_and_date_info_adds_negative_or_empty(self) -> None:
        """Commission objects should default negativeOrEmpty to False."""
        payload = {
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": {"amount": 500000, "currency": "USD"},
            "representationType": "BUYER",
            "listingCommission": {"commissionPercent": 3.0, "percentEnabled": True},
            "saleCommission": {"commissionPercent": 3.0, "percentEnabled": True},
        }

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "put", lambda *_args, **_kwargs: {"ok": True})
            result = self.client.update_price_and_date_info(
                self.transaction_id, payload
            )
            assert result == {"ok": True}

        assert payload["listingCommission"]["negativeOrEmpty"] is False
        assert payload["saleCommission"]["negativeOrEmpty"] is False

    @responses.activate
    def test_update_personal_deal_info(self) -> None:
        """Test update_personal_deal_info endpoint."""
        expected_response = {"success": True, "deal_info_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/personal-deal-info",
            json=expected_response,
            status=200,
        )

        deal_info = {"deal_type": "SALE", "personal_notes": "Important deal"}
        result = self.client.update_personal_deal_info(self.transaction_id, deal_info)

        assert result == expected_response

    @responses.activate
    def test_update_owner_info(self) -> None:
        """Test update_owner_info endpoint."""
        expected_response = {"success": True, "owner_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/owner-info",
            json=expected_response,
            status=200,
        )

        owner_info = {"owner_name": "Property Owner", "agent_id": "agent-789"}
        result = self.client.update_owner_info(self.transaction_id, owner_info)

        assert result == expected_response

    @responses.activate
    def test_add_participant(self) -> None:
        """Test add_participant endpoint sends multipart/form-data."""
        expected_response = {"success": True, "participant_added": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/other-participants",
            json=expected_response,
            status=200,
        )

        participant_info = {"role": "INSPECTOR", "name": "Inspector Joe"}
        result = self.client.add_participant(self.transaction_id, participant_info)

        assert result == expected_response

        # Verify that the request was sent as multipart/form-data
        request = responses.calls[0].request
        content_type = request.headers.get("Content-Type", "")
        # The actual Content-Type will be multipart/form-data with a boundary
        assert content_type and "multipart/form-data" in content_type
        # Verify no JSON content-type
        assert content_type and "application/json" not in content_type

    @responses.activate
    def test_add_opcity(self) -> None:
        """Test add_opcity endpoint."""
        expected_response = {"success": True, "opcity_enabled": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/opcity",
            json=expected_response,
            status=200,
        )

        result = self.client.add_opcity(self.transaction_id, opcity=True)

        assert result == expected_response
        # Check query parameter
        assert "opcity=True" in responses.calls[0].request.url

    @responses.activate
    def test_update_mortgage_info(self) -> None:
        """Test update_mortgage_info endpoint."""
        expected_response = {"success": True, "mortgage_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/mortgage-info",
            json=expected_response,
            status=200,
        )

        mortgage_info = {"lender": "Bank of America", "loan_amount": 400000}
        result = self.client.update_mortgage_info(self.transaction_id, mortgage_info)

        assert result == expected_response

    @responses.activate
    def test_update_location_info(self) -> None:
        """Test update_location_info endpoint."""
        expected_response = {"success": True, "location_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/location-info",
            json=expected_response,
            status=200,
        )

        location_info = {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CALIFORNIA",
        }
        result = self.client.update_location_info(self.transaction_id, location_info)

        assert result == expected_response

    @responses.activate
    def test_update_fmls_info(self) -> None:
        """Test update_fmls_info endpoint."""
        expected_response = {"success": True, "fmls_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/fmls",
            json=expected_response,
            status=200,
        )

        fmls_info = {"listed_on_fmls": True, "mls_number": "ML123456"}
        result = self.client.update_fmls_info(self.transaction_id, fmls_info)

        assert result == expected_response

    @responses.activate
    def test_add_double_ender_agent(self) -> None:
        """Test add_double_ender_agent endpoint."""
        expected_response = {"success": True, "double_ender_added": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/double-ender-agent",
            json=expected_response,
            status=200,
        )

        agent_info = {"agent_id": "agent-999", "represents_both": True}
        result = self.client.add_double_ender_agent(self.transaction_id, agent_info)

        assert result == expected_response

    @responses.activate
    def test_add_commission_payer(self) -> None:
        """Test add_commission_payer endpoint."""
        expected_response = {
            "id": self.transaction_id,
            "commissionPayerInfo": {
                "id": "commission-payer-id",
                "role": "REAL",
                "firstName": "Commission",
                "lastName": "Payer",
                "companyName": "Commission Company LLC",
                "email": "commission@example.com",
                "phoneNumber": "(555) 111-2222",
                "receivesInvoice": True,
            },
        }
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/commission-payer",
            json=expected_response,
            status=200,
        )

        commission_info = {
            "role": "REAL",
            "firstName": "Commission",
            "lastName": "Payer",
            "email": "commission@example.com",
            "phoneNumber": "(555) 111-2222",
            "companyName": "Commission Company LLC",
            "receivesInvoice": True,
            "opCityReferral": False,
            "optedInForEcp": False,
        }
        result = self.client.add_commission_payer(self.transaction_id, commission_info)

        assert result == expected_response

    @responses.activate
    def test_update_commission_splits(self) -> None:
        """Test update_commission_splits endpoint."""
        expected_response = {"success": True, "splits_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/commission-info",
            json=expected_response,
            status=200,
        )

        commission_splits = [
            {"agent_id": "agent-1", "percentage": 60},
            {"agent_id": "agent-2", "percentage": 40},
        ]
        result = self.client.update_commission_splits(
            self.transaction_id, commission_splits
        )

        assert result == expected_response

    @responses.activate
    def test_add_co_agent(self) -> None:
        """Test add_co_agent endpoint."""
        expected_response = {"success": True, "co_agent_added": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/co-agent",
            json=expected_response,
            status=200,
        )

        co_agent_info = {"agent_id": "co-agent-123", "split_percentage": 30}
        result = self.client.add_co_agent(self.transaction_id, co_agent_info)

        assert result == expected_response

    @responses.activate
    def test_add_buyer(self) -> None:
        """Test add_buyer endpoint."""
        expected_response = {"success": True, "buyer_added": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/buyer",
            json=expected_response,
            status=200,
        )

        buyer_info = {"name": "Jane Buyer", "email": "jane.buyer@example.com"}
        result = self.client.add_buyer(self.transaction_id, buyer_info)

        assert result == expected_response

    def test_add_buyer_rejects_snake_case_fields(self) -> None:
        """Test add_buyer rejects snake_case field names."""
        with pytest.raises(InvalidFieldNameError):
            self.client.add_buyer(
                self.transaction_id, {"phone_number": "1(555) 111-2222"}
            )

    @responses.activate
    def test_update_buyer_and_seller_info(self) -> None:
        """Test update_buyer_and_seller_info endpoint."""
        expected_response = {"success": True, "buyer_seller_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/buyer-seller-info",
            json=expected_response,
            status=200,
        )

        buyer_seller_info = {
            "buyer": {"name": "John Buyer"},
            "seller": {"name": "Jane Seller"},
        }
        result = self.client.update_buyer_and_seller_info(
            self.transaction_id, buyer_seller_info
        )

        assert result == expected_response

    @responses.activate
    def test_update_additional_fees_info(self) -> None:
        """Test update_additional_fees_info endpoint."""
        expected_response = {"success": True, "fees_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/additional-fees-info",
            json=expected_response,
            status=200,
        )

        fees_info = {"inspection_fee": 500, "appraisal_fee": 400}
        result = self.client.update_additional_fees_info(self.transaction_id, fees_info)

        assert result == expected_response

    @responses.activate
    def test_add_referral_info_v2(self) -> None:
        """Test add_referral_info_v2 endpoint."""
        expected_response = {"success": True, "referral_added_v2": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/add-referral-info",
            json=expected_response,
            status=200,
        )

        referral_info = {"type": "AGENT", "agent_id": "ref-agent-456"}
        result = self.client.add_referral_info_v2(self.transaction_id, referral_info)

        assert result == expected_response

    # ===== NEW ENDPOINT TESTS =====

    # GET endpoint tests
    @responses.activate
    def test_get_transaction_builders(self) -> None:
        """Test get_transaction_builders endpoint."""
        expected_response = {"builders": [], "total": 0}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_builders(
            limit=10, from_offset=0, yenta_id="user-123"
        )

        assert result == expected_response
        request = responses.calls[0].request
        assert "limit=10" in request.url
        assert "from=0" in request.url
        assert "yentaId=user-123" in request.url
        assert "type=TRANSACTION" in request.url

    @responses.activate
    def test_get_transaction_builders_paged(self) -> None:
        """Test get_transaction_builders_paged endpoint."""
        expected_response = {"builders": [], "total": 0}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/paged",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_builders_paged(
            limit=20, from_offset=10, yenta_id="user-456", builder_type="LISTING"
        )

        assert result == expected_response
        request = responses.calls[0].request
        assert "limit=20" in request.url
        assert "from=10" in request.url
        assert "type=LISTING" in request.url

    @responses.activate
    def test_get_transaction_builder(self) -> None:
        """Test get_transaction_builder endpoint."""
        expected_response = {"id": self.transaction_id, "status": "DRAFT"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}",
            json=expected_response,
            status=200,
        )

        result = self.client.get_transaction_builder(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_builder_features(self) -> None:
        """Test get_builder_features endpoint."""
        expected_response = {"features": ["feature1", "feature2"]}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/features",
            json=expected_response,
            status=200,
        )

        result = self.client.get_builder_features(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_eligible_for_mortgage_ecp(self) -> None:
        """Test get_eligible_for_mortgage_ecp endpoint."""
        expected_response = {"eligible": True}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/eligible-for-mortgage-ecp",
            json=expected_response,
            status=200,
        )

        result = self.client.get_eligible_for_mortgage_ecp(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_get_commission_payer_roles_and_display_name(self) -> None:
        """Test get_commission_payer_roles_and_display_name endpoint."""
        expected_response = {"roles": {"SELLER": "Seller", "BUYER": "Buyer"}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/commission-payer-roles-and-display-name",
            json=expected_response,
            status=200,
        )

        result = self.client.get_commission_payer_roles_and_display_name(
            self.transaction_id
        )

        assert result == expected_response

    @responses.activate
    def test_get_commission_payer_roles(self) -> None:
        """Test get_commission_payer_roles endpoint."""
        expected_response = {"roles": ["SELLER", "BUYER", "LENDER"]}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/commission-payer-roles",
            json=expected_response,
            status=200,
        )

        result = self.client.get_commission_payer_roles()

        assert result == expected_response

    @responses.activate
    def test_get_commission_payer_roles_and_display_names(self) -> None:
        """Test get_commission_payer_roles_and_display_names endpoint."""
        expected_response = {"roles": {"SELLER": "Seller", "BUYER": "Buyer"}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/commission-payer-roles-and-display-name",
            json=expected_response,
            status=200,
        )

        result = self.client.get_commission_payer_roles_and_display_names()

        assert result == expected_response

    @responses.activate
    def test_get_commission_payer_roles_and_display_names_with_representation_type(
        self,
    ) -> None:
        """Test optional representationType param is passed through."""
        expected_response = {"roles": {"SELLER": "Seller"}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/commission-payer-roles-and-display-name",
            json=expected_response,
            status=200,
        )

        result = self.client.get_commission_payer_roles_and_display_names(
            representation_type="SELLER"
        )
        assert result == expected_response
        assert "representationType=SELLER" in responses.calls[0].request.url

    @responses.activate
    def test_get_metadata_for_participant_creation(self) -> None:
        """Test get_metadata_for_participant_creation endpoint."""
        expected_response = {"metadata": {"required_fields": ["name", "email"]}}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/metadata-for-participant-creation/BUYER_AGENT",
            json=expected_response,
            status=200,
        )

        result = self.client.get_metadata_for_participant_creation(
            self.transaction_id, "BUYER_AGENT"
        )

        assert result == expected_response

    # POST endpoint tests
    @responses.activate
    def test_create_transaction_builder(self) -> None:
        """Test create_transaction_builder endpoint."""
        expected_response = {"id": "new-builder-123"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder",
            json=expected_response,
            status=200,
        )

        result = self.client.create_transaction_builder("LISTING")

        assert result == {"id": "new-builder-123"}  # Method now returns dict format
        request = responses.calls[0].request
        assert "type=LISTING" in request.url

    @responses.activate
    def test_create_transaction_builder_string_response(self) -> None:
        """Test create_transaction_builder with string response."""
        # API sometimes returns just a string ID
        expected_response = '"new-builder-456"'
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder",
            body=expected_response,
            status=200,
        )

        result = self.client.create_transaction_builder()

        # Should wrap string response in dict format
        assert result == {"id": "new-builder-456"}

    @responses.activate
    def test_create_transaction_builder_message_response(self) -> None:
        """Test create_transaction_builder wraps dict message field as id."""
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder",
            json={"message": "builder-xyz"},
            status=200,
        )

        assert self.client.create_transaction_builder() == {"id": "builder-xyz"}

    @responses.activate
    def test_create_builder_from_transaction(self) -> None:
        """Test create_builder_from_transaction endpoint."""
        expected_response = {"success": True, "builder_id": "builder-456"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/transaction-to-builder",
            json=expected_response,
            status=200,
        )

        result = self.client.create_builder_from_transaction(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_convert_transaction_to_builder(self) -> None:
        """Test convert_transaction_to_builder convenience method."""
        expected_response = {"success": True, "builder_id": "builder-999"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/transaction-to-builder",
            json=expected_response,
            status=200,
        )

        result = self.client.convert_transaction_to_builder(self.transaction_id)
        assert result == expected_response

    @responses.activate
    def test_convert_listing_transaction_to_builder(self) -> None:
        """Test listing transaction to builder conversion."""
        listing_transaction_id = "listing-transaction-abc"
        expected_response = {"success": True, "builder_id": "builder-from-listing"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder/{listing_transaction_id}/transaction-to-builder",
            json=expected_response,
            status=200,
        )

        result = self.client.convert_listing_transaction_to_builder(
            listing_transaction_id
        )
        assert result == expected_response

    @responses.activate
    def test_convert_listing_to_transaction_deprecated_alias(self) -> None:
        """Test legacy alias convert_listing_to_transaction still works."""
        listing_transaction_id = "listing-transaction-legacy"
        expected_response = {"success": True, "builder_id": "legacy-builder"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder/{listing_transaction_id}/transaction-to-builder",
            json=expected_response,
            status=200,
        )

        result = self.client.convert_listing_to_transaction(listing_transaction_id)
        assert result == expected_response

    @responses.activate
    def test_add_transaction_coordinator(self) -> None:
        """Test add_transaction_coordinator endpoint."""
        expected_response = {"success": True, "coordinator_added": True}
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/transaction-coordinator/coord-123",
            json=expected_response,
            status=200,
        )

        result = self.client.add_transaction_coordinator(
            self.transaction_id, "coord-123"
        )

        assert result == expected_response

    @responses.activate
    def test_submit_transaction(self) -> None:
        """Test submit_transaction endpoint."""
        expected_response = {"success": True, "transaction_id": "tx-789"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/submit",
            json=expected_response,
            status=200,
        )

        result = self.client.submit_transaction(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_update_title_contract(self) -> None:
        """Test update_title_contract endpoint."""
        expected_response = {"success": True, "title_contract_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/title-contract",
            json=expected_response,
            status=200,
        )

        title_contract_info = {"contract_type": "PURCHASE", "terms": "Standard terms"}
        result = self.client.update_title_contract(
            self.transaction_id, title_contract_info
        )

        assert result == expected_response

    @responses.activate
    def test_mortgage_ecp_opt_out(self) -> None:
        """Test mortgage_ecp_opt_out endpoint."""
        expected_response = {"success": True, "opted_out": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/mortgage-ecp-opt-out",
            json=expected_response,
            status=200,
        )

        result = self.client.mortgage_ecp_opt_out(self.transaction_id)

        assert result == expected_response

    @responses.activate
    def test_mortgage_ecp_opt_in(self) -> None:
        """Test mortgage_ecp_opt_in endpoint."""
        expected_response = {"success": True, "opted_in": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/mortgage-ecp-opt-in",
            json=expected_response,
            status=200,
        )

        result = self.client.mortgage_ecp_opt_in(self.transaction_id)

        assert result == expected_response

    # DELETE endpoint tests
    @responses.activate
    def test_delete_transaction_builder(self) -> None:
        """Test delete_transaction_builder endpoint."""
        expected_response = {"success": True}
        responses.add(
            responses.DELETE,
            f"{self.base_url}/transaction-builder/{self.transaction_id}",
            json=expected_response,
            status=200,
        )

        result = self.client.delete_transaction_builder(self.transaction_id)

        assert result == expected_response

    # Individual resource endpoint tests
    @responses.activate
    def test_get_seller(self) -> None:
        """Test get_seller endpoint."""
        expected_response = {"id": "seller-123", "name": "John Seller"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/seller/seller-123",
            json=expected_response,
            status=200,
        )

        result = self.client.get_seller(self.transaction_id, "seller-123")

        assert result == expected_response

    @responses.activate
    def test_update_seller(self) -> None:
        """Test update_seller endpoint."""
        expected_response = {"success": True, "seller_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/seller/seller-123",
            json=expected_response,
            status=200,
        )

        seller_info = {"name": "Updated Seller Name"}
        result = self.client.update_seller(
            self.transaction_id, "seller-123", seller_info
        )

        assert result == expected_response

    @responses.activate
    def test_delete_seller(self) -> None:
        """Test delete_seller endpoint."""
        expected_response = {"success": True}
        responses.add(
            responses.DELETE,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/seller/seller-123",
            json=expected_response,
            status=200,
        )

        result = self.client.delete_seller(self.transaction_id, "seller-123")

        assert result == expected_response

    @responses.activate
    def test_get_referral_participant(self) -> None:
        """Test get_referral_participant endpoint."""
        expected_response = {"id": "participant-456", "role": "REFERRER"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/referral-info/participant-456",
            json=expected_response,
            status=200,
        )

        result = self.client.get_referral_participant(
            self.transaction_id, "participant-456"
        )

        assert result == expected_response

    @responses.activate
    def test_update_referral_participant(self) -> None:
        """Test update_referral_participant endpoint."""
        expected_response = {"success": True, "participant_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/referral-info/participant-456",
            json=expected_response,
            status=200,
        )

        participant_info = {"status": "ACTIVE"}
        result = self.client.update_referral_participant(
            self.transaction_id, "participant-456", participant_info
        )

        assert result == expected_response

    @responses.activate
    def test_delete_referral_participant(self) -> None:
        """Test delete_referral_participant endpoint."""
        expected_response = {"success": True}
        responses.add(
            responses.DELETE,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/referral-info/participant-456",
            json=expected_response,
            status=200,
        )

        result = self.client.delete_referral_participant(
            self.transaction_id, "participant-456"
        )

        assert result == expected_response

    @responses.activate
    def test_get_other_participant(self) -> None:
        """Test get_other_participant endpoint."""
        expected_response = {"id": "other-456", "role": "INSPECTOR"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/other-participants/other-456",
            json=expected_response,
            status=200,
        )

        result = self.client.get_other_participant(self.transaction_id, "other-456")

        assert result == expected_response

    @responses.activate
    def test_update_other_participant(self) -> None:
        """Test update_other_participant endpoint."""
        expected_response = {"success": True, "participant_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/other-participants/other-456",
            json=expected_response,
            status=200,
        )

        participant_info = {"status": "ACTIVE"}
        result = self.client.update_other_participant(
            self.transaction_id, "other-456", participant_info
        )

        assert result == expected_response

    @responses.activate
    def test_delete_other_participant(self) -> None:
        """Test delete_other_participant endpoint."""
        expected_response = {"success": True}
        responses.add(
            responses.DELETE,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/other-participants/other-456",
            json=expected_response,
            status=200,
        )

        result = self.client.delete_other_participant(self.transaction_id, "other-456")

        assert result == expected_response

    @responses.activate
    def test_get_co_agent(self) -> None:
        """Test get_co_agent endpoint."""
        expected_response = {"id": "co-agent-789", "name": "Co Agent"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/co-agent/co-agent-789",
            json=expected_response,
            status=200,
        )

        result = self.client.get_co_agent(self.transaction_id, "co-agent-789")

        assert result == expected_response

    @responses.activate
    def test_update_co_agent(self) -> None:
        """Test update_co_agent endpoint."""
        expected_response = {"success": True, "co_agent_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/co-agent/co-agent-789",
            json=expected_response,
            status=200,
        )

        co_agent_info = {"commission_split": 50}
        result = self.client.update_co_agent(
            self.transaction_id, "co-agent-789", co_agent_info
        )

        assert result == expected_response

    @responses.activate
    def test_delete_co_agent(self) -> None:
        """Test delete_co_agent endpoint."""
        expected_response = {"success": True}
        responses.add(
            responses.DELETE,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/co-agent/co-agent-789",
            json=expected_response,
            status=200,
        )

        result = self.client.delete_co_agent(self.transaction_id, "co-agent-789")

        assert result == expected_response

    @responses.activate
    def test_get_buyer(self) -> None:
        """Test get_buyer endpoint."""
        expected_response = {"id": "buyer-321", "name": "John Buyer"}
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/buyer/buyer-321",
            json=expected_response,
            status=200,
        )

        result = self.client.get_buyer(self.transaction_id, "buyer-321")

        assert result == expected_response

    @responses.activate
    def test_update_buyer(self) -> None:
        """Test update_buyer endpoint."""
        expected_response = {"success": True, "buyer_updated": True}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/buyer/buyer-321",
            json=expected_response,
            status=200,
        )

        buyer_info = {"phone": "555-0123"}
        result = self.client.update_buyer(self.transaction_id, "buyer-321", buyer_info)

        assert result == expected_response

    @responses.activate
    def test_delete_buyer(self) -> None:
        """Test delete_buyer endpoint."""
        expected_response = {"success": True}
        responses.add(
            responses.DELETE,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/buyer/buyer-321",
            json=expected_response,
            status=200,
        )

        result = self.client.delete_buyer(self.transaction_id, "buyer-321")

        assert result == expected_response

    def test_client_inheritance(self) -> None:
        """Test that TransactionBuilderClient inherits from BaseClient."""
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
            responses.PUT,
            f"{self.base_url}/transaction-builder/{self.transaction_id}/title",
            json={"message": "Transaction not found"},
            status=404,
        )

        with pytest.raises(NotFoundError):
            self.client.update_title_info(self.transaction_id, {"title": "Test"})

    def test_update_owner_agent_info_validation_branches(self) -> None:
        """Test update_owner_agent_info validates payload shape before sending."""
        # Missing ownerAgent
        with pytest.raises(
            ValidationError, match="Missing required field 'ownerAgent'"
        ):
            self.client.update_owner_agent_info(self.transaction_id, {"officeId": "o1"})

        # ownerAgent must be dict
        with pytest.raises(InvalidFieldValueError, match="ownerAgent"):
            self.client.update_owner_agent_info(
                self.transaction_id,
                {"ownerAgent": "nope", "officeId": "o1", "teamId": "t1"},
            )

        # Missing agentId / role
        with pytest.raises(ValidationError, match="agentId"):
            self.client.update_owner_agent_info(
                self.transaction_id,
                {
                    "ownerAgent": {"role": "BUYERS_AGENT"},
                    "officeId": "o1",
                    "teamId": "t1",
                },
            )
        with pytest.raises(ValidationError, match="role"):
            self.client.update_owner_agent_info(
                self.transaction_id,
                {"ownerAgent": {"agentId": "a1"}, "officeId": "o1", "teamId": "t1"},
            )

        # Invalid role
        with pytest.raises(InvalidFieldValueError, match="role"):
            self.client.update_owner_agent_info(
                self.transaction_id,
                {
                    "ownerAgent": {"agentId": "a1", "role": "LISTING_AGENT"},
                    "officeId": "o1",
                    "teamId": "t1",
                },
            )

        # Missing officeId / teamId
        with pytest.raises(ValidationError, match="officeId"):
            self.client.update_owner_agent_info(
                self.transaction_id,
                {
                    "ownerAgent": {"agentId": "a1", "role": "BUYERS_AGENT"},
                    "teamId": "t1",
                },
            )
        with pytest.raises(ValidationError, match="teamId"):
            self.client.update_owner_agent_info(
                self.transaction_id,
                {
                    "ownerAgent": {"agentId": "a1", "role": "BUYERS_AGENT"},
                    "officeId": "o1",
                },
            )

    def test_update_owner_agent_info_sequence_error(self) -> None:
        """Test update_owner_agent_info maps generic invalid-request errors to TransactionSequenceError."""
        payload = {
            "ownerAgent": {"agentId": "a1", "role": "BUYERS_AGENT"},
            "officeId": "o1",
            "teamId": "t1",
        }

        def _raise(*_args: Any, **_kwargs: Any) -> Dict[str, Any]:
            raise ValidationError("Bad request: Invalid request")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "put", _raise)
            with pytest.raises(TransactionSequenceError):
                self.client.update_owner_agent_info(self.transaction_id, payload)

    def test_update_owner_agent_info_reraises_other_validation_error(self) -> None:
        """Non-sequence ValidationError should be re-raised as-is."""
        payload = {
            "ownerAgent": {"agentId": "a1", "role": "BUYERS_AGENT"},
            "officeId": "o1",
            "teamId": "t1",
        }

        def _raise(*_args: Any, **_kwargs: Any) -> Dict[str, Any]:
            raise ValidationError("Bad request: Something else")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "put", _raise)
            with pytest.raises(ValidationError, match="Something else"):
                self.client.update_owner_agent_info(self.transaction_id, payload)

    def test_backward_compat_aliases_delegate(self) -> None:
        """Back-compat alias methods should delegate to the canonical implementation."""
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "add_buyer", lambda *_a, **_k: {"buyer": True})
            mp.setattr(self.client, "add_seller", lambda *_a, **_k: {"seller": True})
            mp.setattr(
                self.client,
                "update_location_info",
                lambda *_a, **_k: {"location": True},
            )
            mp.setattr(
                self.client,
                "update_price_and_date_info",
                lambda *_a, **_k: {"price_date": True},
            )
            mp.setattr(
                self.client, "add_commission_payer", lambda *_a, **_k: {"payer": True}
            )
            mp.setattr(
                self.client,
                "update_personal_deal_info",
                lambda *_a, **_k: {"deal": True},
            )
            mp.setattr(
                self.client, "update_title_info", lambda *_a, **_k: {"title": True}
            )

            assert self.client.put_buyer_to_draft("t1", {}) == {"buyer": True}
            assert self.client.put_seller_to_draft("t1", {}) == {"seller": True}
            assert self.client.put_location_to_draft("t1", {}) == {"location": True}
            assert self.client.put_price_and_date_to_draft("t1", {}) == {
                "price_date": True
            }
            assert self.client.update_commission_payer("t1", {}) == {"payer": True}
            assert self.client.update_personal_deal("t1", {}) == {"deal": True}
            assert self.client.update_real_title("t1", {}) == {"title": True}

    def test_owner_agent_convenience_methods_and_helpers(self) -> None:
        """Cover owner-agent convenience helpers for team/office selection."""
        import rezen.users as users_module

        class DummyUsersClient:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

            def get_current_user(self) -> Dict[str, Any]:
                return {
                    "id": "user-1",
                    "teams": [
                        {
                            "teamId": "team-1",
                            "teamName": "Team One",
                            "teamRoles": ["LEADER"],
                            "teamType": "NORMAL",
                        }
                    ],
                    "offices": [{"id": "office-1"}],
                }

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClient)
            mp.setattr(
                self.client, "update_owner_agent_info", lambda *_a, **_k: {"ok": True}
            )

            result = self.client.set_current_user_as_owner_agent(
                transaction_builder_id="builder-1",
                role="BUYERS_AGENT",
                users_client=None,
            )
            assert result == {"ok": True}

        # get_user_teams_and_offices import branch + leader selection
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClient)
            info = self.client.get_user_teams_and_offices(users_client=None)
            assert info["default_team"]["id"] == "team-1"
            assert info["office_id"] == "office-1"

        # set_current_user_as_owner_agent_with_team import branch + membership validation
        class DummyUsersClientMultiTeam(DummyUsersClient):
            def get_current_user(self) -> Dict[str, Any]:
                base = super().get_current_user()
                base["teams"].append(
                    {
                        "teamId": "team-2",
                        "teamName": "Team Two",
                        "teamRoles": ["ADMIN"],
                        "teamType": "NORMAL",
                    }
                )
                return base

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientMultiTeam)
            mp.setattr(
                self.client, "update_owner_agent_info", lambda *_a, **_k: {"ok": True}
            )
            assert self.client.set_current_user_as_owner_agent_with_team(
                transaction_builder_id="builder-1",
                role="SELLERS_AGENT",
                team_id="team-2",
                users_client=None,
            ) == {"ok": True}

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientMultiTeam)
            with pytest.raises(ValidationError, match="not a member of team"):
                self.client.set_current_user_as_owner_agent_with_team(
                    transaction_builder_id="builder-1",
                    role="SELLERS_AGENT",
                    team_id="team-unknown",
                    users_client=None,
                )

    def test_owner_agent_convenience_additional_branches(self) -> None:
        """Cover remaining owner-agent helper branches (warnings and error paths)."""
        import builtins

        import rezen.users as users_module

        class DummyUsersClientNoDefaultTeam:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

            def get_current_user(self) -> Dict[str, Any]:
                return {"id": "user-1", "teams": [], "offices": [{"id": "office-1"}]}

        class DummyUsersClientNoOffices:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

            def get_current_user(self) -> Dict[str, Any]:
                return {
                    "id": "user-1",
                    "teams": [
                        {
                            "teamId": "team-1",
                            "teamName": "Team One",
                            "teamRoles": ["LEADER"],
                            "teamType": "NORMAL",
                        }
                    ],
                    "offices": [],
                }

        class DummyUsersClientTwoTeams:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

            def get_current_user(self) -> Dict[str, Any]:
                return {
                    "id": "user-1",
                    "teams": [
                        {
                            "teamId": "team-1",
                            "teamName": "Team One",
                            "teamRoles": ["LEADER"],
                            "teamType": "NORMAL",
                        },
                        {
                            "teamId": "team-2",
                            "teamName": "Team Two",
                            "teamRoles": ["ADMIN"],
                            "teamType": "NORMAL",
                        },
                    ],
                    "offices": [{"id": "office-1"}],
                }

        # Warning branch: multiple teams prints a message.
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientTwoTeams)
            mp.setattr(builtins, "print", lambda *_a, **_k: None)
            mp.setattr(
                self.client, "update_owner_agent_info", lambda *_a, **_k: {"ok": True}
            )
            self.client.set_current_user_as_owner_agent(
                transaction_builder_id="builder-1",
                role="BUYERS_AGENT",
                users_client=None,
            )

        # No default team branch.
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientNoDefaultTeam)
            mp.setattr(
                self.client,
                "get_user_teams_and_offices",
                lambda *_a, **_k: {"default_team": None},
            )
            with pytest.raises(
                ValidationError, match="must belong to at least one team"
            ):
                self.client.set_current_user_as_owner_agent(
                    transaction_builder_id="builder-1",
                    role="BUYERS_AGENT",
                    users_client=None,
                )

        # No offices branch.
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientNoOffices)
            mp.setattr(
                self.client,
                "get_user_teams_and_offices",
                lambda *_a, **_k: {"default_team": {"id": "team-1"}},
            )
            with pytest.raises(ValidationError, match="no offices available"):
                self.client.set_current_user_as_owner_agent(
                    transaction_builder_id="builder-1",
                    role="BUYERS_AGENT",
                    users_client=None,
                )

        # get_user_teams_and_offices no offices ValueError branch.
        class DummyUsersClientNoOfficesForTeams:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

            def get_current_user(self) -> Dict[str, Any]:
                return {"id": "user-1", "teams": [], "offices": []}

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientNoOfficesForTeams)
            with pytest.raises(ValueError, match="User has no offices"):
                self.client.get_user_teams_and_offices(users_client=None)

        # Admin-default branch.
        class DummyUsersClientAdminTeam:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

            def get_current_user(self) -> Dict[str, Any]:
                return {
                    "id": "user-1",
                    "teams": [
                        {
                            "teamId": "team-admin",
                            "teamName": "Admin Team",
                            "teamRoles": ["ADMIN"],
                            "teamType": "NORMAL",
                        }
                    ],
                    "offices": [{"id": "office-1"}],
                }

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientAdminTeam)
            info = self.client.get_user_teams_and_offices(users_client=None)
            assert info["default_team"]["role"] == "ADMIN"

        # Fallback-to-first-team branch (no roles => MEMBER).
        class DummyUsersClientMemberTeam:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

            def get_current_user(self) -> Dict[str, Any]:
                return {
                    "id": "user-1",
                    "teams": [
                        {
                            "teamId": "team-member",
                            "teamName": "Member Team",
                            "teamRoles": [],
                            "teamType": "NORMAL",
                        }
                    ],
                    "offices": [{"id": "office-1"}],
                }

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientMemberTeam)
            info = self.client.get_user_teams_and_offices(users_client=None)
            assert info["default_team"]["id"] == "team-member"

        # set_current_user_as_owner_agent_with_team no offices branch.
        class DummyUsersClientWithTeamNoOffices:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

            def get_current_user(self) -> Dict[str, Any]:
                return {
                    "id": "user-1",
                    "teams": [{"teamId": "team-1"}],
                    "offices": [],
                }

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(users_module, "UsersClient", DummyUsersClientWithTeamNoOffices)
            with pytest.raises(ValidationError, match="no offices available"):
                self.client.set_current_user_as_owner_agent_with_team(
                    transaction_builder_id="builder-1",
                    role="BUYERS_AGENT",
                    team_id="team-1",
                    users_client=None,
                )

    def test_create_complete_transaction_example_returns_string(self) -> None:
        """create_complete_transaction_example should return documentation string."""
        example = self.client.create_complete_transaction_example()
        assert isinstance(example, str)
        assert "COMPLETE WORKING TRANSACTION SUBMISSION EXAMPLE" in example

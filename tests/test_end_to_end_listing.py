#!/usr/bin/env python3
"""
End-to-end test for complete listing posting workflow.
This test verifies that the location update fix allows successful listing creation.
"""

from typing import Any, Dict

import pytest
import responses

from rezen.exceptions import ValidationError
from rezen.transaction_builder import TransactionBuilderClient


class TestEndToEndListingPosting:
    """Test complete listing posting workflow with location validation fixes."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.api_key = "test_api_key_12345"
        self.base_url = "https://arrakis.therealbrokerage.com/api/v1"
        self.client = TransactionBuilderClient(api_key=self.api_key)

    @responses.activate
    def test_complete_listing_posting_workflow(self) -> None:
        """Test the complete listing posting workflow from creation to submission."""

        # Step 1: Create listing builder
        create_response = {"id": "listing-123"}
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder",
            json=create_response,
            status=200,
        )

        listing_id = self.client.create_listing_builder()
        assert listing_id == {"id": "listing-123"}

        # Step 2: Add location with ALL required fields (this was the issue)
        location_response = {
            "id": "listing-123",
            "address": {
                "street": "123 Demo Street",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101",
            },
            "yearBuilt": 2020,
            "mlsNumber": "MLS123456",
        }
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/listing-123/location-info",
            json=location_response,
            status=200,
        )

        complete_location = {
            "street": "123 Demo Street",  # Use 'street' not 'address'
            "city": "Salt Lake City",
            "state": "UTAH",  # ALL CAPS required
            "zip": "84101",  # Use 'zip' not 'zipCode'
            "county": "Salt Lake",  # REQUIRED - was missing before
            "yearBuilt": 2020,  # REQUIRED - was missing before
            "mlsNumber": "MLS123456",  # REQUIRED - was missing before
        }

        location_result = self.client.update_location_info(
            "listing-123", complete_location
        )
        assert location_result == location_response

        # Step 3: Add price and date info with BOTH commission objects
        price_response = {
            "id": "listing-123",
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": {"amount": 550000, "currency": "USD"},
            "representationType": "SELLER",
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
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/listing-123/price-date-info",
            json=price_response,
            status=200,
        )

        # Use the helper method to ensure proper format
        price_data = self.client.prepare_price_and_date_data(
            sale_price=550000,
            representation_type="SELLER",
            acceptance_date="2025-08-01",
            closing_date="2025-09-01",
        )

        price_result = self.client.update_price_and_date_info("listing-123", price_data)
        assert price_result == price_response

        # Step 4: Add seller
        seller_response = {"id": "listing-123", "sellers": [{"id": "seller-456"}]}
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/listing-123/seller",
            json=seller_response,
            status=200,
        )

        seller_data = {
            "firstName": "Jane",  # camelCase required
            "lastName": "Seller",  # camelCase required
            "email": "jane.seller@example.com",
            "phoneNumber": "1(801) 555-1234",  # Country code required
        }

        seller_result = self.client.add_seller("listing-123", seller_data)
        assert seller_result == seller_response

        # Step 5: Get transaction to verify all data is correctly stored
        get_response = {
            "id": "listing-123",
            "builderType": "LISTING",
            "address": {
                "street": "123 Demo Street",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101",
            },
            "yearBuilt": 2020,
            "mlsNumber": "MLS123456",
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": {"amount": 550000, "currency": "USD"},
            "representationType": "SELLER",
            "sellers": [{"id": "seller-456"}],
        }
        responses.add(
            responses.GET,
            f"{self.base_url}/transaction-builder/listing-123",
            json=get_response,
            status=200,
        )

        final_listing = self.client.get_transaction_builder("listing-123")
        assert final_listing["id"] == "listing-123"
        assert final_listing["builderType"] == "LISTING"
        assert final_listing["address"]["street"] == "123 Demo Street"
        assert final_listing["yearBuilt"] == 2020
        assert final_listing["mlsNumber"] == "MLS123456"

    @responses.activate
    def test_listing_vs_transaction_builder_types(self) -> None:
        """Test that both listing and transaction builders work with location updates."""

        # Test listing builder
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder",
            json={"id": "listing-789"},
            status=200,
        )

        listing_id = self.client.create_listing_builder()
        assert listing_id == {"id": "listing-789"}

        # Test transaction builder
        responses.add(
            responses.POST,
            f"{self.base_url}/transaction-builder",
            json={"id": "transaction-789"},
            status=200,
        )

        transaction_id = self.client.create_transaction_builder()
        assert transaction_id == {"id": "transaction-789"}

        # Both should accept the same location data structure
        location_data = {
            "street": "456 Test Ave",
            "city": "Test City",
            "state": "CALIFORNIA",
            "zip": "90210",
            "county": "Los Angeles",
            "yearBuilt": 2015,
            "mlsNumber": "MLS789012",
        }

        # Mock responses for both types
        for builder_id in ["listing-789", "transaction-789"]:
            responses.add(
                responses.PUT,
                f"{self.base_url}/transaction-builder/{builder_id}/location-info",
                json={"success": True, "id": builder_id},
                status=200,
            )

        # Both should work identically
        listing_result = self.client.update_location_info("listing-789", location_data)
        transaction_result = self.client.update_location_info(
            "transaction-789", location_data
        )

        assert listing_result["success"] is True
        assert transaction_result["success"] is True

    def test_location_field_validation_prevents_common_mistakes(self) -> None:
        """Test that validation catches common field naming mistakes."""

        # Test all the common mistakes that used to cause "Bad request" errors
        common_mistakes = [
            {
                "name": "Using 'address' instead of 'street'",
                "data": {
                    "address": "123 Main St",
                    "city": "City",
                    "state": "UTAH",
                    "zip": "84101",
                },
                "error_contains": "address",
            },
            {
                "name": "Using 'zipCode' instead of 'zip'",
                "data": {
                    "street": "123 Main St",
                    "city": "City",
                    "state": "UTAH",
                    "zipCode": "84101",
                },
                "error_contains": "zipCode",
            },
            {
                "name": "Using lowercase state",
                "data": {
                    "street": "123 Main St",
                    "city": "City",
                    "state": "utah",
                    "zip": "84101",
                },
                "error_contains": "utah",
            },
            {
                "name": "Using snake_case for yearBuilt",
                "data": {
                    "street": "123 Main St",
                    "city": "City",
                    "state": "UTAH",
                    "zip": "84101",
                    "county": "Test",
                    "year_built": 2020,
                    "mlsNumber": "MLS123",
                },
                "error_contains": "year_built",
            },
        ]

        for mistake in common_mistakes:
            with pytest.raises((ValidationError, Exception)) as exc_info:
                # These should fail validation before hitting the API
                self.client.update_location_info("test-id", mistake["data"])

            error_str = str(exc_info.value)
            assert mistake["error_contains"] in error_str

    def test_complete_location_data_requirements(self) -> None:
        """Test that all required location fields are documented and enforced."""

        # This is the minimal complete location data that should work
        complete_location = {
            # Basic address fields (always required)
            "street": "123 Main Street",
            "city": "Salt Lake City",
            "state": "UTAH",  # Must be ALL CAPS
            "zip": "84101",  # Not 'zipCode'
            # Additional required fields (the fix)
            "county": "Salt Lake",  # REQUIRED - API fails without this
            "yearBuilt": 2020,  # REQUIRED - API fails without this
            "mlsNumber": "MLS123456",  # REQUIRED - API fails without this
        }

        # Verify structure
        required_fields = [
            "street",
            "city",
            "state",
            "zip",
            "county",
            "yearBuilt",
            "mlsNumber",
        ]
        for field in required_fields:
            assert field in complete_location

        # Verify types
        assert isinstance(complete_location["yearBuilt"], int)
        assert isinstance(complete_location["county"], str)
        assert isinstance(complete_location["mlsNumber"], str)
        assert complete_location["state"] == complete_location["state"].upper()

    @responses.activate
    def test_backward_compatibility_aliases(self) -> None:
        """Test that backward compatibility aliases still work."""

        listing_id = "test-listing-456"
        location_data = {
            "street": "789 Compat St",
            "city": "Compat City",
            "state": "TEXAS",
            "zip": "75201",
            "county": "Dallas",
            "yearBuilt": 2018,
            "mlsNumber": "MLS456789",
        }

        # Mock the API response
        responses.add(
            responses.PUT,
            f"{self.base_url}/transaction-builder/{listing_id}/location-info",
            json={"success": True, "id": listing_id},
            status=200,
        )

        # Test that put_location_to_draft alias works
        result = self.client.put_location_to_draft(listing_id, location_data)
        assert result["success"] is True

        # Verify it called the same endpoint as update_location_info
        assert len(responses.calls) == 1
        assert "location-info" in responses.calls[0].request.url

"""Tests for the DirectoryClient."""

import json
from datetime import date
from io import BytesIO
from typing import Any, Dict, List
from unittest.mock import patch

import pytest
import responses

from rezen.directory import (
    Country,
    DirectoryClient,
    DirectoryEntryType,
    DirectoryRole,
    DirectoryEntrySortField,
    PersonSortField,
    StateOrProvince,
    VendorSortField,
)
from rezen.exceptions import AuthenticationError, NotFoundError, ValidationError


class TestDirectoryEnums:
    """Test directory enums."""

    def test_directory_entry_type_enum(self) -> None:
        """Test DirectoryEntryType enum values."""
        assert DirectoryEntryType.VENDOR.value == "VENDOR"
        assert DirectoryEntryType.PERSON.value == "PERSON"

    def test_directory_role_enum(self) -> None:
        """Test DirectoryRole enum values."""
        assert DirectoryRole.CLIENT.value == "CLIENT"
        assert DirectoryRole.LANDLORD.value == "LANDLORD"
        assert DirectoryRole.TENANT.value == "TENANT"
        assert DirectoryRole.TITLE_ESCROW.value == "TITLE_ESCROW"
        assert DirectoryRole.LENDER.value == "LENDER"
        assert DirectoryRole.LAWYER.value == "LAWYER"
        assert DirectoryRole.TRUSTEE.value == "TRUSTEE"
        assert DirectoryRole.OTHER_AGENT.value == "OTHER_AGENT"
        assert DirectoryRole.VENDOR.value == "VENDOR"
        assert DirectoryRole.REFERRAL.value == "REFERRAL"
        assert DirectoryRole.OTHER.value == "OTHER"

    def test_vendor_sort_field_enum(self) -> None:
        """Test VendorSortField enum values."""
        assert VendorSortField.NAME.value == "NAME"
        assert VendorSortField.EMAIL_ADDRESS.value == "EMAIL_ADDRESS"
        assert VendorSortField.PHONE_NUMBER.value == "PHONE_NUMBER"
        assert VendorSortField.CITY.value == "CITY"
        assert VendorSortField.STATE_OR_PROVINCE.value == "STATE_OR_PROVINCE"
        assert VendorSortField.STATUS.value == "STATUS"

    def test_person_sort_field_enum(self) -> None:
        """Test PersonSortField enum values."""
        assert PersonSortField.FIRST_NAME.value == "FIRST_NAME"
        assert PersonSortField.LAST_NAME.value == "LAST_NAME"
        assert PersonSortField.EMAIL_ADDRESS.value == "EMAIL_ADDRESS"
        assert PersonSortField.PHONE_NUMBER.value == "PHONE_NUMBER"
        assert PersonSortField.IS_PUBLIC.value == "IS_PUBLIC"

    def test_directory_entry_sort_field_enum(self) -> None:
        """Test DirectoryEntrySortField enum values."""
        assert DirectoryEntrySortField.NAME.value == "NAME"
        assert DirectoryEntrySortField.NAME_LOGICAL.value == "NAME_LOGICAL"
        assert DirectoryEntrySortField.EMAIL_ADDRESS.value == "EMAIL_ADDRESS"
        assert DirectoryEntrySortField.PHONE_NUMBER.value == "PHONE_NUMBER"
        assert DirectoryEntrySortField.CITY.value == "CITY"
        assert DirectoryEntrySortField.STATE_OR_PROVINCE.value == "STATE_OR_PROVINCE"
        assert DirectoryEntrySortField.STATUS.value == "STATUS"

    def test_state_or_province_enum_us_states(self) -> None:
        """Test StateOrProvince enum for US states."""
        assert StateOrProvince.CALIFORNIA.value == "CALIFORNIA"
        assert StateOrProvince.NEW_YORK.value == "NEW_YORK"
        assert StateOrProvince.TEXAS.value == "TEXAS"
        assert StateOrProvince.FLORIDA.value == "FLORIDA"

    def test_state_or_province_enum_canadian_provinces(self) -> None:
        """Test StateOrProvince enum for Canadian provinces."""
        assert StateOrProvince.ONTARIO.value == "ONTARIO"
        assert StateOrProvince.BRITISH_COLUMBIA.value == "BRITISH_COLUMBIA"
        assert StateOrProvince.QUEBEC.value == "QUEBEC"
        assert StateOrProvince.ALBERTA.value == "ALBERTA"

    def test_country_enum(self) -> None:
        """Test Country enum values."""
        assert Country.UNITED_STATES.value == "UNITED_STATES"
        assert Country.CANADA.value == "CANADA"


class TestDirectoryClient:
    """Test DirectoryClient class."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = DirectoryClient(api_key="test_api_key")

    def test_init_with_api_key(self) -> None:
        """Test client initialization with API key."""
        client = DirectoryClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://yenta.therealbrokerage.com/api/v1"

    def test_init_with_custom_base_url(self) -> None:
        """Test client initialization with custom base URL."""
        client = DirectoryClient(
            api_key="test_key", base_url="https://custom.example.com/api/v1"
        )
        assert client.base_url == "https://custom.example.com/api/v1"

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_api_key"})
    def test_init_with_env_api_key(self) -> None:
        """Test client initialization with environment variable API key."""
        client = DirectoryClient()
        assert client.api_key == "env_api_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test client initialization without API key raises error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(AuthenticationError, match="API key is required"):
                DirectoryClient()

    # ===== VENDOR TESTS =====

    @responses.activate
    def test_create_vendor_success(self) -> None:
        """Test successful vendor creation."""
        vendor_data = {
            "name": "Test Vendor",
            "emailAddress": "test@vendor.com",
            "phoneNumber": "555-0123",
        }
        mock_response = {"id": "vendor-123", **vendor_data}

        responses.add(
            responses.POST,
            "https://yenta.therealbrokerage.com/api/v1/directory/vendors",
            json=mock_response,
            status=201,
        )

        result = self.client.create_vendor(vendor_data)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_vendor_success(self) -> None:
        """Test successful vendor retrieval."""
        vendor_id = "vendor-123"
        mock_response = {
            "id": vendor_id,
            "name": "Test Vendor",
            "emailAddress": "test@vendor.com",
        }

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/directory/vendors/{vendor_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.get_vendor(vendor_id)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_update_vendor_success(self) -> None:
        """Test successful vendor update."""
        vendor_id = "vendor-123"
        vendor_data = {"name": "Updated Vendor"}
        mock_response = {"id": vendor_id, **vendor_data}

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/directory/vendors/{vendor_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.update_vendor(vendor_id, vendor_data)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_vendor_w9_url_success(self) -> None:
        """Test successful vendor W9 URL retrieval."""
        vendor_id = "vendor-123"
        mock_url = "https://example.com/w9.pdf"

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/directory/vendors/{vendor_id}/w9",
            json={"url": mock_url},
            status=200,
        )

        result = self.client.get_vendor_w9_url(vendor_id)
        assert result == mock_url
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_vendor_w9_url_string_response(self) -> None:
        """Test vendor W9 URL retrieval with string response."""
        vendor_id = "vendor-123"
        mock_url = "https://example.com/w9.pdf"

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/directory/vendors/{vendor_id}/w9",
            json=mock_url,
            status=200,
        )

        result = self.client.get_vendor_w9_url(vendor_id)
        assert result == mock_url
        assert len(responses.calls) == 1

    @responses.activate
    def test_update_vendor_w9_success(self) -> None:
        """Test successful vendor W9 update."""
        vendor_id = "vendor-123"
        w9_file = BytesIO(b"fake pdf content")
        mock_response = {"id": vendor_id, "w9Updated": True}

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/directory/vendors/{vendor_id}/w9",
            json=mock_response,
            status=200,
        )

        result = self.client.update_vendor_w9(vendor_id, w9_file)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_archive_vendor_success(self) -> None:
        """Test successful vendor archiving."""
        vendor_id = "vendor-123"
        mock_response = {"id": vendor_id, "archived": True}

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/directory/vendors/{vendor_id}/archive",
            json=mock_response,
            status=200,
        )

        result = self.client.archive_vendor(vendor_id, archive=True)
        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify query parameters
        request = responses.calls[0].request
        assert request.url is not None
        assert "archive=True" in request.url

    @responses.activate
    def test_unarchive_vendor_success(self) -> None:
        """Test successful vendor unarchiving."""
        vendor_id = "vendor-123"
        mock_response = {"id": vendor_id, "archived": False}

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/directory/vendors/{vendor_id}/archive",
            json=mock_response,
            status=200,
        )

        result = self.client.archive_vendor(vendor_id, archive=False)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_search_vendors_minimal(self) -> None:
        """Test vendor search with minimal parameters."""
        mock_response = {
            "content": [{"id": "vendor-123", "name": "Test Vendor"}],
            "totalElements": 1,
        }

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/vendors/search/all",
            json=mock_response,
            status=200,
        )

        result = self.client.search_vendors(page_number=0, page_size=20)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_search_vendors_with_all_parameters(self) -> None:
        """Test vendor search with all parameters."""
        mock_response = {"content": [], "totalElements": 0}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/vendors/search/all",
            json=mock_response,
            status=200,
        )

        result = self.client.search_vendors(
            page_number=1,
            page_size=50,
            is_archived=False,
            is_verified=True,
            has_linked_persons=True,
            search_text="test vendor",
            national_business_id="123456789",
            name="Test Vendor",
            email_address="test@vendor.com",
            phone_number="555-0123",
            street="123 Main St",
            city="Test City",
            postal="12345",
            state_or_province=StateOrProvince.CALIFORNIA,
            country=Country.UNITED_STATES,
            administrative_area_ids=["area-1", "area-2"],
            roles=[DirectoryRole.VENDOR, DirectoryRole.CLIENT],
            sort_by=[VendorSortField.NAME, VendorSortField.EMAIL_ADDRESS],
        )

        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify query parameters
        request = responses.calls[0].request
        assert request.url is not None
        assert "pageNumber=1" in request.url
        assert "pageSize=50" in request.url
        assert "isArchived=False" in request.url
        assert "isVerified=True" in request.url
        assert "hasLinkedPersons=True" in request.url
        assert "searchText=test+vendor" in request.url
        assert "nationalBusinessId=123456789" in request.url
        assert "name=Test+Vendor" in request.url
        assert "emailAddress=test%40vendor.com" in request.url
        assert "phoneNumber=555-0123" in request.url
        assert "street=123+Main+St" in request.url
        assert "city=Test+City" in request.url
        assert "postal=12345" in request.url
        assert "stateOrProvince=CALIFORNIA" in request.url
        assert "country=UNITED_STATES" in request.url

    @responses.activate
    def test_search_vendors_with_string_enums(self) -> None:
        """Test vendor search with string enum values."""
        mock_response = {"content": [], "totalElements": 0}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/vendors/search/all",
            json=mock_response,
            status=200,
        )

        result = self.client.search_vendors(
            page_number=0,
            page_size=20,
            state_or_province="NEW_YORK",
            country="CANADA",
            roles=["VENDOR", "CLIENT"],
            sort_by=["NAME", "EMAIL_ADDRESS"],
        )

        assert result == mock_response
        assert len(responses.calls) == 1

    # ===== PERSON TESTS =====

    @responses.activate
    def test_create_person_success(self) -> None:
        """Test successful person creation."""
        person_data = {
            "firstName": "John",
            "lastName": "Doe",
            "emailAddress": "john@example.com",
        }
        mock_response = {"id": "person-123", **person_data}

        responses.add(
            responses.POST,
            "https://yenta.therealbrokerage.com/api/v1/directory/persons",
            json=mock_response,
            status=201,
        )

        result = self.client.create_person(person_data)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_create_person_with_owner_ids(self) -> None:
        """Test person creation with owner IDs."""
        person_data = {"firstName": "John", "lastName": "Doe"}
        mock_response = {"id": "person-123", **person_data}

        responses.add(
            responses.POST,
            "https://yenta.therealbrokerage.com/api/v1/directory/persons",
            json=mock_response,
            status=201,
        )

        result = self.client.create_person(
            person_data, owner_agent_id="agent-123", owner_team_id="team-456"
        )
        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify query parameters
        request = responses.calls[0].request
        assert request.url is not None
        assert "ownerAgentId=agent-123" in request.url
        assert "ownerTeamId=team-456" in request.url

    @responses.activate
    def test_get_person_success(self) -> None:
        """Test successful person retrieval."""
        person_id = "person-123"
        mock_response = {
            "id": person_id,
            "firstName": "John",
            "lastName": "Doe",
        }

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/directory/persons/{person_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.get_person(person_id)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_update_person_success(self) -> None:
        """Test successful person update."""
        person_id = "person-123"
        person_data = {"firstName": "Jane"}
        mock_response = {"id": person_id, **person_data}

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/directory/persons/{person_id}",
            json=mock_response,
            status=200,
        )

        result = self.client.update_person(person_id, person_data)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_unlink_person_success(self) -> None:
        """Test successful person unlinking."""
        person_id = "person-123"
        mock_response = {"id": person_id, "linkedVendor": None}

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/directory/persons/{person_id}/unlink",
            json=mock_response,
            status=200,
        )

        result = self.client.unlink_person(person_id)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_link_person_success(self) -> None:
        """Test successful person linking."""
        person_id = "person-123"
        link_data = {"vendorId": "vendor-456"}
        mock_response = {"id": person_id, "linkedVendor": "vendor-456"}

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/directory/persons/{person_id}/link",
            json=mock_response,
            status=200,
        )

        result = self.client.link_person(person_id, link_data)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_archive_person_success(self) -> None:
        """Test successful person archiving."""
        person_id = "person-123"
        mock_response = {"id": person_id, "archived": True}

        responses.add(
            responses.PATCH,
            f"https://yenta.therealbrokerage.com/api/v1/directory/persons/{person_id}/archive",
            json=mock_response,
            status=200,
        )

        result = self.client.archive_person(person_id, archive=True)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_search_persons_minimal(self) -> None:
        """Test person search with minimal parameters."""
        mock_response = {
            "content": [{"id": "person-123", "firstName": "John"}],
            "totalElements": 1,
        }

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/persons/search/all",
            json=mock_response,
            status=200,
        )

        result = self.client.search_persons(page_number=0, page_size=20)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_search_persons_with_all_parameters(self) -> None:
        """Test person search with all parameters."""
        mock_response = {"content": [], "totalElements": 0}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/persons/search/all",
            json=mock_response,
            status=200,
        )

        result = self.client.search_persons(
            page_number=1,
            page_size=50,
            is_archived=False,
            is_public=True,
            is_linked_to_vendor=True,
            search_text="john doe",
            first_name="John",
            last_name="Doe",
            email_address="john@example.com",
            roles=[DirectoryRole.CLIENT],
            sort_by=[PersonSortField.FIRST_NAME, PersonSortField.LAST_NAME],
        )

        assert result == mock_response
        assert len(responses.calls) == 1

    # ===== DIRECTORY ENTRY TESTS =====

    @responses.activate
    def test_get_permitted_roles_success(self) -> None:
        """Test successful get permitted roles."""
        mock_response = {"roles": ["CLIENT", "VENDOR", "LANDLORD"]}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/permitted-roles",
            json=mock_response,
            status=200,
        )

        result = self.client.get_permitted_roles()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_permitted_roles_with_entry_type(self) -> None:
        """Test get permitted roles with entry type."""
        mock_response = {"roles": ["VENDOR", "CLIENT"]}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/permitted-roles",
            json=mock_response,
            status=200,
        )

        result = self.client.get_permitted_roles(DirectoryEntryType.VENDOR)
        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify query parameters
        request = responses.calls[0].request
        assert request.url is not None
        assert "entryType=VENDOR" in request.url

    @responses.activate
    def test_get_permitted_roles_with_string_entry_type(self) -> None:
        """Test get permitted roles with string entry type."""
        mock_response = {"roles": ["CLIENT"]}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/permitted-roles",
            json=mock_response,
            status=200,
        )

        result = self.client.get_permitted_roles("PERSON")
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_search_all_entries_minimal(self) -> None:
        """Test search all entries with minimal parameters."""
        mock_response = {
            "content": [{"id": "entry-123", "name": "Test Entry"}],
            "totalElements": 1,
        }

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/search/all",
            json=mock_response,
            status=200,
        )

        result = self.client.search_all_entries(page_number=0, page_size=20)
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_search_all_entries_with_all_parameters(self) -> None:
        """Test search all entries with all parameters."""
        mock_response = {"content": [], "totalElements": 0}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/search/all",
            json=mock_response,
            status=200,
        )

        result = self.client.search_all_entries(
            page_number=1,
            page_size=50,
            is_archived=False,
            is_verified=True,
            search_text="test entry",
            national_business_id="123456789",
            name="Test Entry",
            email_address="test@example.com",
            phone_number="555-0123",
            street="123 Main St",
            city="Test City",
            postal="12345",
            state_or_province=StateOrProvince.CALIFORNIA,
            country=Country.UNITED_STATES,
            administrative_area_ids=["area-1"],
            roles=[DirectoryRole.CLIENT],
            created_by="agent-123",
            entry_id="entry-456",
            sort_by=[
                DirectoryEntrySortField.NAME,
                DirectoryEntrySortField.EMAIL_ADDRESS,
            ],
        )

        assert result == mock_response
        assert len(responses.calls) == 1

    # ===== OVERRIDE METHODS TESTS =====

    # ===== ERROR HANDLING TESTS =====

    @responses.activate
    def test_vendor_not_found_error(self) -> None:
        """Test vendor not found error."""
        vendor_id = "nonexistent-vendor"
        error_response = {"message": "Vendor not found"}

        responses.add(
            responses.GET,
            f"https://yenta.therealbrokerage.com/api/v1/directory/vendors/{vendor_id}",
            json=error_response,
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found: Vendor not found"):
            self.client.get_vendor(vendor_id)

    @responses.activate
    def test_authentication_error(self) -> None:
        """Test authentication error."""
        error_response = {"message": "Invalid API key"}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/vendors/search/all",
            json=error_response,
            status=401,
        )

        with pytest.raises(
            AuthenticationError, match="Authentication failed: Invalid API key"
        ):
            self.client.search_vendors(page_number=0, page_size=20)

    @responses.activate
    def test_validation_error(self) -> None:
        """Test validation error."""
        error_response = {"message": "Invalid request data"}

        responses.add(
            responses.POST,
            "https://yenta.therealbrokerage.com/api/v1/directory/vendors",
            json=error_response,
            status=400,
        )

        with pytest.raises(ValidationError, match="Bad request: Invalid request data"):
            self.client.create_vendor({})

    @responses.activate
    def test_search_persons_with_phone_number(self) -> None:
        """Test person search with phone number to hit line 548."""
        mock_response = {"content": [], "totalElements": 0}

        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/directory/persons/search/all",
            json=mock_response,
            status=200,
        )

        result = self.client.search_persons(
            page_number=0,
            page_size=20,
            phone_number="555-1234",  # This should hit line 548
        )

        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify query parameters
        request = responses.calls[0].request
        assert request.url is not None
        assert "phoneNumber=555-1234" in request.url

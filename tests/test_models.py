"""Tests for ReZEN API data models and dataclasses."""

import pytest
from dataclasses import asdict, fields
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from rezen.models import (
    # Core data models
    Address,
    Agent,
    AgentParticipantInfo,
    AgentStatus,
    ApiKeyResponse,
    ApiResponse,
    ChecklistItem,
    ChecklistLabel,
    Commission,
    Country,
    DirectoryEntry,
    ErrorResponse,
    Money,
    PagedResponse,
    Person,
    StateOrProvince,
    Team,
    TeamAgent,
    TeamConfig,
    TeamInvitation,
    Transaction,
    Vendor,
    # Request/Response models
    EnableMfaRequest,
    GenerateApiKeyRequest,
    JwtAuthenticationResponse,
    LoginRequest,
    MfaVerificationRequest,
    PasswordUpdateRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    RevokeApiKeyRequest,
    UpdateEmailRequest,
    UpdateExistingPasswordRequest,
    # Additional models
    Availability,
    Buyer,
    ChecklistDocument,
    Division,
    DoubleEnderInfo,
    DocumentVersion,
    ExternalParticipantInfo,
    FeeSplit,
    HourRange,
    LeaderSplitConfig,
    MortgageInfo,
    MsdxVendor,
    OfficeSchedule,
    OneRealImpactFundConfig,
    Participant,
    ProfileScore,
    RealCapConfig,
    ReferralInfo,
    Seller,
    TitleInfo,
    # Enums
    ChecklistItemStatus,
    DayOfWeek,
    DealType,
    FeeType,
    InvitationStatus,
    ParticipantRole,
    PropertyType,
    RepresentationType,
    TeamStatus,
    TeamType,
)


class TestEnums:
    """Test enum classes."""

    def test_agent_status_enum(self):
        """Test AgentStatus enum values."""
        assert AgentStatus.CANDIDATE.value == "CANDIDATE"
        assert AgentStatus.ACTIVE.value == "ACTIVE"
        assert AgentStatus.INACTIVE.value == "INACTIVE"
        assert AgentStatus.REJECTED.value == "REJECTED"
        assert AgentStatus.RESURRECTING.value == "RESURRECTING"

    def test_team_status_enum(self):
        """Test TeamStatus enum values."""
        assert TeamStatus.ACTIVE.value == "ACTIVE"
        assert TeamStatus.INACTIVE.value == "INACTIVE"

    def test_team_type_enum(self):
        """Test TeamType enum values."""
        assert TeamType.NORMAL.value == "NORMAL"
        assert TeamType.PLATINUM.value == "PLATINUM"
        assert TeamType.GROUP.value == "GROUP"
        assert TeamType.DOMESTIC.value == "DOMESTIC"
        assert TeamType.PRO.value == "PRO"

    def test_country_enum(self):
        """Test Country enum values."""
        assert Country.UNITED_STATES.value == "UNITED_STATES"
        assert Country.CANADA.value == "CANADA"

    def test_state_or_province_enum(self):
        """Test StateOrProvince enum values."""
        assert StateOrProvince.CALIFORNIA.value == "CALIFORNIA"
        assert StateOrProvince.TEXAS.value == "TEXAS"
        assert StateOrProvince.ONTARIO.value == "ONTARIO"
        assert StateOrProvince.BRITISH_COLUMBIA.value == "BRITISH_COLUMBIA"

    def test_deal_type_enum(self):
        """Test DealType enum values."""
        assert DealType.SALE.value == "SALE"
        assert DealType.COMPENSATING.value == "COMPENSATING"
        assert DealType.NON_COMPENSATING.value == "NON_COMPENSATING"

    def test_property_type_enum(self):
        """Test PropertyType enum values."""
        assert PropertyType.RESIDENTIAL.value == "RESIDENTIAL"
        assert PropertyType.COMMERCIAL.value == "COMMERCIAL"
        assert PropertyType.LAND.value == "LAND"
        assert PropertyType.RENTAL.value == "RENTAL"

    def test_participant_role_enum(self):
        """Test ParticipantRole enum values."""
        assert ParticipantRole.REAL.value == "REAL"
        assert ParticipantRole.OTHER.value == "OTHER"

    def test_representation_type_enum(self):
        """Test RepresentationType enum values."""
        assert RepresentationType.BUYER.value == "BUYER"
        assert RepresentationType.SELLER.value == "SELLER"
        assert RepresentationType.DUAL.value == "DUAL"

    def test_invitation_status_enum(self):
        """Test InvitationStatus enum values."""
        assert InvitationStatus.EMAILED.value == "EMAILED"
        assert InvitationStatus.PENDING.value == "PENDING"
        assert InvitationStatus.ACCEPTED.value == "ACCEPTED"
        assert InvitationStatus.DECLINED.value == "DECLINED"
        assert InvitationStatus.EXPIRED.value == "EXPIRED"

    def test_checklist_item_status_enum(self):
        """Test ChecklistItemStatus enum values."""
        assert ChecklistItemStatus.BEFORE_UPDATE.value == "BEFORE_UPDATE"
        assert ChecklistItemStatus.PENDING.value == "PENDING"
        assert ChecklistItemStatus.COMPLETED.value == "COMPLETED"
        assert ChecklistItemStatus.SKIPPED.value == "SKIPPED"

    def test_fee_type_enum(self):
        """Test FeeType enum values."""
        assert FeeType.ADDITIONAL_COMMISSION.value == "ADDITIONAL_COMMISSION"
        assert FeeType.BROKERAGE_FEE.value == "BROKERAGE_FEE"
        assert FeeType.TRANSACTION_FEE.value == "TRANSACTION_FEE"
        assert FeeType.REFERRAL_FEE.value == "REFERRAL_FEE"

    def test_day_of_week_enum(self):
        """Test DayOfWeek enum values."""
        assert DayOfWeek.MONDAY.value == "MONDAY"
        assert DayOfWeek.TUESDAY.value == "TUESDAY"
        assert DayOfWeek.WEDNESDAY.value == "WEDNESDAY"
        assert DayOfWeek.THURSDAY.value == "THURSDAY"
        assert DayOfWeek.FRIDAY.value == "FRIDAY"
        assert DayOfWeek.SATURDAY.value == "SATURDAY"
        assert DayOfWeek.SUNDAY.value == "SUNDAY"


class TestCoreDataModels:
    """Test core data model classes."""

    def test_address_model(self):
        """Test Address dataclass."""
        address = Address(
            street="123 Main St",
            city="Springfield",
            state=StateOrProvince.CALIFORNIA,
            zip="12345",
            country=Country.UNITED_STATES,
            street2="Apt 2",
            unit="A",
            valid=True,
            one_line="123 Main St, Apt 2, Springfield, CA 12345",
        )

        assert address.street == "123 Main St"
        assert address.city == "Springfield"
        assert address.state == StateOrProvince.CALIFORNIA
        assert address.zip == "12345"
        assert address.country == Country.UNITED_STATES
        assert address.street2 == "Apt 2"
        assert address.unit == "A"
        assert address.valid is True
        assert address.one_line == "123 Main St, Apt 2, Springfield, CA 12345"

    def test_address_model_defaults(self):
        """Test Address dataclass with default values."""
        address = Address(
            street="123 Main St", city="Springfield", state="CA", zip="12345"
        )

        assert address.country == Country.UNITED_STATES
        assert address.street2 is None
        assert address.unit is None
        assert address.valid is None
        assert address.one_line is None

    def test_money_model(self):
        """Test Money dataclass."""
        money = Money(amount=Decimal("100.50"), currency="USD")

        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"

    def test_money_model_defaults(self):
        """Test Money dataclass with default currency."""
        money = Money(amount=Decimal("100.50"))

        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"

    def test_commission_model(self):
        """Test Commission dataclass."""
        money = Money(amount=Decimal("5000.00"), currency="USD")
        commission = Commission(
            commission_amount=money,
            commission_percent=3.0,
            percent_enabled=True,
            negative_or_empty=False,
        )

        assert commission.commission_amount == money
        assert commission.commission_percent == 3.0
        assert commission.percent_enabled is True
        assert commission.negative_or_empty is False

    def test_commission_model_defaults(self):
        """Test Commission dataclass with defaults."""
        money = Money(amount=Decimal("5000.00"))
        commission = Commission(commission_amount=money)

        assert commission.commission_amount == money
        assert commission.commission_percent is None
        assert commission.percent_enabled is True
        assert commission.negative_or_empty is False

    def test_division_model(self):
        """Test Division dataclass."""
        division_id = uuid4()
        division = Division(
            id=division_id,
            name="Real Estate Division",
            logo_url="https://example.com/logo.png",
        )

        assert division.id == division_id
        assert division.name == "Real Estate Division"
        assert division.logo_url == "https://example.com/logo.png"

    def test_division_model_defaults(self):
        """Test Division dataclass with defaults."""
        division_id = uuid4()
        division = Division(id=division_id, name="Real Estate Division")

        assert division.id == division_id
        assert division.name == "Real Estate Division"
        assert division.logo_url is None

    def test_hour_range_model(self):
        """Test HourRange dataclass."""
        hour_range = HourRange(start_time="09:00", end_time="17:00")

        assert hour_range.start_time == "09:00"
        assert hour_range.end_time == "17:00"

    def test_office_schedule_model(self):
        """Test OfficeSchedule dataclass."""
        hour_range = HourRange(start_time="09:00", end_time="17:00")
        schedule = OfficeSchedule(day_of_week=DayOfWeek.MONDAY, hour_range=hour_range)

        assert schedule.day_of_week == DayOfWeek.MONDAY
        assert schedule.hour_range == hour_range

    def test_availability_model(self):
        """Test Availability dataclass."""
        availability = Availability(
            do_not_disturb=True, time_zone="US/Pacific", available=False
        )

        assert availability.office_schedule == []
        assert availability.out_of_office == []
        assert availability.do_not_disturb is True
        assert availability.time_zone == "US/Pacific"
        assert availability.available is False

    def test_availability_model_defaults(self):
        """Test Availability dataclass with defaults."""
        availability = Availability()

        assert availability.office_schedule == []
        assert availability.out_of_office == []
        assert availability.do_not_disturb is False
        assert availability.time_zone == "US/Eastern"
        assert availability.available is True

    def test_msdx_vendor_model(self):
        """Test MsdxVendor dataclass."""
        vendor = MsdxVendor(
            subsidiary="REAL_BROKER_LLC",
            no="12345",
            error="Connection timeout",
            synced_at=1640995200,
        )

        assert vendor.subsidiary == "REAL_BROKER_LLC"
        assert vendor.no == "12345"
        assert vendor.error == "Connection timeout"
        assert vendor.synced_at == 1640995200

    def test_msdx_vendor_model_defaults(self):
        """Test MsdxVendor dataclass with defaults."""
        vendor = MsdxVendor(subsidiary="REAL_BROKER_LLC", no="12345")

        assert vendor.subsidiary == "REAL_BROKER_LLC"
        assert vendor.no == "12345"
        assert vendor.error is None
        assert vendor.synced_at is None


class TestAgentModels:
    """Test agent-related data models."""

    def test_agent_model(self):
        """Test Agent dataclass."""
        agent_id = uuid4()
        agent = Agent(
            id=agent_id,
            first_name="John",
            last_name="Doe",
            email_address="john.doe@example.com",
            agent_status=AgentStatus.ACTIVE,
            agent_account_country=Country.UNITED_STATES,
            created_at=1640995200,
            phone_number="555-123-4567",
        )

        assert agent.id == agent_id
        assert agent.first_name == "John"
        assert agent.last_name == "Doe"
        assert agent.email_address == "john.doe@example.com"
        assert agent.agent_status == AgentStatus.ACTIVE
        assert agent.agent_account_country == Country.UNITED_STATES
        assert agent.created_at == 1640995200
        assert agent.phone_number == "555-123-4567"
        assert agent.type == "AGENT"  # default value
        assert agent.divisions == []  # default empty list

    def test_agent_participant_info_model(self):
        """Test AgentParticipantInfo dataclass."""
        yenta_id = uuid4()
        participant = AgentParticipantInfo(
            agent_id="agent123",
            role=ParticipantRole.REAL,
            receives_invoice=True,
            id="participant123",
            created_at=1640995200,
            op_city_referral=True,
            opted_in_for_ecp=True,
            yenta_id=yenta_id,
        )

        assert participant.agent_id == "agent123"
        assert participant.role == ParticipantRole.REAL
        assert participant.receives_invoice is True
        assert participant.id == "participant123"
        assert participant.created_at == 1640995200
        assert participant.op_city_referral is True
        assert participant.opted_in_for_ecp is True
        assert participant.yenta_id == yenta_id
        assert participant.one_real_impact_fund_config is None  # default

    def test_one_real_impact_fund_config_model(self):
        """Test OneRealImpactFundConfig dataclass."""
        config = OneRealImpactFundConfig(
            amount=100.0, percent=5.0, percent_enabled=True
        )

        assert config.amount == 100.0
        assert config.percent == 5.0
        assert config.percent_enabled is True

    def test_profile_score_model(self):
        """Test ProfileScore dataclass."""
        score = ProfileScore(score=85, max_score=100, completion_percentage=85.0)

        assert score.score == 85
        assert score.max_score == 100
        assert score.completion_percentage == 85.0


class TestTeamModels:
    """Test team-related data models."""

    def test_leader_split_config_model(self):
        """Test LeaderSplitConfig dataclass."""
        config = LeaderSplitConfig(enforce_splits=True, min_split_percent=10.0)

        assert config.enforce_splits is True
        assert config.min_split_percent == 10.0

    def test_real_cap_config_model(self):
        """Test RealCapConfig dataclass."""
        config = RealCapConfig(
            leader_cap=50000.0, excluded_member_caps=[25000.0, 30000.0]
        )

        assert config.leader_cap == 50000.0
        assert config.excluded_member_caps == [25000.0, 30000.0]

    def test_real_cap_config_model_defaults(self):
        """Test RealCapConfig dataclass with defaults."""
        config = RealCapConfig(leader_cap=50000.0)

        assert config.leader_cap == 50000.0
        assert config.excluded_member_caps == []

    def test_team_config_model(self):
        """Test TeamConfig dataclass."""
        config_id = uuid4()
        commission_plan_id = uuid4()
        leader_split_config = LeaderSplitConfig(
            enforce_splits=True, min_split_percent=10.0
        )
        real_cap_config = RealCapConfig(leader_cap=50000.0)

        config = TeamConfig(
            id=config_id,
            commission_plan_id=commission_plan_id,
            country=Country.UNITED_STATES,
            team_type=TeamType.NORMAL,
            name="Test Team",
            min_teammates=2,
            max_teammates=10,
            min_leaders=1,
            max_leaders=2,
            payment_details_visibility="TEAM_LEADER",
            paid_at_closing=True,
            leader_split_config=leader_split_config,
            real_cap_config=real_cap_config,
            cda_approver="TEAM_LEADER",
            leader_overridable_properties=["LEADER_SPLIT_ENFORCEMENT"],
            allowed_member_caps_for_permanent_plan=[16000.0],
            allowed_member_caps_for_temporary_plan=[12000.0],
            status=TeamStatus.ACTIVE,
            permitted_transaction_editors="TEAM_LEADER",
            allowed_member_caps_for_new_member=[12000.0],
            minimum_allowed_member_for_new_member=10000.0,
        )

        assert config.id == config_id
        assert config.commission_plan_id == commission_plan_id
        assert config.country == Country.UNITED_STATES
        assert config.team_type == TeamType.NORMAL
        assert config.name == "Test Team"
        assert config.min_teammates == 2
        assert config.max_teammates == 10
        assert config.min_leaders == 1
        assert config.max_leaders == 2
        assert config.payment_details_visibility == "TEAM_LEADER"
        assert config.paid_at_closing is True
        assert config.leader_split_config == leader_split_config
        assert config.real_cap_config == real_cap_config
        assert config.status == TeamStatus.ACTIVE

    def test_fee_split_model(self):
        """Test FeeSplit dataclass."""
        fee_split = FeeSplit(fee_type=FeeType.BROKERAGE_FEE, percent=50.0)

        assert fee_split.fee_type == FeeType.BROKERAGE_FEE
        assert fee_split.percent == 50.0

    def test_team_invitation_model(self):
        """Test TeamInvitation dataclass."""
        invitation_id = uuid4()
        team_id = uuid4()
        agent_id = uuid4()

        invitation = TeamInvitation(
            invitation_id=invitation_id,
            team_id=team_id,
            first_name="Jane",
            last_name="Smith",
            email_address="jane.smith@example.com",
            cap_level=16000.0,
            invitation_created_by_agent_id=agent_id,
            status=InvitationStatus.EMAILED,
            waive_fees=True,
        )

        assert invitation.invitation_id == invitation_id
        assert invitation.team_id == team_id
        assert invitation.first_name == "Jane"
        assert invitation.last_name == "Smith"
        assert invitation.email_address == "jane.smith@example.com"
        assert invitation.cap_level == 16000.0
        assert invitation.invitation_created_by_agent_id == agent_id
        assert invitation.status == InvitationStatus.EMAILED
        assert invitation.waive_fees is True
        assert invitation.pending is True  # default


class TestTransactionModels:
    """Test transaction-related data models."""

    def test_participant_model(self):
        """Test Participant dataclass."""
        vendor_id = uuid4()
        participant = Participant(
            id="participant123",
            created_at=1640995200,
            role=ParticipantRole.REAL,
            first_name="John",
            last_name="Doe",
            company_name="Real Estate Co",
            phone_number="555-123-4567",
            email="john.doe@example.com",
            address="123 Main St",
            vendor_directory_id=vendor_id,
        )

        assert participant.id == "participant123"
        assert participant.created_at == 1640995200
        assert participant.role == ParticipantRole.REAL
        assert participant.first_name == "John"
        assert participant.last_name == "Doe"
        assert participant.company_name == "Real Estate Co"
        assert participant.phone_number == "555-123-4567"
        assert participant.email == "john.doe@example.com"
        assert participant.address == "123 Main St"
        assert participant.vendor_directory_id == vendor_id

    def test_buyer_model(self):
        """Test Buyer dataclass (inherits from Participant)."""
        buyer = Buyer(
            id="buyer123",
            created_at=1640995200,
            role=ParticipantRole.REAL,
            first_name="Jane",
            last_name="Buyer",
        )

        assert buyer.id == "buyer123"
        assert buyer.created_at == 1640995200
        assert buyer.role == ParticipantRole.REAL
        assert buyer.first_name == "Jane"
        assert buyer.last_name == "Buyer"

    def test_seller_model(self):
        """Test Seller dataclass (inherits from Participant)."""
        seller = Seller(
            id="seller123",
            created_at=1640995200,
            role=ParticipantRole.REAL,
            first_name="Bob",
            last_name="Seller",
        )

        assert seller.id == "seller123"
        assert seller.created_at == 1640995200
        assert seller.role == ParticipantRole.REAL
        assert seller.first_name == "Bob"
        assert seller.last_name == "Seller"

    def test_external_participant_info_model(self):
        """Test ExternalParticipantInfo dataclass."""
        vendor_id = uuid4()
        participant = ExternalParticipantInfo(
            id="external123",
            created_at=1640995200,
            role=ParticipantRole.OTHER,
            first_name="External",
            last_name="Agent",
            assistant_email_address="assistant@example.com",
            w9_path="/documents/w9.pdf",
            receives_invoice=True,
            ein="12-3456789",
            vendor_directory_id=vendor_id,
        )

        assert participant.id == "external123"
        assert participant.created_at == 1640995200
        assert participant.role == ParticipantRole.OTHER
        assert participant.first_name == "External"
        assert participant.last_name == "Agent"
        assert participant.assistant_email_address == "assistant@example.com"
        assert participant.w9_path == "/documents/w9.pdf"
        assert participant.receives_invoice is True
        assert participant.ein == "12-3456789"
        assert participant.vendor_directory_id == vendor_id


class TestAuthenticationModels:
    """Test authentication and MFA data models."""

    def test_login_request_model(self):
        """Test LoginRequest dataclass."""
        request = LoginRequest(email="user@example.com", password="securepassword123")

        assert request.email == "user@example.com"
        assert request.password == "securepassword123"

    def test_jwt_authentication_response_model(self):
        """Test JwtAuthenticationResponse dataclass."""
        response = JwtAuthenticationResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="Bearer",
            expires_in=3600,
            refresh_token="refresh123",
        )

        assert response.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert response.token_type == "Bearer"
        assert response.expires_in == 3600
        assert response.refresh_token == "refresh123"

    def test_jwt_authentication_response_defaults(self):
        """Test JwtAuthenticationResponse dataclass with defaults."""
        response = JwtAuthenticationResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="Bearer",
            expires_in=3600,
        )

        assert response.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert response.token_type == "Bearer"
        assert response.expires_in == 3600
        assert response.refresh_token is None

    def test_mfa_verification_request_model(self):
        """Test MfaVerificationRequest dataclass."""
        request = MfaVerificationRequest(
            email="user@example.com",
            mfa_code="123456",
            temporary_token="temp_token_123",
        )

        assert request.email == "user@example.com"
        assert request.mfa_code == "123456"
        assert request.temporary_token == "temp_token_123"

    def test_enable_mfa_request_model(self):
        """Test EnableMfaRequest dataclass."""
        request = EnableMfaRequest(mfa_code="123456")

        assert request.mfa_code == "123456"

    def test_update_email_request_model(self):
        """Test UpdateEmailRequest dataclass."""
        request = UpdateEmailRequest(email="newemail@example.com")

        assert request.email == "newemail@example.com"

    def test_reset_password_request_model(self):
        """Test ResetPasswordRequest dataclass."""
        request = ResetPasswordRequest(email="user@example.com")

        assert request.email == "user@example.com"

    def test_reset_password_response_model(self):
        """Test ResetPasswordResponse dataclass."""
        response = ResetPasswordResponse(
            message="Password reset email sent", success=True
        )

        assert response.message == "Password reset email sent"
        assert response.success is True

    def test_update_existing_password_request_model(self):
        """Test UpdateExistingPasswordRequest dataclass."""
        request = UpdateExistingPasswordRequest(
            current_password="oldpassword", new_password="newpassword123"
        )

        assert request.current_password == "oldpassword"
        assert request.new_password == "newpassword123"

    def test_password_update_request_model(self):
        """Test PasswordUpdateRequest dataclass."""
        request = PasswordUpdateRequest(
            new_password="newpassword123", token="reset_token_456"
        )

        assert request.new_password == "newpassword123"
        assert request.token == "reset_token_456"


class TestApiKeyModels:
    """Test API key data models."""

    def test_api_key_response_model(self):
        """Test ApiKeyResponse dataclass."""
        key_id = uuid4()
        created_at = datetime(2022, 1, 1, 12, 0, 0)
        last_used_at = datetime(2022, 1, 15, 10, 30, 0)
        expires_at = datetime(2023, 1, 1, 12, 0, 0)

        response = ApiKeyResponse(
            id=key_id,
            name="My API Key",
            key_prefix="sk_test_",
            created_at=created_at,
            last_used_at=last_used_at,
            expires_at=expires_at,
        )

        assert response.id == key_id
        assert response.name == "My API Key"
        assert response.key_prefix == "sk_test_"
        assert response.created_at == created_at
        assert response.last_used_at == last_used_at
        assert response.expires_at == expires_at

    def test_api_key_response_defaults(self):
        """Test ApiKeyResponse dataclass with defaults."""
        key_id = uuid4()
        created_at = datetime(2022, 1, 1, 12, 0, 0)

        response = ApiKeyResponse(
            id=key_id, name="My API Key", key_prefix="sk_test_", created_at=created_at
        )

        assert response.id == key_id
        assert response.name == "My API Key"
        assert response.key_prefix == "sk_test_"
        assert response.created_at == created_at
        assert response.last_used_at is None
        assert response.expires_at is None

    def test_generate_api_key_request_model(self):
        """Test GenerateApiKeyRequest dataclass."""
        expires_at = datetime(2023, 1, 1, 12, 0, 0)

        request = GenerateApiKeyRequest(name="New API Key", expires_at=expires_at)

        assert request.name == "New API Key"
        assert request.expires_at == expires_at

    def test_generate_api_key_request_defaults(self):
        """Test GenerateApiKeyRequest dataclass with defaults."""
        request = GenerateApiKeyRequest(name="New API Key")

        assert request.name == "New API Key"
        assert request.expires_at is None

    def test_revoke_api_key_request_model(self):
        """Test RevokeApiKeyRequest dataclass."""
        key_id = uuid4()
        request = RevokeApiKeyRequest(key_id=key_id)

        assert request.key_id == key_id


class TestDirectoryModels:
    """Test directory data models."""

    def test_directory_entry_model(self):
        """Test DirectoryEntry dataclass."""
        entry_id = uuid4()
        created_at = datetime(2022, 1, 1, 12, 0, 0)
        updated_at = datetime(2022, 1, 15, 10, 30, 0)

        entry = DirectoryEntry(
            id=entry_id,
            name="John Doe",
            email="john.doe@example.com",
            phone="555-123-4567",
            company="Real Estate Co",
            role="Agent",
            type="Person",
            created_at=created_at,
            updated_at=updated_at,
        )

        assert entry.id == entry_id
        assert entry.name == "John Doe"
        assert entry.email == "john.doe@example.com"
        assert entry.phone == "555-123-4567"
        assert entry.company == "Real Estate Co"
        assert entry.role == "Agent"
        assert entry.type == "Person"
        assert entry.created_at == created_at
        assert entry.updated_at == updated_at

    def test_person_model(self):
        """Test Person dataclass (inherits from DirectoryEntry)."""
        person_id = uuid4()
        created_at = datetime(2022, 1, 1, 12, 0, 0)
        updated_at = datetime(2022, 1, 15, 10, 30, 0)

        person = Person(
            id=person_id,
            name="John Doe",
            email="john.doe@example.com",
            phone="555-123-4567",
            company="Real Estate Co",
            role="Agent",
            type="Person",
            created_at=created_at,
            updated_at=updated_at,
            first_name="John",
            last_name="Doe",
        )

        assert person.id == person_id
        assert person.name == "John Doe"
        assert person.first_name == "John"
        assert person.last_name == "Doe"

    def test_vendor_model(self):
        """Test Vendor dataclass (inherits from DirectoryEntry)."""
        vendor_id = uuid4()
        created_at = datetime(2022, 1, 1, 12, 0, 0)
        updated_at = datetime(2022, 1, 15, 10, 30, 0)

        vendor = Vendor(
            id=vendor_id,
            name="Title Company",
            email="contact@titleco.com",
            phone="555-987-6543",
            company="Title Company Inc",
            role="Title Company",
            type="Vendor",
            created_at=created_at,
            updated_at=updated_at,
            business_name="Title Company Inc",
            services=["Title Search", "Escrow"],
        )

        assert vendor.id == vendor_id
        assert vendor.name == "Title Company"
        assert vendor.business_name == "Title Company Inc"
        assert vendor.services == ["Title Search", "Escrow"]

    def test_vendor_model_defaults(self):
        """Test Vendor dataclass with defaults."""
        vendor_id = uuid4()
        created_at = datetime(2022, 1, 1, 12, 0, 0)
        updated_at = datetime(2022, 1, 15, 10, 30, 0)

        vendor = Vendor(
            id=vendor_id,
            name="Title Company",
            email="contact@titleco.com",
            phone="555-987-6543",
            company="Title Company Inc",
            role="Title Company",
            type="Vendor",
            created_at=created_at,
            updated_at=updated_at,
            business_name="Title Company Inc",
        )

        assert vendor.id == vendor_id
        assert vendor.name == "Title Company"
        assert vendor.business_name == "Title Company Inc"
        assert vendor.services == []


class TestResponseModels:
    """Test response wrapper data models."""

    def test_paged_response_model(self):
        """Test PagedResponse dataclass."""
        results = ["item1", "item2", "item3"]

        response = PagedResponse(
            page_number=1, page_size=10, has_next=True, total_count=50, results=results
        )

        assert response.page_number == 1
        assert response.page_size == 10
        assert response.has_next is True
        assert response.total_count == 50
        assert response.results == results

    def test_paged_response_defaults(self):
        """Test PagedResponse dataclass with defaults."""
        response = PagedResponse(
            page_number=1, page_size=10, has_next=False, total_count=5
        )

        assert response.page_number == 1
        assert response.page_size == 10
        assert response.has_next is False
        assert response.total_count == 5
        assert response.results == []

    def test_api_response_model(self):
        """Test ApiResponse dataclass."""
        data = {"key": "value"}

        response = ApiResponse(status=True, message="Operation successful", data=data)

        assert response.status is True
        assert response.message == "Operation successful"
        assert response.data == data

    def test_api_response_defaults(self):
        """Test ApiResponse dataclass with defaults."""
        response = ApiResponse(status=True, message="Operation successful")

        assert response.status is True
        assert response.message == "Operation successful"
        assert response.data is None

    def test_error_response_model(self):
        """Test ErrorResponse dataclass."""
        timestamp = datetime(2022, 1, 1, 12, 0, 0)

        response = ErrorResponse(
            error="ValidationError",
            message="Invalid input data",
            status_code=400,
            timestamp=timestamp,
        )

        assert response.error == "ValidationError"
        assert response.message == "Invalid input data"
        assert response.status_code == 400
        assert response.timestamp == timestamp


class TestDataclassUtilities:
    """Test dataclass utility functions and integration."""

    def test_dataclass_serialization(self):
        """Test that dataclasses can be serialized to dictionaries."""
        address = Address(
            street="123 Main St",
            city="Springfield",
            state=StateOrProvince.CALIFORNIA,
            zip="12345",
        )

        # Convert to dict
        address_dict = asdict(address)

        assert isinstance(address_dict, dict)
        assert address_dict["street"] == "123 Main St"
        assert address_dict["city"] == "Springfield"
        assert address_dict["state"] == StateOrProvince.CALIFORNIA
        assert address_dict["zip"] == "12345"
        assert address_dict["country"] == Country.UNITED_STATES

    def test_dataclass_fields(self):
        """Test that dataclass fields are properly defined."""
        address_fields = fields(Address)
        field_names = [f.name for f in address_fields]

        expected_fields = [
            "street",
            "city",
            "state",
            "zip",
            "country",
            "street2",
            "unit",
            "valid",
            "one_line",
        ]

        for field_name in expected_fields:
            assert field_name in field_names

    def test_nested_dataclass_models(self):
        """Test that nested dataclass models work correctly."""
        money = Money(amount=Decimal("5000.00"), currency="USD")
        commission = Commission(commission_amount=money, commission_percent=3.0)

        # Test that nested objects are properly accessible
        assert commission.commission_amount.amount == Decimal("5000.00")
        assert commission.commission_amount.currency == "USD"
        assert commission.commission_percent == 3.0

    def test_enum_field_types(self):
        """Test that enum fields work correctly in dataclasses."""
        address = Address(
            street="123 Main St",
            city="Springfield",
            state=StateOrProvince.CALIFORNIA,
            zip="12345",
            country=Country.UNITED_STATES,
        )

        # Test enum comparisons
        assert address.state == StateOrProvince.CALIFORNIA
        assert address.state.value == "CALIFORNIA"
        assert address.country == Country.UNITED_STATES
        assert address.country.value == "UNITED_STATES"

    def test_optional_fields(self):
        """Test that optional fields work correctly."""
        # Create agent with minimal required fields
        agent_id = uuid4()
        agent = Agent(
            id=agent_id,
            first_name="John",
            last_name="Doe",
            email_address="john.doe@example.com",
            agent_status=AgentStatus.ACTIVE,
            agent_account_country=Country.UNITED_STATES,
        )

        # Test that optional fields have correct default values
        assert agent.created_at is None
        assert agent.updated_at is None
        assert agent.type == "AGENT"
        assert agent.middle_name is None
        assert agent.divisions == []
        assert agent.administrative_area_ids == []
        assert agent.opted_into_sms is False

    def test_list_fields_with_defaults(self):
        """Test that list fields with default_factory work correctly."""
        availability = Availability()

        # Test that list fields are properly initialized
        assert isinstance(availability.office_schedule, list)
        assert isinstance(availability.out_of_office, list)
        assert availability.office_schedule == []
        assert availability.out_of_office == []

        # Test that we can append to these lists
        hour_range = HourRange(start_time="09:00", end_time="17:00")
        schedule = OfficeSchedule(day_of_week=DayOfWeek.MONDAY, hour_range=hour_range)
        availability.office_schedule.append(schedule)

        assert len(availability.office_schedule) == 1
        assert availability.office_schedule[0] == schedule


if __name__ == "__main__":
    pytest.main([__file__])

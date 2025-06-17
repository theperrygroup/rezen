"""ReZEN API Python Client."""

from .agents import AgentsClient, AgentSortField, AgentStatus
from .api_keys import ApiKeysClient
from .auth import AuthClient
from .checklist import ChecklistClient
from .client import RezenClient
from .directory import (
    DirectoryClient,
    DirectoryEntrySortField,
    DirectoryEntryType,
    DirectoryRole,
    PersonSortField,
    VendorSortField,
)
from .documents import DocumentClient
from .dropbox import DropboxClient
from .enums import Country, SortDirection, StateOrProvince
from .exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    RezenError,
    ServerError,
    ValidationError,
)
from .mfa import MfaClient
from .models import (
    # Core data models
    Address,
    Agent,
    AgentParticipantInfo,
    AgentStatus as ModelAgentStatus,
    ApiKeyResponse,
    ApiResponse,
    ChecklistItem,
    ChecklistLabel,
    Commission,
    Country as ModelCountry,
    DirectoryEntry,
    ErrorResponse,
    Money,
    PagedResponse,
    Person,
    StateOrProvince as ModelStateOrProvince,
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
    # Enums
    ChecklistItemStatus,
    DayOfWeek,
    DealType,
    FeeType,
    InvitationStatus,
    ParticipantRole,
    PropertyType,
    RepresentationType,
    TeamStatus as ModelTeamStatus,
    TeamType as ModelTeamType,
)
from .teams import TeamsClient, TeamSortField, TeamStatus, TeamType
from .transaction_builder import TransactionBuilderClient
from .transactions import TransactionsClient
from .users import UsersClient

__version__ = "2.2.5"
__all__ = [
    # Client classes
    "RezenClient",
    "AuthClient",
    "MfaClient",
    "ApiKeysClient",
    "ChecklistClient",
    "TransactionBuilderClient",
    "TransactionsClient",
    "TeamsClient",
    "DirectoryClient",
    "AgentsClient",
    "UsersClient",
    "DocumentClient",
    "DropboxClient",
    # Enums from legacy modules
    "SortDirection",
    "TeamSortField",
    "TeamStatus",
    "TeamType",
    "AgentStatus",
    "AgentSortField",
    "DirectoryEntryType",
    "DirectoryRole",
    "DirectoryEntrySortField",
    "PersonSortField",
    "VendorSortField",
    "Country",
    "StateOrProvince",
    # Data models
    "Address",
    "Agent",
    "AgentParticipantInfo",
    "ModelAgentStatus",
    "ApiKeyResponse",
    "ApiResponse",
    "ChecklistItem",
    "ChecklistLabel",
    "Commission",
    "ModelCountry",
    "DirectoryEntry",
    "ErrorResponse",
    "Money",
    "PagedResponse",
    "Person",
    "ModelStateOrProvince",
    "Team",
    "TeamAgent",
    "TeamConfig",
    "TeamInvitation",
    "Transaction",
    "Vendor",
    # Request/Response models
    "EnableMfaRequest",
    "GenerateApiKeyRequest",
    "JwtAuthenticationResponse",
    "LoginRequest",
    "MfaVerificationRequest",
    "PasswordUpdateRequest",
    "ResetPasswordRequest",
    "ResetPasswordResponse",
    "RevokeApiKeyRequest",
    "UpdateEmailRequest",
    "UpdateExistingPasswordRequest",
    # Model enums
    "ChecklistItemStatus",
    "DayOfWeek",
    "DealType",
    "FeeType",
    "InvitationStatus",
    "ParticipantRole",
    "PropertyType",
    "RepresentationType",
    "ModelTeamStatus",
    "ModelTeamType",
    # Exception classes
    "RezenError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
]

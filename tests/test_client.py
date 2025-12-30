"""Tests for the main ReZEN client."""

from unittest.mock import patch

from rezen.agents import AgentsClient
from rezen.client import RezenClient
from rezen.directory import DirectoryClient
from rezen.documents import DocumentClient
from rezen.dropbox import DropboxClient
from rezen.rev_share import RevShareClient
from rezen.teams import TeamsClient
from rezen.transaction_builder import TransactionBuilderClient
from rezen.transactions import TransactionsClient


class TestRezenClient:
    """Test the main RezenClient class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        client = RezenClient()
        assert client._api_key is None
        assert client._base_url is None
        assert client._timeout_seconds is None
        assert client._max_retries is None
        assert client._retry_backoff_seconds is None
        assert client._transaction_builder is None
        assert client._transactions is None
        assert client._teams is None
        assert client._agents is None
        assert client._directory is None
        assert client._documents is None
        assert client._dropbox is None
        assert client._rev_share is None

    def test_init_with_parameters(self) -> None:
        """Test initialization with API key and base URL."""
        client = RezenClient(api_key="test_key", base_url="https://test.example.com")
        assert client._api_key == "test_key"
        assert client._base_url == "https://test.example.com"
        assert client._timeout_seconds is None
        assert client._max_retries is None
        assert client._retry_backoff_seconds is None
        assert client._transaction_builder is None
        assert client._transactions is None
        assert client._teams is None
        assert client._agents is None
        assert client._directory is None
        assert client._documents is None
        assert client._dropbox is None
        assert client._rev_share is None

    def test_transaction_builder_property_lazy_loading(self) -> None:
        """Test that transaction_builder property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._transaction_builder is None

        # First access creates the client
        tb_client = client.transaction_builder
        assert isinstance(tb_client, TransactionBuilderClient)

        # Second access returns the same instance
        tb_client2 = client.transaction_builder
        assert tb_client2 is tb_client

    def test_transaction_builder_property_passes_parameters(self) -> None:
        """Test that transaction_builder property passes API key and base URL."""
        api_key = "test_key"
        base_url = "https://test.example.com"

        client = RezenClient(api_key=api_key, base_url=base_url)
        tb_client = client.transaction_builder

        assert tb_client.api_key == api_key
        assert tb_client.base_url == base_url

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_test_key"})
    def test_transaction_builder_with_env_api_key(self) -> None:
        """Test transaction_builder with API key from environment."""
        client = RezenClient()
        tb_client = client.transaction_builder

        assert tb_client.api_key == "env_test_key"

    def test_transactions_property_lazy_loading(self) -> None:
        """Test that transactions property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._transactions is None

        # First access creates the client
        transactions_client = client.transactions
        assert isinstance(transactions_client, TransactionsClient)

        # Second access returns the same instance
        transactions_client2 = client.transactions
        assert transactions_client2 is transactions_client

    def test_transactions_property_passes_parameters(self) -> None:
        """Test that transactions property passes API key and base URL."""
        api_key = "test_key"
        base_url = "https://test.example.com"

        client = RezenClient(api_key=api_key, base_url=base_url)
        transactions_client = client.transactions

        assert transactions_client.api_key == api_key
        assert transactions_client.base_url == base_url

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_test_key"})
    def test_transactions_with_env_api_key(self) -> None:
        """Test transactions with API key from environment."""
        client = RezenClient()
        transactions_client = client.transactions

        assert transactions_client.api_key == "env_test_key"

    def test_load_dotenv_opt_in(self) -> None:
        """Test that dotenv loading is opt-in."""
        with patch("dotenv.load_dotenv") as load:
            RezenClient(load_dotenv=True)
            load.assert_called_once()

    def test_timeout_and_retry_settings_propagate_to_subclients(self) -> None:
        """Test that configured timeouts/retries propagate to created sub-clients."""
        client = RezenClient(
            api_key="test_key",
            timeout_seconds=12.0,
            max_retries=1,
            retry_backoff_seconds=0.1,
        )

        assert client.transaction_builder.timeout_seconds == 12.0
        assert client.transaction_builder.max_retries == 1
        assert client.transaction_builder.retry_backoff_seconds == 0.1

        assert client.transactions.timeout_seconds == 12.0
        assert client.transactions.max_retries == 1
        assert client.transactions.retry_backoff_seconds == 0.1

        assert client.rev_share.timeout_seconds == 12.0
        assert client.rev_share.max_retries == 1
        assert client.rev_share.retry_backoff_seconds == 0.1

        # Different base URLs still receive the same transport configuration.
        assert client.agents.timeout_seconds == 12.0
        assert client.teams.timeout_seconds == 12.0
        assert client.directory.timeout_seconds == 12.0
        assert client.users.timeout_seconds == 12.0

    def test_teams_property_lazy_loading(self) -> None:
        """Test that teams property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._teams is None

        # First access creates the client
        teams_client = client.teams
        assert isinstance(teams_client, TeamsClient)

        # Second access returns the same instance
        teams_client2 = client.teams
        assert teams_client2 is teams_client

    def test_teams_property_passes_api_key(self) -> None:
        """Test that teams property passes API key (but not base URL due to different API)."""
        api_key = "test_key"

        client = RezenClient(api_key=api_key, base_url="https://test.example.com")
        teams_client = client.teams

        assert teams_client.api_key == api_key
        # Teams uses different base URL, so it should not inherit the main base URL
        assert teams_client.base_url == "https://yenta.therealbrokerage.com/api/v1"

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_test_key"})
    def test_teams_with_env_api_key(self) -> None:
        """Test teams with API key from environment."""
        client = RezenClient()
        teams_client = client.teams

        assert teams_client.api_key == "env_test_key"

    def test_all_clients_independent(self) -> None:
        """Test that all client properties work independently."""
        client = RezenClient(api_key="test_key")

        # Access all properties
        tb_client = client.transaction_builder
        transactions_client = client.transactions
        teams_client = client.teams
        agents_client = client.agents
        directory_client = client.directory
        documents_client = client.documents
        dropbox_client = client.dropbox
        rev_share_client = client.rev_share

        # Verify they are different instances
        assert tb_client is not transactions_client  # type: ignore[comparison-overlap]
        assert tb_client is not teams_client  # type: ignore[comparison-overlap]
        assert tb_client is not agents_client  # type: ignore[comparison-overlap]
        assert tb_client is not directory_client  # type: ignore[comparison-overlap]
        assert tb_client is not documents_client  # type: ignore[comparison-overlap]
        assert tb_client is not dropbox_client  # type: ignore[comparison-overlap]
        assert tb_client is not rev_share_client  # type: ignore[comparison-overlap]
        assert transactions_client is not teams_client  # type: ignore[comparison-overlap]
        assert transactions_client is not agents_client  # type: ignore[comparison-overlap]
        assert transactions_client is not directory_client  # type: ignore[comparison-overlap]
        assert transactions_client is not documents_client  # type: ignore[comparison-overlap]
        assert transactions_client is not dropbox_client  # type: ignore[comparison-overlap]
        assert transactions_client is not rev_share_client  # type: ignore[comparison-overlap]
        assert teams_client is not agents_client  # type: ignore[comparison-overlap]
        assert teams_client is not directory_client  # type: ignore[comparison-overlap]
        assert teams_client is not documents_client  # type: ignore[comparison-overlap]
        assert teams_client is not dropbox_client  # type: ignore[comparison-overlap]
        assert teams_client is not rev_share_client  # type: ignore[comparison-overlap]
        assert agents_client is not directory_client  # type: ignore[comparison-overlap]
        assert agents_client is not documents_client  # type: ignore[comparison-overlap]
        assert agents_client is not dropbox_client  # type: ignore[comparison-overlap]
        assert agents_client is not rev_share_client  # type: ignore[comparison-overlap]
        assert directory_client is not documents_client  # type: ignore[comparison-overlap]
        assert directory_client is not dropbox_client  # type: ignore[comparison-overlap]
        assert directory_client is not rev_share_client  # type: ignore[comparison-overlap]
        assert documents_client is not dropbox_client  # type: ignore[comparison-overlap]
        assert documents_client is not rev_share_client  # type: ignore[comparison-overlap]

        assert dropbox_client is not rev_share_client  # type: ignore[comparison-overlap]

        assert isinstance(tb_client, TransactionBuilderClient)
        assert isinstance(transactions_client, TransactionsClient)
        assert isinstance(teams_client, TeamsClient)
        assert isinstance(agents_client, AgentsClient)
        assert isinstance(directory_client, DirectoryClient)
        assert isinstance(documents_client, DocumentClient)
        assert isinstance(dropbox_client, DropboxClient)
        assert isinstance(rev_share_client, RevShareClient)

        # Verify they all have the same API key
        assert tb_client.api_key == "test_key"
        assert transactions_client.api_key == "test_key"
        assert teams_client.api_key == "test_key"
        assert agents_client.api_key == "test_key"
        assert directory_client.api_key == "test_key"
        assert documents_client.api_key == "test_key"
        assert dropbox_client.api_key == "test_key"
        assert rev_share_client.api_key == "test_key"

    def test_agents_property_lazy_loading(self) -> None:
        """Test that agents property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._agents is None

        # First access creates the client
        agents_client = client.agents
        assert isinstance(agents_client, AgentsClient)

        # Second access returns the same instance
        agents_client2 = client.agents
        assert agents_client2 is agents_client

    def test_agents_property_passes_api_key(self) -> None:
        """Test that agents property passes API key (but not base URL due to different API)."""
        api_key = "test_key"

        client = RezenClient(api_key=api_key, base_url="https://test.example.com")
        agents_client = client.agents

        assert agents_client.api_key == api_key
        # Agents uses different base URL, so it should not inherit the main base URL
        assert agents_client.base_url == "https://yenta.therealbrokerage.com/api/v1"

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_test_key"})
    def test_agents_with_env_api_key(self) -> None:
        """Test agents with API key from environment."""
        client = RezenClient()
        agents_client = client.agents

        assert agents_client.api_key == "env_test_key"

    def test_directory_property_lazy_loading(self) -> None:
        """Test that directory property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._directory is None

        # First access creates the client
        directory_client = client.directory
        assert isinstance(directory_client, DirectoryClient)

        # Second access returns the same instance
        directory_client2 = client.directory
        assert directory_client2 is directory_client

    def test_directory_property_passes_api_key(self) -> None:
        """Test that directory property passes API key (but not base URL due to different API)."""
        api_key = "test_key"

        client = RezenClient(api_key=api_key, base_url="https://test.example.com")
        directory_client = client.directory

        assert directory_client.api_key == api_key
        # Directory uses different base URL, so it should not inherit the main base URL
        assert directory_client.base_url == "https://yenta.therealbrokerage.com/api/v1"

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_test_key"})
    def test_directory_with_env_api_key(self) -> None:
        """Test directory with API key from environment."""
        client = RezenClient()
        directory_client = client.directory

        assert directory_client.api_key == "env_test_key"

    def test_documents_property_lazy_loading(self) -> None:
        """Test that documents property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._documents is None

        # First access creates the client
        documents_client = client.documents
        assert isinstance(documents_client, DocumentClient)

        # Second access returns the same instance
        documents_client2 = client.documents
        assert documents_client2 is documents_client

    def test_documents_property_passes_parameters(self) -> None:
        """Test that documents property passes API key and base URL."""
        api_key = "test_key"
        base_url = "https://test.example.com"

        client = RezenClient(api_key=api_key, base_url=base_url)
        documents_client = client.documents

        assert documents_client.api_key == api_key
        assert documents_client.base_url == base_url

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_test_key"})
    def test_documents_with_env_api_key(self) -> None:
        """Test documents with API key from environment."""
        client = RezenClient()
        documents_client = client.documents

        assert documents_client.api_key == "env_test_key"

    def test_dropbox_property_lazy_loading(self) -> None:
        """Test that dropbox property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._dropbox is None

        # First access creates the client
        dropbox_client = client.dropbox
        assert isinstance(dropbox_client, DropboxClient)

        # Second access returns the same instance
        dropbox_client2 = client.dropbox
        assert dropbox_client2 is dropbox_client

    def test_dropbox_property_passes_api_key(self) -> None:
        """Test that dropbox property passes API key (but not base URL due to different API)."""
        api_key = "test_key"

        client = RezenClient(api_key=api_key, base_url="https://test.example.com")
        dropbox_client = client.dropbox

        assert dropbox_client.api_key == api_key
        # Dropbox uses different base URL, so it should not inherit the main base URL
        assert dropbox_client.base_url == "https://sherlock.therealbrokerage.com/api/v1"

    @patch.dict("os.environ", {"REZEN_API_KEY": "env_test_key"})
    def test_dropbox_with_env_api_key(self) -> None:
        """Test dropbox with API key from environment."""
        client = RezenClient()
        dropbox_client = client.dropbox

        assert dropbox_client.api_key == "env_test_key"

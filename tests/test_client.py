"""Tests for the main ReZEN client."""

from unittest.mock import patch

from rezen.agents import AgentsClient
from rezen.client import RezenClient
from rezen.directory import DirectoryClient
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
        assert client._transaction_builder is None
        assert client._transactions is None
        assert client._teams is None
        assert client._agents is None
        assert client._directory is None

    def test_init_with_parameters(self) -> None:
        """Test initialization with API key and base URL."""
        client = RezenClient(api_key="test_key", base_url="https://test.example.com")
        assert client._api_key == "test_key"
        assert client._base_url == "https://test.example.com"
        assert client._transaction_builder is None
        assert client._transactions is None
        assert client._teams is None
        assert client._agents is None
        assert client._directory is None

    def test_transaction_builder_property_lazy_loading(self) -> None:
        """Test that transaction_builder property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._transaction_builder is None

        # First access creates the client
        tb_client = client.transaction_builder
        assert isinstance(tb_client, TransactionBuilderClient)
        assert client._transaction_builder is tb_client

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
        assert client._transactions is transactions_client

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

    def test_teams_property_lazy_loading(self) -> None:
        """Test that teams property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._teams is None

        # First access creates the client
        teams_client = client.teams
        assert isinstance(teams_client, TeamsClient)
        assert client._teams is teams_client

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

        # Verify they are different instances
        assert tb_client is not transactions_client  # type: ignore[comparison-overlap]
        assert tb_client is not teams_client  # type: ignore[comparison-overlap]
        assert tb_client is not agents_client  # type: ignore[comparison-overlap]
        assert tb_client is not directory_client  # type: ignore[comparison-overlap]
        assert transactions_client is not teams_client  # type: ignore[comparison-overlap]
        assert transactions_client is not agents_client  # type: ignore[comparison-overlap]
        assert transactions_client is not directory_client  # type: ignore[comparison-overlap]
        assert teams_client is not agents_client  # type: ignore[comparison-overlap]
        assert teams_client is not directory_client  # type: ignore[comparison-overlap]
        assert agents_client is not directory_client  # type: ignore[comparison-overlap]

        assert isinstance(tb_client, TransactionBuilderClient)
        assert isinstance(transactions_client, TransactionsClient)
        assert isinstance(teams_client, TeamsClient)
        assert isinstance(agents_client, AgentsClient)
        assert isinstance(directory_client, DirectoryClient)

        # Verify they all have the same API key
        assert tb_client.api_key == "test_key"
        assert transactions_client.api_key == "test_key"
        assert teams_client.api_key == "test_key"
        assert agents_client.api_key == "test_key"
        assert directory_client.api_key == "test_key"

    def test_agents_property_lazy_loading(self) -> None:
        """Test that agents property creates client on first access."""
        client = RezenClient(api_key="test_key")

        # Initially None
        assert client._agents is None

        # First access creates the client
        agents_client = client.agents
        assert isinstance(agents_client, AgentsClient)
        assert client._agents is agents_client

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
        assert client._directory is directory_client

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

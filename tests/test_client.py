"""Tests for the main ReZEN client."""

from unittest.mock import patch

import pytest

from rezen.client import RezenClient
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

    def test_init_with_parameters(self) -> None:
        """Test initialization with API key and base URL."""
        client = RezenClient(api_key="test_key", base_url="https://test.example.com")
        assert client._api_key == "test_key"
        assert client._base_url == "https://test.example.com"
        assert client._transaction_builder is None
        assert client._transactions is None
        assert client._teams is None

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

        # Verify they are different instances
        assert tb_client is not transactions_client
        assert tb_client is not teams_client
        assert transactions_client is not teams_client

        assert isinstance(tb_client, TransactionBuilderClient)
        assert isinstance(transactions_client, TransactionsClient)
        assert isinstance(teams_client, TeamsClient)

        # Verify they all have the same API key
        assert tb_client.api_key == "test_key"
        assert transactions_client.api_key == "test_key"
        assert teams_client.api_key == "test_key"

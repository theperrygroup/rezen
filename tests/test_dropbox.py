"""Tests for Dropbox integration client."""

from typing import Any, Dict
from unittest.mock import Mock, mock_open, patch

import pytest

from rezen.dropbox import DropboxClient
from rezen.exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    ServerError,
    ValidationError,
)


class TestDropboxClient:
    """Test cases for DropboxClient."""

    @pytest.fixture
    def dropbox_client(self) -> DropboxClient:
        """Create DropboxClient instance for testing."""
        return DropboxClient(api_key="test_api_key")

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Create mock session for testing."""
        return Mock()

    def test_dropbox_client_initialization(self) -> None:
        """Test DropboxClient initialization."""
        client = DropboxClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert "sherlock.therealbrokerage.com" in client.base_url

    def test_dropbox_client_with_custom_base_url(self) -> None:
        """Test DropboxClient with custom base URL."""
        custom_url = "https://test.example.com/api/v1"
        client = DropboxClient(api_key="test_key", base_url=custom_url)
        assert client.base_url == custom_url

    @patch("rezen.dropbox.DropboxClient.get")
    def test_get_auth_url_success(
        self, mock_get: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test successful retrieval of Dropbox auth URL."""
        mock_response = {"url": "https://dropbox.com/oauth/authorize?client_id=123"}
        mock_get.return_value = mock_response

        result = dropbox_client.get_auth_url()

        mock_get.assert_called_once_with("dropbox/auth-url")
        assert result == mock_response
        assert "url" in result

    @patch("rezen.dropbox.DropboxClient.get")
    def test_get_auth_url_network_error(
        self, mock_get: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test get_auth_url with network error."""
        mock_get.side_effect = NetworkError("Connection failed")

        with pytest.raises(NetworkError):
            dropbox_client.get_auth_url()

    @patch("rezen.dropbox.DropboxClient.post")
    def test_save_token_success(
        self, mock_post: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test successful token save."""
        mock_response: Dict[str, Any] = {}
        mock_post.return_value = mock_response

        result = dropbox_client.save_token("auth_code_123")

        mock_post.assert_called_once_with(
            "dropbox/token",
            json_data={"code": "auth_code_123"},
        )
        assert result == mock_response

    def test_save_token_empty_code(self, dropbox_client: DropboxClient) -> None:
        """Test save_token with empty code."""
        with pytest.raises(ValidationError) as exc_info:
            dropbox_client.save_token("")

        assert "Authorization code is required" in str(exc_info.value)

    @patch("rezen.dropbox.DropboxClient.post")
    def test_save_token_authentication_error(
        self, mock_post: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test save_token with authentication error."""
        mock_post.side_effect = AuthenticationError("Invalid auth code")

        with pytest.raises(AuthenticationError):
            dropbox_client.save_token("invalid_code")

    @patch("rezen.dropbox.DropboxClient.get")
    def test_get_folders_success(
        self, mock_get: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test successful folder retrieval."""
        mock_response = [
            {"name": "Documents", "path": "/Documents"},
            {"name": "Photos", "path": "/Photos"},
        ]
        mock_get.return_value = mock_response

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        result = dropbox_client.get_folders(agent_id)

        mock_get.assert_called_once_with(f"dropbox/{agent_id}/folders", params=None)
        assert result == mock_response
        assert len(result) == 2
        assert result[0]["name"] == "Documents"

    @patch("rezen.dropbox.DropboxClient.get")
    def test_get_folders_with_path(
        self, mock_get: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test folder retrieval with specific path."""
        mock_response = [
            {"name": "Contracts", "path": "/Documents/Contracts"},
            {"name": "Invoices", "path": "/Documents/Invoices"},
        ]
        mock_get.return_value = mock_response

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        result = dropbox_client.get_folders(agent_id, path="/Documents")

        mock_get.assert_called_once_with(
            f"dropbox/{agent_id}/folders",
            params={"path": "/Documents"},
        )
        assert result == mock_response

    def test_get_folders_empty_agent_id(self, dropbox_client: DropboxClient) -> None:
        """Test get_folders with empty agent ID."""
        with pytest.raises(ValidationError) as exc_info:
            dropbox_client.get_folders("")

        assert "Agent ID is required" in str(exc_info.value)

    @patch("rezen.dropbox.DropboxClient.get")
    def test_get_folders_not_found(
        self, mock_get: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test get_folders when agent not found."""
        mock_get.side_effect = NotFoundError("Agent not found")

        with pytest.raises(NotFoundError):
            dropbox_client.get_folders("nonexistent-agent")

    @patch("rezen.dropbox.DropboxClient.post")
    def test_upload_file_success(
        self, mock_post: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test successful file upload."""
        mock_response: Dict[str, Any] = {}
        mock_post.return_value = mock_response

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_file = mock_open(read_data=b"file content")()

        result = dropbox_client.upload_file(
            agent_id=agent_id,
            file=mock_file,
            path="/transactions/document.pdf",
        )

        mock_post.assert_called_once_with(
            f"dropbox/{agent_id}/files",
            data={"path": "/transactions/document.pdf"},
            files={"file": mock_file},
        )
        assert result == mock_response

    def test_upload_file_missing_agent_id(self, dropbox_client: DropboxClient) -> None:
        """Test upload_file with missing agent ID."""
        mock_file = mock_open(read_data=b"file content")()

        with pytest.raises(ValidationError) as exc_info:
            dropbox_client.upload_file(
                agent_id="",
                file=mock_file,
                path="/test.pdf",
            )

        assert "Agent ID is required" in str(exc_info.value)

    def test_upload_file_missing_file(self, dropbox_client: DropboxClient) -> None:
        """Test upload_file with missing file."""
        with pytest.raises(ValidationError) as exc_info:
            dropbox_client.upload_file(
                agent_id="550e8400-e29b-41d4-a716-446655440000",
                file=None,  # type: ignore
                path="/test.pdf",
            )

        assert "File is required" in str(exc_info.value)

    def test_upload_file_missing_path(self, dropbox_client: DropboxClient) -> None:
        """Test upload_file with missing path."""
        mock_file = mock_open(read_data=b"file content")()

        with pytest.raises(ValidationError) as exc_info:
            dropbox_client.upload_file(
                agent_id="550e8400-e29b-41d4-a716-446655440000",
                file=mock_file,
                path="",
            )

        assert "Path is required" in str(exc_info.value)

    @patch("rezen.dropbox.DropboxClient.post")
    def test_create_folder_success(
        self, mock_post: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test successful folder creation."""
        mock_response: Dict[str, Any] = {}
        mock_post.return_value = mock_response

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        result = dropbox_client.create_folder(
            agent_id=agent_id,
            path="/transactions/2024/january",
        )

        mock_post.assert_called_once_with(
            f"dropbox/{agent_id}/folders",
            json_data={"path": "/transactions/2024/january"},
        )
        assert result == mock_response

    def test_create_folder_missing_agent_id(
        self, dropbox_client: DropboxClient
    ) -> None:
        """Test create_folder with missing agent ID."""
        with pytest.raises(ValidationError) as exc_info:
            dropbox_client.create_folder(
                agent_id="",
                path="/new-folder",
            )

        assert "Agent ID is required" in str(exc_info.value)

    def test_create_folder_missing_path(self, dropbox_client: DropboxClient) -> None:
        """Test create_folder with missing path."""
        with pytest.raises(ValidationError) as exc_info:
            dropbox_client.create_folder(
                agent_id="550e8400-e29b-41d4-a716-446655440000",
                path="",
            )

        assert "Path is required" in str(exc_info.value)

    @patch("rezen.dropbox.DropboxClient.post")
    def test_create_folder_conflict(
        self, mock_post: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test create_folder when folder already exists."""
        mock_post.side_effect = ValidationError("Folder already exists")

        with pytest.raises(ValidationError):
            dropbox_client.create_folder(
                agent_id="550e8400-e29b-41d4-a716-446655440000",
                path="/existing-folder",
            )

    def test_integration_workflow(self, dropbox_client: DropboxClient) -> None:
        """Test a complete Dropbox integration workflow."""
        with patch.object(dropbox_client, "get") as mock_get, patch.object(
            dropbox_client, "post"
        ) as mock_post:
            # Step 1: Get auth URL
            mock_get.return_value = {
                "url": "https://dropbox.com/oauth/authorize?client_id=123"
            }
            auth_url = dropbox_client.get_auth_url()
            assert "url" in auth_url

            # Step 2: Save token
            mock_post.return_value = {}
            dropbox_client.save_token("auth_code_123")

            # Step 3: Get folders
            mock_get.return_value = [
                {"name": "Documents", "path": "/Documents"},
            ]
            folders = dropbox_client.get_folders("agent-id")
            assert len(folders) == 1

            # Step 4: Create folder
            mock_post.return_value = {}
            dropbox_client.create_folder("agent-id", "/Documents/New")

            # Step 5: Upload file
            mock_file = mock_open(read_data=b"content")()
            mock_post.return_value = {}
            dropbox_client.upload_file("agent-id", mock_file, "/Documents/New/file.pdf")

            # Verify all calls were made
            assert mock_get.call_count == 2
            assert mock_post.call_count == 3

    @patch("rezen.dropbox.DropboxClient.get")
    def test_get_folders_empty_response(
        self, mock_get: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test get_folders with empty response."""
        mock_get.return_value = []

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        result = dropbox_client.get_folders(agent_id)

        assert result == []
        assert len(result) == 0

    @patch("rezen.dropbox.DropboxClient.post")
    def test_upload_file_with_large_file(
        self, mock_post: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test uploading a large file."""
        mock_response: Dict[str, Any] = {}
        mock_post.return_value = mock_response

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        # Simulate a large file (100MB)
        large_content = b"x" * (100 * 1024 * 1024)
        mock_file = mock_open(read_data=large_content)()

        result = dropbox_client.upload_file(
            agent_id=agent_id,
            file=mock_file,
            path="/large-files/big-document.pdf",
        )

        assert result == mock_response

    @patch("rezen.dropbox.DropboxClient.post")
    def test_create_folder_with_special_characters(
        self, mock_post: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test creating folder with special characters in path."""
        mock_response: Dict[str, Any] = {}
        mock_post.return_value = mock_response

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        special_path = "/Transactions/John & Jane's Deal #123 (2024)"

        result = dropbox_client.create_folder(
            agent_id=agent_id,
            path=special_path,
        )

        mock_post.assert_called_once_with(
            f"dropbox/{agent_id}/folders",
            json_data={"path": special_path},
        )
        assert result == mock_response

    @patch("rezen.dropbox.DropboxClient.get")
    def test_get_folders_with_deeply_nested_path(
        self, mock_get: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test get_folders with deeply nested path."""
        mock_response = [
            {"name": "SubFolder1", "path": "/A/B/C/D/E/SubFolder1"},
            {"name": "SubFolder2", "path": "/A/B/C/D/E/SubFolder2"},
        ]
        mock_get.return_value = mock_response

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        deep_path = "/A/B/C/D/E"
        result = dropbox_client.get_folders(agent_id, path=deep_path)

        mock_get.assert_called_once_with(
            f"dropbox/{agent_id}/folders",
            params={"path": deep_path},
        )
        assert len(result) == 2

    def test_save_token_with_whitespace_code(
        self, dropbox_client: DropboxClient
    ) -> None:
        """Test save_token with whitespace-only code."""
        with pytest.raises(ValidationError) as exc_info:
            dropbox_client.save_token("   ")

        assert "Authorization code is required" in str(exc_info.value)

    @patch("rezen.dropbox.DropboxClient.post")
    def test_upload_file_server_error(
        self, mock_post: Mock, dropbox_client: DropboxClient
    ) -> None:
        """Test upload_file with server error response."""
        mock_post.side_effect = ServerError("Internal server error")

        agent_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_file = mock_open(read_data=b"content")()

        with pytest.raises(ServerError):
            dropbox_client.upload_file(
                agent_id=agent_id,
                file=mock_file,
                path="/test.pdf",
            )

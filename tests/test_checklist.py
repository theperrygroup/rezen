"""Tests for ChecklistClient."""

import io
from unittest.mock import patch

import pytest
import responses

from rezen.checklist import ChecklistClient
from rezen.exceptions import AuthenticationError, NotFoundError, ValidationError


class TestChecklistClient:
    """Test cases for ChecklistClient."""

    @pytest.fixture
    def client(self) -> ChecklistClient:
        """Create ChecklistClient instance for testing."""
        return ChecklistClient(api_key="test_api_key")

    def test_client_initialization(self) -> None:
        """Test ChecklistClient initialization."""
        client = ChecklistClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://sherlock.therealbrokerage.com/api/v1"

    def test_client_initialization_with_custom_base_url(self) -> None:
        """Test ChecklistClient initialization with custom base URL."""
        custom_url = "https://test.example.com/api/v1"
        client = ChecklistClient(api_key="test_key", base_url=custom_url)
        assert client.base_url == custom_url

    @responses.activate
    def test_get_checklist_item(self, client: ChecklistClient) -> None:
        """Test getting checklist item by ID."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        expected_response = {
            "id": checklist_item_id,
            "createdAt": 1640995200000,
            "name": "Test Item",
            "checklistId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "updatedAt": 1640995200000,
            "description": "Test description",
            "position": 1,
            "required": True,
            "complete": False,
        }

        responses.add(
            responses.GET,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}",
            json=expected_response,
            status=200,
        )

        result = client.get_checklist_item(checklist_item_id)

        assert len(responses.calls) == 1
        assert result == expected_response

    @responses.activate
    def test_update_checklist_item(self, client: ChecklistClient) -> None:
        """Test updating checklist item."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        item_data = {
            "item": {
                "id": checklist_item_id,
                "name": "Updated Item",
                "description": "Updated description",
                "required": True,
                "complete": True,
            }
        }

        responses.add(
            responses.PUT,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}",
            json={"success": True},
            status=200,
        )

        result = client.update_checklist_item(checklist_item_id, item_data)

        assert len(responses.calls) == 1
        assert result == {"success": True}

    @responses.activate
    def test_delete_checklist_item(self, client: ChecklistClient) -> None:
        """Test deleting checklist item."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        expected_response = {"status": True, "message": "Item deleted successfully"}

        responses.add(
            responses.DELETE,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}",
            json=expected_response,
            status=200,
        )

        result = client.delete_checklist_item(checklist_item_id)

        assert len(responses.calls) == 1
        assert result == expected_response

    @responses.activate
    def test_complete_checklist_item_default(self, client: ChecklistClient) -> None:
        """Test marking checklist item as complete with default value."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

        responses.add(
            responses.PUT,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}/complete",
            json={"success": True},
            status=200,
        )

        result = client.complete_checklist_item(checklist_item_id)

        assert len(responses.calls) == 1
        request_url = responses.calls[0].request.url
        assert "isComplete=True" in request_url
        assert result == {"success": True}

    @responses.activate
    def test_complete_checklist_item_false(self, client: ChecklistClient) -> None:
        """Test marking checklist item as incomplete."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

        responses.add(
            responses.PUT,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}/complete",
            json={"success": True},
            status=200,
        )

        result = client.complete_checklist_item(checklist_item_id, is_complete=False)

        assert len(responses.calls) == 1
        request_url = responses.calls[0].request.url
        assert "isComplete=False" in request_url
        assert result == {"success": True}

    @responses.activate
    def test_get_checklist_document(self, client: ChecklistClient) -> None:
        """Test getting checklist document by ID."""
        document_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        expected_response = {
            "id": document_id,
            "createdAt": 1640995200000,
            "name": "Test Document",
            "description": "Test document description",
            "versions": [],
            "currentVersion": None,
        }

        responses.add(
            responses.GET,
            f"{client.base_url}/checklists/checklist-documents/{document_id}",
            json=expected_response,
            status=200,
        )

        result = client.get_checklist_document(document_id)

        assert len(responses.calls) == 1
        assert result == expected_response

    @responses.activate
    def test_update_checklist_document(self, client: ChecklistClient) -> None:
        """Test updating checklist document."""
        document_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        document_data = {
            "id": document_id,
            "name": "Updated Document",
            "description": "Updated description",
            "versions": [],
        }

        responses.add(
            responses.PUT,
            f"{client.base_url}/checklists/checklist-documents/{document_id}",
            json={"success": True},
            status=200,
        )

        result = client.update_checklist_document(document_id, document_data)

        assert len(responses.calls) == 1
        assert result == {"success": True}

    @responses.activate
    def test_delete_checklist_document(self, client: ChecklistClient) -> None:
        """Test deleting checklist document."""
        document_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

        responses.add(
            responses.DELETE,
            f"{client.base_url}/checklists/checklist-documents/{document_id}",
            json={"success": True},
            status=200,
        )

        result = client.delete_checklist_document(document_id)

        assert len(responses.calls) == 1
        assert result == {"success": True}

    @responses.activate
    def test_create_checklist_item(self, client: ChecklistClient) -> None:
        """Test creating checklist item."""
        checklist_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        item_data = {
            "item": {
                "name": "New Item",
                "description": "New item description",
                "required": True,
                "position": 1,
            }
        }

        responses.add(
            responses.POST,
            f"{client.base_url}/checklists/{checklist_id}/items",
            json={"success": True, "id": "new-item-id"},
            status=200,
        )

        result = client.create_checklist_item(checklist_id, item_data)

        assert len(responses.calls) == 1
        assert result == {"success": True, "id": "new-item-id"}

    @responses.activate
    def test_create_checklist(self, client: ChecklistClient) -> None:
        """Test creating checklist from definition."""
        checklist_definition_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        checklist_data = {
            "parentId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "parentType": "TRANSACTION",
            "assignees": {"agent1": "3fa85f64-5717-4562-b3fc-2c963f66afa6"},
            "brokerAgentId": "broker-123",
            "ownerAgentId": "owner-123",
        }

        responses.add(
            responses.POST,
            f"{client.base_url}/checklists/{checklist_definition_id}",
            json={"success": True, "checklistId": "new-checklist-id"},
            status=200,
        )

        result = client.create_checklist(checklist_definition_id, checklist_data)

        assert len(responses.calls) == 1
        assert result == {"success": True, "checklistId": "new-checklist-id"}

    @responses.activate
    def test_add_document_to_checklist_item_with_file(
        self, client: ChecklistClient
    ) -> None:
        """Test adding document to checklist item with file upload."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        uploader_id = "123e4567-e89b-12d3-a456-426614174000"
        transaction_id = "987fcdeb-51d2-4321-b789-123456789012"
        file_content = b"test file content"
        file_obj = io.BytesIO(file_content)

        expected_response = {
            "id": "doc-123",
            "name": "Test Document",
            "description": "Test document",
            "createdAt": 1640995200000,
        }

        responses.add(
            responses.POST,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}/documents",
            json=expected_response,
            status=200,
        )

        with patch.object(
            client, "_request", return_value=expected_response
        ) as mock_request:
            result = client.add_document_to_checklist_item(
                checklist_item_id=checklist_item_id,
                name="Test Document",
                description="Test document",
                uploader_id=uploader_id,
                transaction_id=transaction_id,
                file=file_obj,
            )

            mock_request.assert_called_once_with(
                "POST",
                f"checklists/checklist-items/{checklist_item_id}/documents",
                data={
                    "name": "Test Document",
                    "description": "Test document",
                    "uploaderId": uploader_id,
                    "transactionId": transaction_id,
                },
                files={"file": file_obj},
            )
            assert result == expected_response

    def test_add_document_to_checklist_item_validation_errors(
        self, client: ChecklistClient
    ) -> None:
        """Test validation errors for add_document_to_checklist_item."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        uploader_id = "123e4567-e89b-12d3-a456-426614174000"
        transaction_id = "987fcdeb-51d2-4321-b789-123456789012"
        file_obj = io.BytesIO(b"test content")

        # Test empty name
        with pytest.raises(ValidationError, match="Document name is required"):
            client.add_document_to_checklist_item(
                checklist_item_id=checklist_item_id,
                name="",
                description="Test document",
                uploader_id=uploader_id,
                transaction_id=transaction_id,
                file=file_obj,
            )

        # Test invalid UUID format
        with pytest.raises(ValidationError, match="Invalid parameter format"):
            client.add_document_to_checklist_item(
                checklist_item_id=checklist_item_id,
                name="Test Document",
                description="Test document",
                uploader_id="invalid-uuid",
                transaction_id=transaction_id,
                file=file_obj,
            )

    def test_add_document_to_checklist_item_additional_validation_errors(
        self, client: ChecklistClient
    ) -> None:
        """Test additional required-field validations."""
        valid_uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        file_obj = io.BytesIO(b"test content")

        with pytest.raises(ValidationError, match="Document description is required"):
            client.add_document_to_checklist_item(
                checklist_item_id=valid_uuid,
                name="Test Document",
                description="",
                uploader_id=valid_uuid,
                transaction_id=valid_uuid,
                file=file_obj,
            )

        with pytest.raises(ValidationError, match="Checklist item ID is required"):
            client.add_document_to_checklist_item(
                checklist_item_id="",
                name="Test Document",
                description="Test document",
                uploader_id=valid_uuid,
                transaction_id=valid_uuid,
                file=file_obj,
            )

        with pytest.raises(ValidationError, match="Uploader ID is required"):
            client.add_document_to_checklist_item(
                checklist_item_id=valid_uuid,
                name="Test Document",
                description="Test document",
                uploader_id="",
                transaction_id=valid_uuid,
                file=file_obj,
            )

        with pytest.raises(ValidationError, match="Transaction ID is required"):
            client.add_document_to_checklist_item(
                checklist_item_id=valid_uuid,
                name="Test Document",
                description="Test document",
                uploader_id=valid_uuid,
                transaction_id="",
                file=file_obj,
            )

        with pytest.raises(
            ValidationError, match="File is required for document upload"
        ):
            client.add_document_to_checklist_item(
                checklist_item_id=valid_uuid,
                name="Test Document",
                description="Test document",
                uploader_id=valid_uuid,
                transaction_id=valid_uuid,
                file=None,  # type: ignore[arg-type]
            )

    def test_add_document_to_checklist_item_enhanced_bad_request_message(
        self, client: ChecklistClient
    ) -> None:
        """Test enhanced debugging information when API returns Bad request."""
        valid_uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                client,
                "_request",
                lambda *_args, **_kwargs: (_ for _ in ()).throw(
                    ValidationError("Bad request: Invalid request")
                ),
            )

            with pytest.raises(ValidationError) as exc:
                client.add_document_to_checklist_item(
                    checklist_item_id=valid_uuid,
                    name="Test Document",
                    description="Test document",
                    uploader_id=valid_uuid,
                    transaction_id=valid_uuid,
                    file=io.BytesIO(b"x"),
                )

            assert "Debugging checklist" in str(exc.value)

    @responses.activate
    def test_add_document_version_with_file(self, client: ChecklistClient) -> None:
        """Test adding document version with file upload."""
        checklist_document_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        uploader_id = "123e4567-e89b-12d3-a456-426614174000"
        transaction_id = "987fcdeb-51d2-4321-b789-123456789012"
        file_content = b"test file content"
        file_obj = io.BytesIO(file_content)

        expected_response = {
            "id": "version-123",
            "name": "Version 2",
            "description": "Second version",
            "number": 2,
            "createdAt": 1640995200000,
        }

        responses.add(
            responses.POST,
            f"{client.base_url}/checklists/checklist-documents/{checklist_document_id}/versions",
            json=expected_response,
            status=200,
        )

        with patch.object(
            client, "_request", return_value=expected_response
        ) as mock_request:
            result = client.add_document_version(
                checklist_document_id=checklist_document_id,
                name="Version 2",
                description="Second version",
                uploader_id=uploader_id,
                transaction_id=transaction_id,
                file=file_obj,
            )

            mock_request.assert_called_once_with(
                "POST",
                f"checklists/checklist-documents/{checklist_document_id}/versions",
                data={
                    "name": "Version 2",
                    "description": "Second version",
                    "uploaderId": uploader_id,
                    "transactionId": transaction_id,
                },
                files={"file": file_obj},
            )
            assert result == expected_response

    def test_add_document_version_validation_errors(
        self, client: ChecklistClient
    ) -> None:
        """Test validation errors for add_document_version."""
        valid_uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

        with pytest.raises(ValidationError, match="Version name is required"):
            client.add_document_version(
                checklist_document_id=valid_uuid,
                name="",
                description="Second version",
                uploader_id=valid_uuid,
                transaction_id=valid_uuid,
                file=io.BytesIO(b"x"),
            )

        with pytest.raises(ValidationError, match="Version description is required"):
            client.add_document_version(
                checklist_document_id=valid_uuid,
                name="Version 2",
                description="",
                uploader_id=valid_uuid,
                transaction_id=valid_uuid,
                file=io.BytesIO(b"x"),
            )

        with pytest.raises(ValidationError, match="Checklist document ID is required"):
            client.add_document_version(
                checklist_document_id="",
                name="Version 2",
                description="Second version",
                uploader_id=valid_uuid,
                transaction_id=valid_uuid,
                file=io.BytesIO(b"x"),
            )

        with pytest.raises(ValidationError, match="Uploader ID is required"):
            client.add_document_version(
                checklist_document_id=valid_uuid,
                name="Version 2",
                description="Second version",
                uploader_id="",
                transaction_id=valid_uuid,
                file=io.BytesIO(b"x"),
            )

        with pytest.raises(ValidationError, match="Transaction ID is required"):
            client.add_document_version(
                checklist_document_id=valid_uuid,
                name="Version 2",
                description="Second version",
                uploader_id=valid_uuid,
                transaction_id="",
                file=io.BytesIO(b"x"),
            )

        with pytest.raises(
            ValidationError, match="File is required for document version upload"
        ):
            client.add_document_version(
                checklist_document_id=valid_uuid,
                name="Version 2",
                description="Second version",
                uploader_id=valid_uuid,
                transaction_id=valid_uuid,
                file=None,  # type: ignore[arg-type]
            )

    def test_add_document_version_invalid_uuid_format(
        self, client: ChecklistClient
    ) -> None:
        """Test invalid UUIDs are wrapped with context for add_document_version."""
        with pytest.raises(ValidationError, match="Invalid parameter format"):
            client.add_document_version(
                checklist_document_id="not-a-uuid",
                name="Version 2",
                description="Second version",
                uploader_id="also-not-a-uuid",
                transaction_id="still-not-a-uuid",
                file=io.BytesIO(b"x"),
            )

    def test_add_document_version_enhanced_bad_request_message(
        self, client: ChecklistClient
    ) -> None:
        """Test enhanced debugging information when version upload fails with Bad request."""
        valid_uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                client,
                "_request",
                lambda *_args, **_kwargs: (_ for _ in ()).throw(
                    ValidationError("Bad request: Invalid request")
                ),
            )

            with pytest.raises(ValidationError) as exc:
                client.add_document_version(
                    checklist_document_id=valid_uuid,
                    name="Version 2",
                    description="Second version",
                    uploader_id=valid_uuid,
                    transaction_id=valid_uuid,
                    file=io.BytesIO(b"x"),
                )

            assert "Debugging checklist" in str(exc.value)

    @responses.activate
    def test_batch_update_checklists(self, client: ChecklistClient) -> None:
        """Test batch updating checklists."""
        batch_items = [
            {
                "checklistId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "patch": {"locked": True},
            },
            {
                "checklistId": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                "patch": {"approved": True},
            },
        ]

        responses.add(
            responses.POST,
            f"{client.base_url}/checklists/batch-update",
            json={"success": True, "updatedCount": 2},
            status=200,
        )

        result = client.batch_update_checklists(batch_items)

        assert len(responses.calls) == 1
        assert result == {"success": True, "updatedCount": 2}

    @responses.activate
    def test_get_checklist(self, client: ChecklistClient) -> None:
        """Test getting checklist by ID."""
        checklist_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        expected_response = {
            "id": checklist_id,
            "createdAt": 1640995200000,
            "name": "Test Checklist",
            "items": [],
            "approved": False,
            "locked": False,
        }

        responses.add(
            responses.GET,
            f"{client.base_url}/checklists/{checklist_id}",
            json=expected_response,
            status=200,
        )

        result = client.get_checklist(checklist_id)

        assert len(responses.calls) == 1
        assert result == expected_response

    @responses.activate
    def test_get_checklists_progress(self, client: ChecklistClient) -> None:
        """Test getting checklists progress."""
        checklist_ids = ["checklist-1", "checklist-2"]
        expected_response = [
            {
                "checklistId": "checklist-1",
                "itemCount": 5,
                "completedCount": 3,
                "itemCountIncludingOptionals": 7,
                "completedCountIncludingOptionals": 4,
            },
            {
                "checklistId": "checklist-2",
                "itemCount": 3,
                "completedCount": 2,
                "itemCountIncludingOptionals": 4,
                "completedCountIncludingOptionals": 3,
            },
        ]

        responses.add(
            responses.GET,
            f"{client.base_url}/checklists/progress",
            json=expected_response,
            status=200,
        )

        result = client.get_checklists_progress(checklist_ids)

        assert len(responses.calls) == 1
        request_url = responses.calls[0].request.url
        assert "checklistIds=checklist-1" in request_url
        assert "checklistIds=checklist-2" in request_url
        assert result == expected_response

    @responses.activate
    def test_download_document_version(self, client: ChecklistClient) -> None:
        """Test downloading document version."""
        version_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        expected_response = {"downloadUrl": "https://example.com/download/file.pdf"}

        responses.add(
            responses.GET,
            f"{client.base_url}/checklists/checklist-documents/versions/{version_id}/download",
            json=expected_response,
            status=200,
        )

        result = client.download_document_version(version_id)

        assert len(responses.calls) == 1
        assert result == expected_response

    @responses.activate
    def test_link_file_to_checklist_item(self, client: ChecklistClient) -> None:
        """Test link_file_to_checklist_item endpoint."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        responses.add(
            responses.POST,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}/file-references",
            json={"ok": True},
            status=200,
        )

        result = client.link_file_to_checklist_item(
            checklist_item_id, [{"fileId": "file-1", "filename": "x.pdf"}]
        )
        assert result == {"ok": True}

    # Legacy method tests
    @responses.activate
    def test_post_document_to_checklist_legacy(self, client: ChecklistClient) -> None:
        """Test legacy post_document_to_checklist method."""
        checklist_item_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        uploader_id = "123e4567-e89b-12d3-a456-426614174000"
        transaction_id = "987fcdeb-51d2-4321-b789-123456789012"
        data = {
            "name": "Legacy Document",
            "description": "Legacy description",
            "uploaderId": uploader_id,
            "transactionId": transaction_id,
        }
        file_obj = io.BytesIO(b"legacy test content")

        expected_response = {"id": "doc-123", "name": "Legacy Document"}

        responses.add(
            responses.POST,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}/documents",
            json=expected_response,
            status=200,
        )

        with patch.object(
            client, "add_document_to_checklist_item", return_value=expected_response
        ) as mock_method:
            result = client.post_document_to_checklist(
                checklist_item_id, data, file_obj
            )

            mock_method.assert_called_once_with(
                checklist_item_id=checklist_item_id,
                name="Legacy Document",
                description="Legacy description",
                uploader_id=uploader_id,
                transaction_id=transaction_id,
                file=file_obj,
            )
            assert result == expected_response

    def test_post_document_to_checklist_legacy_missing_fields_raises(
        self, client: ChecklistClient
    ) -> None:
        """Test legacy post_document_to_checklist validates required fields."""
        with pytest.raises(ValidationError, match="Missing required fields in data"):
            client.post_document_to_checklist(
                "checklist-item-1", {"name": "Only name"}, io.BytesIO(b"x")
            )

    @responses.activate
    def test_mark_checklist_item_complete_legacy(self, client: ChecklistClient) -> None:
        """Test legacy mark_checklist_item_complete method."""
        checklist_id = "checklist-123"
        checklist_item_id = "item-123"

        responses.add(
            responses.PUT,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}/complete",
            json={"success": True},
            status=200,
        )

        result = client.mark_checklist_item_complete(checklist_id, checklist_item_id)

        assert len(responses.calls) == 1
        request_url = responses.calls[0].request.url
        assert "isComplete=True" in request_url
        assert result == {"success": True}

    @responses.activate
    def test_delete_checklist_item_document_legacy(
        self, client: ChecklistClient
    ) -> None:
        """Test legacy delete_checklist_item_document method."""
        checklist_item_id = "item-123"
        document_id = "doc-123"

        responses.add(
            responses.DELETE,
            f"{client.base_url}/checklists/checklist-documents/{document_id}",
            json={"success": True},
            status=200,
        )

        result = client.delete_checklist_item_document(checklist_item_id, document_id)

        assert len(responses.calls) == 1
        assert result == {"success": True}

    @responses.activate
    def test_get_checklist_templates_legacy(self, client: ChecklistClient) -> None:
        """Test legacy get_checklist_templates method."""
        expected_response = {"templates": [{"id": "template-1", "name": "Template 1"}]}

        responses.add(
            responses.GET,
            f"{client.base_url}/checklists/templates",
            json=expected_response,
            status=200,
        )

        result = client.get_checklist_templates()

        assert len(responses.calls) == 1
        assert result == expected_response

    @responses.activate
    def test_create_checklist_from_template_legacy(
        self, client: ChecklistClient
    ) -> None:
        """Test legacy create_checklist_from_template method."""
        template_id = "template-123"
        data = {"parentId": "parent-123", "name": "New Checklist"}

        expected_response = {"success": True, "checklistId": "checklist-123"}

        responses.add(
            responses.POST,
            f"{client.base_url}/checklists/templates/{template_id}/create",
            json=expected_response,
            status=200,
        )

        result = client.create_checklist_from_template(template_id, data)

        assert len(responses.calls) == 1
        assert result == expected_response

    # Error handling tests
    @responses.activate
    def test_not_found_error(self, client: ChecklistClient) -> None:
        """Test handling of 404 Not Found errors."""
        checklist_item_id = "nonexistent-item"

        responses.add(
            responses.GET,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}",
            json={"message": "Checklist item not found"},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            client.get_checklist_item(checklist_item_id)

    @responses.activate
    def test_validation_error(self, client: ChecklistClient) -> None:
        """Test handling of 400 Validation errors."""
        checklist_item_id = "item-123"
        invalid_data = {"invalid": "data"}

        responses.add(
            responses.PUT,
            f"{client.base_url}/checklists/checklist-items/{checklist_item_id}",
            json={"message": "Invalid request data"},
            status=400,
        )

        with pytest.raises(ValidationError, match="Bad request"):
            client.update_checklist_item(checklist_item_id, invalid_data)

    @responses.activate
    def test_authentication_error(self, client: ChecklistClient) -> None:
        """Test handling of 401 Authentication errors."""
        checklist_id = "checklist-123"

        responses.add(
            responses.GET,
            f"{client.base_url}/checklists/{checklist_id}",
            json={"message": "Unauthorized"},
            status=401,
        )

        with pytest.raises(AuthenticationError, match="Authentication failed"):
            client.get_checklist(checklist_id)

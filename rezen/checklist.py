"""ReZEN Checklist API client implementation."""

from typing import Any, BinaryIO, Dict, List, Optional, Union

from .base_client import BaseClient


class ChecklistClient(BaseClient):
    """
    Client for ReZEN Checklist API endpoints.

    Provides access to checklist-related functionality including:
    - Managing checklists and checklist items
    - Document upload and management
    - Checklist progress tracking
    - Batch operations
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """
        Initialize the Checklist API client.

        Args:
            api_key: ReZEN API key for authentication
            base_url: Base URL for the checklist API. Defaults to sherlock production URL
        """
        # Use the sherlock base URL for checklist API
        checklist_base_url = base_url or "https://sherlock.therealbrokerage.com/api/v1"
        super().__init__(api_key=api_key, base_url=checklist_base_url)

    def get_checklist_item(self, checklist_item_id: str) -> Dict[str, Any]:
        """
        Get checklist item for given ID.

        Args:
            checklist_item_id: The checklist item ID

        Returns:
            Dict containing checklist item details

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}"
        return self.get(endpoint)

    def update_checklist_item(
        self, checklist_item_id: str, item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update checklist item for given checklist item ID.

        Args:
            checklist_item_id: The checklist item ID
            item_data: Item data including item details

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}"
        return self.put(endpoint, json_data=item_data)

    def delete_checklist_item(self, checklist_item_id: str) -> Dict[str, Any]:
        """
        Delete checklist item for given ID.

        Args:
            checklist_item_id: The checklist item ID

        Returns:
            Dict containing deletion status and message

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}"
        return self.delete(endpoint)

    def complete_checklist_item(
        self, checklist_item_id: str, is_complete: bool = True
    ) -> Dict[str, Any]:
        """
        Mark checklist item as complete or incomplete.

        Args:
            checklist_item_id: The checklist item ID
            is_complete: Whether to mark as complete (default: True)

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}/complete?isComplete={is_complete}"
        return self.put(endpoint)

    def get_checklist_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get document for the given ID.

        Args:
            document_id: The document ID

        Returns:
            Dict containing document details including versions

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/{document_id}"
        return self.get(endpoint)

    def update_checklist_document(
        self, document_id: str, document_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update current version for the given document ID.

        Args:
            document_id: The document ID
            document_data: Document data including versions and current version

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/{document_id}"
        return self.put(endpoint, json_data=document_data)

    def delete_checklist_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete the given document ID.

        Args:
            document_id: The document ID

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/{document_id}"
        return self.delete(endpoint)

    def create_checklist_item(
        self, checklist_id: str, item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create checklist item for given checklist ID.

        Args:
            checklist_id: The checklist ID
            item_data: Item data including item details

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_id}/items"
        return self.post(endpoint, json_data=item_data)

    def create_checklist(
        self, checklist_definition_id: str, checklist_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create checklist for given checklist definition ID.

        Args:
            checklist_definition_id: The checklist definition ID
            checklist_data: Checklist creation data including parent info and assignees

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_definition_id}"
        return self.post(endpoint, json_data=checklist_data)

    def add_document_to_checklist_item(
        self,
        checklist_item_id: str,
        name: str,
        description: str,
        uploader_id: str,
        transaction_id: str,
        file: Optional[BinaryIO] = None,
    ) -> Dict[str, Any]:
        """
        Add a new document to the given checklist item ID.

        Args:
            checklist_item_id: The checklist item ID
            name: Document name
            description: Document description
            uploader_id: ID of the user uploading the document
            transaction_id: Transaction ID
            file: File to upload (optional)

        Returns:
            Dict containing document details

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}/documents"

        data = {
            "name": name,
            "description": description,
            "uploaderId": uploader_id,
            "transactionId": transaction_id,
        }

        if file:
            files = {"file": file}
            return self._request("POST", endpoint, data=data, files=files)
        else:
            return self.post(endpoint, data=data)

    def add_document_version(
        self,
        checklist_document_id: str,
        name: str,
        description: str,
        uploader_id: str,
        transaction_id: str,
        file: Optional[BinaryIO] = None,
    ) -> Dict[str, Any]:
        """
        Add a new version for given document ID.

        Args:
            checklist_document_id: The checklist document ID
            name: Version name
            description: Version description
            uploader_id: ID of the user uploading the version
            transaction_id: Transaction ID
            file: File to upload (optional)

        Returns:
            Dict containing version details

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/{checklist_document_id}/versions"

        data = {
            "name": name,
            "description": description,
            "uploaderId": uploader_id,
            "transactionId": transaction_id,
        }

        if file:
            files = {"file": file}
            return self._request("POST", endpoint, data=data, files=files)
        else:
            return self.post(endpoint, data=data)

    def batch_update_checklists(
        self, batch_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update all checklists with the given IDs.

        Args:
            batch_items: List of items with checklistId and patch data

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "checklists/batch-update"
        data = {"items": batch_items}
        return self.post(endpoint, json_data=data)

    def get_checklist(self, checklist_id: str) -> Dict[str, Any]:
        """
        Get checklist for given ID.

        Args:
            checklist_id: The checklist ID

        Returns:
            Dict containing checklist details and items

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_id}"
        return self.get(endpoint)

    def get_checklists_progress(self, checklist_ids: List[str]) -> Dict[str, Any]:
        """
        Get checklists progress for given checklist IDs.

        Args:
            checklist_ids: List of checklist IDs

        Returns:
            Dict containing progress information (API returns array in 'data' field)

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "checklists/progress"
        params = {"checklistIds": checklist_ids}
        return self.get(endpoint, params=params)

    def download_document_version(self, version_id: str) -> Dict[str, Any]:
        """
        Get the download URL for a document version.

        Args:
            version_id: The version ID

        Returns:
            Dict containing the download URL (response will be processed by base client)

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/versions/{version_id}/download"
        return self.get(endpoint)

    # Legacy methods for backward compatibility
    def post_document_to_checklist(
        self,
        checklist_item_id: str,
        data: Dict[str, Any],
        file: Optional[BinaryIO] = None,
    ) -> Dict[str, Any]:
        """
        Upload document to checklist item (legacy method).

        Args:
            checklist_item_id: The checklist item ID to upload to
            data: Document metadata (e.g., document type, name, etc.)
            file: File to upload (optional)

        Returns:
            Dict containing upload response

        Raises:
            RezenError: If the API request fails
        """
        # Extract required fields from data for the new method
        name = data.get("name", "")
        description = data.get("description", "")
        uploader_id = data.get("uploaderId", "")
        transaction_id = data.get("transactionId", "")

        return self.add_document_to_checklist_item(
            checklist_item_id=checklist_item_id,
            name=name,
            description=description,
            uploader_id=uploader_id,
            transaction_id=transaction_id,
            file=file,
        )

    def mark_checklist_item_complete(
        self, checklist_id: str, checklist_item_id: str
    ) -> Dict[str, Any]:
        """
        Mark checklist item as complete (legacy method).

        Args:
            checklist_id: The checklist ID (not used in new API)
            checklist_item_id: The checklist item ID

        Returns:
            Dict containing updated checklist item

        Raises:
            RezenError: If the API request fails
        """
        return self.complete_checklist_item(checklist_item_id, is_complete=True)

    def delete_checklist_item_document(
        self, checklist_item_id: str, document_id: str
    ) -> Dict[str, Any]:
        """
        Delete document from checklist item (legacy method).

        Args:
            checklist_item_id: The checklist item ID (not used in new API)
            document_id: The document ID to delete

        Returns:
            Dict containing deletion response

        Raises:
            RezenError: If the API request fails
        """
        return self.delete_checklist_document(document_id)

    def get_checklist_templates(self) -> Dict[str, Any]:
        """
        Get available checklist templates (legacy method).

        Returns:
            Dict containing checklist templates

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "checklists/templates"
        return self.get(endpoint)

    def create_checklist_from_template(
        self, template_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new checklist from a template (legacy method).

        Args:
            template_id: The template ID to use
            data: Checklist creation data

        Returns:
            Dict containing created checklist

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/templates/{template_id}/create"
        return self.post(endpoint, json_data=data)

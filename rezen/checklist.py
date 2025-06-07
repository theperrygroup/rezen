"""ReZEN Checklist API client implementation."""

from typing import Any, BinaryIO, Dict, Optional

from .base_client import BaseClient


class ChecklistClient(BaseClient):
    """
    Client for ReZEN Checklist API endpoints.

    Provides access to checklist-related functionality including:
    - Getting checklist details
    - Uploading documents to checklist items
    - Managing checklist items
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """
        Initialize the Checklist API client.

        Args:
            api_key: ReZEN API key for authentication
            base_url: Base URL for the checklist API. Defaults to production URL
        """
        super().__init__(api_key=api_key, base_url=base_url)

    def get_checklist(self, checklist_id: str) -> Dict[str, Any]:
        """
        Get checklist details.

        Args:
            checklist_id: The checklist ID

        Returns:
            Dict containing checklist details

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_id}"
        return self.get(endpoint)

    def get_checklist_item(
        self, checklist_id: str, checklist_item_id: str
    ) -> Dict[str, Any]:
        """
        Get specific checklist item details.

        Args:
            checklist_id: The checklist ID
            checklist_item_id: The checklist item ID

        Returns:
            Dict containing checklist item details

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_id}/items/{checklist_item_id}"
        return self.get(endpoint)

    def post_document_to_checklist(
        self,
        checklist_item_id: str,
        data: Dict[str, Any],
        file: Optional[BinaryIO] = None,
    ) -> Dict[str, Any]:
        """
        Upload document to checklist item.

        Args:
            checklist_item_id: The checklist item ID to upload to
            data: Document metadata (e.g., document type, name, etc.)
            file: File to upload (optional)

        Returns:
            Dict containing upload response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/items/{checklist_item_id}/documents"

        if file:
            # If file is provided, use multipart/form-data
            files = {"file": file}
            return self._request("POST", endpoint, data=data, files=files)
        else:
            # Otherwise just send JSON data
            return self.post(endpoint, json_data=data)

    def update_checklist_item(
        self, checklist_id: str, checklist_item_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update checklist item.

        Args:
            checklist_id: The checklist ID
            checklist_item_id: The checklist item ID
            data: Updated checklist item data

        Returns:
            Dict containing updated checklist item

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_id}/items/{checklist_item_id}"
        return self.put(endpoint, json_data=data)

    def mark_checklist_item_complete(
        self, checklist_id: str, checklist_item_id: str
    ) -> Dict[str, Any]:
        """
        Mark checklist item as complete.

        Args:
            checklist_id: The checklist ID
            checklist_item_id: The checklist item ID

        Returns:
            Dict containing updated checklist item

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_id}/items/{checklist_item_id}/complete"
        return self.post(endpoint)

    def delete_checklist_item_document(
        self, checklist_item_id: str, document_id: str
    ) -> Dict[str, Any]:
        """
        Delete document from checklist item.

        Args:
            checklist_item_id: The checklist item ID
            document_id: The document ID to delete

        Returns:
            Dict containing deletion response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/items/{checklist_item_id}/documents/{document_id}"
        return self.delete(endpoint)

    def get_checklist_templates(self) -> Dict[str, Any]:
        """
        Get available checklist templates.

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
        Create a new checklist from a template.

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

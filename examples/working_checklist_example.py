#!/usr/bin/env python3
"""
Working example of ReZEN ChecklistClient usage.

This script demonstrates how to use the ChecklistClient to interact with
checklist-related API endpoints.

Requirements:
- Set REZEN_API_KEY environment variable
- Have appropriate permissions to access checklist endpoints
"""

import os

from rezen import ChecklistClient


def main() -> None:
    """Demonstrate ChecklistClient functionality."""
    # Initialize client (API key will be read from REZEN_API_KEY env var)
    client = ChecklistClient()

    print("🔧 ReZEN ChecklistClient Example")
    print("=" * 50)

    # Example checklist and item IDs (replace with real IDs)
    example_checklist_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    example_item_id = "4fa85f64-5717-4562-b3fc-2c963f66afa7"
    example_document_id = "5fa85f64-5717-4562-b3fc-2c963f66afa8"

    try:
        # Example 1: Get checklist information
        print("\n📋 Getting checklist information...")
        checklist = client.get_checklist(example_checklist_id)
        print(f"Checklist: {checklist.get('name', 'Unknown')}")
        print(f"Items count: {len(checklist.get('items', []))}")

        # Example 2: Get checklist item details
        print("\n📝 Getting checklist item details...")
        item = client.get_checklist_item(example_item_id)
        print(f"Item: {item.get('name', 'Unknown')}")
        print(f"Required: {item.get('required', False)}")
        print(f"Complete: {item.get('complete', False)}")

        # Example 3: Get checklist progress
        print("\n📊 Getting checklist progress...")
        progress = client.get_checklists_progress([example_checklist_id])
        if progress and isinstance(progress, dict):
            # The API returns the progress data, check if it contains a list or direct data
            progress_data = progress.get("data", progress)
            if isinstance(progress_data, list) and progress_data:
                first_progress = progress_data[0]
                completed = first_progress.get("completedCount", 0)
                total = first_progress.get("itemCount", 0)
                print(f"Progress: {completed}/{total} items completed")
            elif isinstance(progress_data, dict):
                completed = progress_data.get("completedCount", 0)
                total = progress_data.get("itemCount", 0)
                print(f"Progress: {completed}/{total} items completed")

        # Example 4: Mark item complete
        print("\n✅ Marking checklist item complete...")
        result = client.complete_checklist_item(example_item_id, is_complete=True)
        print(f"Mark complete result: {result.get('success', False)}")

        # Example 5: Create new checklist item
        print("\n➕ Creating new checklist item...")
        new_item_data = {
            "item": {
                "name": "Example New Item",
                "description": "This is a test item created via API",
                "required": True,
                "position": 999,
            }
        }
        create_result = client.create_checklist_item(
            example_checklist_id, new_item_data
        )
        print(f"Create item result: {create_result.get('success', False)}")

        # Example 6: Get document information
        print("\n📄 Getting document information...")
        document = client.get_checklist_document(example_document_id)
        print(f"Document: {document.get('name', 'Unknown')}")
        print(f"Versions: {len(document.get('versions', []))}")

        # Example 7: Batch update checklists
        print("\n🔄 Batch updating checklists...")
        batch_items = [
            {"checklistId": example_checklist_id, "patch": {"locked": False}}
        ]
        batch_result = client.batch_update_checklists(batch_items)
        print(f"Batch update result: {batch_result.get('success', False)}")

        # Example 8: Add document to checklist item
        print("\n📎 Adding document to checklist item...")
        doc_result = client.add_document_to_checklist_item(
            checklist_item_id=example_item_id,
            name="API Test Document",
            description="Document uploaded via API",
            uploader_id="test-user-id",
            transaction_id="test-transaction-id",
        )
        print(f"Add document result: {doc_result.get('id', 'No ID returned')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nNote: This example uses placeholder IDs.")
        print("Replace with real checklist/item/document IDs for actual testing.")


def demonstrate_legacy_methods() -> None:
    """Demonstrate legacy method compatibility."""
    client = ChecklistClient()

    print("\n🔄 Legacy Methods Compatibility")
    print("=" * 40)

    try:
        # Legacy document upload
        data = {
            "name": "Legacy Document",
            "description": "Uploaded via legacy method",
            "uploaderId": "test-user",
            "transactionId": "test-txn",
        }
        result = client.post_document_to_checklist("test-item-id", data)
        print(f"Legacy document upload: {result.get('success', False)}")

        # Legacy complete item
        result = client.mark_checklist_item_complete("test-checklist", "test-item")
        print(f"Legacy mark complete: {result.get('success', False)}")

        # Legacy templates
        templates = client.get_checklist_templates()
        print(f"Templates available: {len(templates.get('templates', []))}")

    except Exception as e:
        print(f"Legacy method error: {e}")


def show_api_info() -> None:
    """Show API endpoint information."""
    print("\n🌐 ChecklistClient API Endpoints")
    print("=" * 40)

    endpoints = [
        "GET /checklists/{checklistId}",
        "GET /checklists/checklist-items/{checklistItemId}",
        "PUT /checklists/checklist-items/{checklistItemId}",
        "DELETE /checklists/checklist-items/{checklistItemId}",
        "PUT /checklists/checklist-items/{checklistItemId}/complete",
        "GET /checklists/checklist-documents/{documentId}",
        "PUT /checklists/checklist-documents/{documentId}",
        "DELETE /checklists/checklist-documents/{documentId}",
        "POST /checklists/{checklistId}/items",
        "POST /checklists/{checklistDefinitionId}",
        "POST /checklists/checklist-items/{checklistItemId}/documents",
        "POST /checklists/checklist-documents/{documentId}/versions",
        "POST /checklists/batch-update",
        "GET /checklists/progress",
        "GET /checklists/checklist-documents/versions/{versionId}/download",
    ]

    for endpoint in endpoints:
        print(f"  • {endpoint}")

    print(f"\nBase URL: https://sherlock.therealbrokerage.com/api/v1")
    print(f"Total endpoints implemented: {len(endpoints)}")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("REZEN_API_KEY"):
        print("⚠️  REZEN_API_KEY environment variable not set!")
        print("Set it before running this example:")
        print("export REZEN_API_KEY=your_api_key_here")
        exit(1)

    # Run examples
    main()
    demonstrate_legacy_methods()
    show_api_info()

    print("\n✨ ChecklistClient example completed!")
    print("\nFor more information, check the documentation:")
    print("- rezen/checklist.py for method details")
    print("- tests/test_checklist.py for usage examples")
    print("- open_api/checklist_schema.json for API specification")

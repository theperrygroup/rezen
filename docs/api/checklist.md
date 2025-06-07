# Checklist API

Manage transaction checklists, checklist items, and document uploads.

---

## Overview

!!! abstract "Checklist API Features"

    - **Checklist Management**: Get and manage transaction checklists
    - **Item Tracking**: Monitor checklist item completion
    - **Document Upload**: Attach documents to checklist items
    - **Template Support**: Create checklists from templates

---

## Quick Start

```python
from rezen import RezenClient

client = RezenClient()

# Get checklist details
checklist = client.checklist.get_checklist("checklist-123")

# Upload document to checklist item
with open("document.pdf", "rb") as file:
    result = client.checklist.post_document_to_checklist(
        checklist_item_id="item-456",
        data={"document_type": "contract", "name": "Purchase Agreement"},
        file=file
    )

# Mark item as complete
client.checklist.mark_checklist_item_complete("checklist-123", "item-456")
```

---

## Core Methods

### Get Checklist

::: rezen.checklist.ChecklistClient.get_checklist
    options:
      show_source: false
      heading_level: 4

### Get Checklist Item

::: rezen.checklist.ChecklistClient.get_checklist_item
    options:
      show_source: false
      heading_level: 4

### Upload Document

::: rezen.checklist.ChecklistClient.post_document_to_checklist
    options:
      show_source: false
      heading_level: 4

!!! tip "Document Upload"
    The `post_document_to_checklist` method supports both file uploads and metadata-only submissions.

### Update Checklist Item

::: rezen.checklist.ChecklistClient.update_checklist_item
    options:
      show_source: false
      heading_level: 4

### Mark Item Complete

::: rezen.checklist.ChecklistClient.mark_checklist_item_complete
    options:
      show_source: false
      heading_level: 4

---

## Usage Examples

!!! example "Checklist Management"

    === "Get Checklist"

        ```python
        # Get full checklist with all items
        checklist = client.checklist.get_checklist("checklist-123")
        
        print(f"Checklist: {checklist['name']}")
        print(f"Total items: {len(checklist['items'])}")
        
        # Process checklist items
        for item in checklist['items']:
            print(f"- {item['name']}: {item['status']}")
        ```

    === "Upload Document"

        ```python
        # Upload document with metadata
        with open("inspection_report.pdf", "rb") as file:
            metadata = {
                "document_type": "inspection_report",
                "name": "Property Inspection Report",
                "description": "Complete inspection findings"
            }
            
            result = client.checklist.post_document_to_checklist(
                checklist_item_id="item-456",
                data=metadata,
                file=file
            )
            
            print(f"Document uploaded: {result['id']}")
        ```

    === "Complete Workflow"

        ```python
        # Complete checklist item workflow
        checklist_id = "checklist-123"
        item_id = "item-456"
        
        # 1. Get item details
        item = client.checklist.get_checklist_item(checklist_id, item_id)
        print(f"Item: {item['name']} - Status: {item['status']}")
        
        # 2. Upload required document
        with open("document.pdf", "rb") as file:
            client.checklist.post_document_to_checklist(
                checklist_item_id=item_id,
                data={"document_type": "contract"},
                file=file
            )
        
        # 3. Mark item as complete
        client.checklist.mark_checklist_item_complete(checklist_id, item_id)
        print("Item marked as complete")
        ```

---

## Document Management

!!! info "Document Operations"

    The checklist API supports various document operations:

    - **Upload**: Attach documents to checklist items
    - **Metadata**: Add document metadata without file upload
    - **Delete**: Remove documents from checklist items

!!! example "Document Operations"

    === "Upload with File"

        ```python
        # Upload document with file
        with open("contract.pdf", "rb") as file:
            result = client.checklist.post_document_to_checklist(
                checklist_item_id="item-789",
                data={
                    "document_type": "purchase_agreement",
                    "name": "Purchase Agreement",
                    "version": "1.0"
                },
                file=file
            )
        ```

    === "Metadata Only"

        ```python
        # Add document reference without file upload
        result = client.checklist.post_document_to_checklist(
            checklist_item_id="item-789",
            data={
                "document_type": "external_link",
                "name": "Property Listing",
                "url": "https://example.com/listing/123"
            }
        )
        ```

    === "Delete Document"

        ```python
        # Remove document from checklist item
        result = client.checklist.delete_checklist_item_document(
            checklist_item_id="item-789",
            document_id="doc-abc"
        )
        print("Document removed from checklist")
        ```

---

## Template Management

### Get Templates

::: rezen.checklist.ChecklistClient.get_checklist_templates
    options:
      show_source: false
      heading_level: 4

### Create from Template

::: rezen.checklist.ChecklistClient.create_checklist_from_template
    options:
      show_source: false
      heading_level: 4

!!! example "Using Templates"

    ```python
    # Get available templates
    templates = client.checklist.get_checklist_templates()
    
    for template in templates:
        print(f"Template: {template['name']} - {template['description']}")
    
    # Create checklist from template
    new_checklist = client.checklist.create_checklist_from_template(
        template_id="template-001",
        data={
            "transaction_id": "tx-12345",
            "name": "Purchase Transaction Checklist"
        }
    )
    
    print(f"Created checklist: {new_checklist['id']}")
    ```

---

## Complete Example

!!! example "Full Checklist Workflow"

    ```python
    from rezen import RezenClient
    from rezen.exceptions import RezenError
    
    def manage_transaction_checklist(transaction_id: str):
        """Complete checklist management workflow."""
        
        client = RezenClient()
        
        try:
            # Create checklist from template
            checklist = client.checklist.create_checklist_from_template(
                template_id="purchase-template",
                data={
                    "transaction_id": transaction_id,
                    "name": f"Checklist for Transaction {transaction_id}"
                }
            )
            
            checklist_id = checklist['id']
            print(f"Created checklist: {checklist_id}")
            
            # Process each checklist item
            items = client.checklist.get_checklist(checklist_id)['items']
            
            for item in items:
                print(f"\nProcessing: {item['name']}")
                
                # Upload required documents
                if item['requires_document']:
                    document_path = f"documents/{item['document_type']}.pdf"
                    
                    try:
                        with open(document_path, "rb") as file:
                            result = client.checklist.post_document_to_checklist(
                                checklist_item_id=item['id'],
                                data={
                                    "document_type": item['document_type'],
                                    "name": item['name']
                                },
                                file=file
                            )
                            print(f"  ✓ Uploaded document: {result['id']}")
                    except FileNotFoundError:
                        print(f"  ✗ Document not found: {document_path}")
                        continue
                
                # Mark item as complete
                client.checklist.mark_checklist_item_complete(
                    checklist_id,
                    item['id']
                )
                print(f"  ✓ Item completed")
            
            # Get final status
            final_checklist = client.checklist.get_checklist(checklist_id)
            completed_count = sum(
                1 for item in final_checklist['items'] 
                if item['status'] == 'COMPLETED'
            )
            
            print(f"\nChecklist Summary:")
            print(f"Total items: {len(final_checklist['items'])}")
            print(f"Completed: {completed_count}")
            print(f"Progress: {completed_count/len(final_checklist['items'])*100:.1f}%")
            
            return checklist_id
            
        except RezenError as e:
            print(f"Error managing checklist: {e}")
            return None
    
    # Run the example
    transaction_id = "tx-12345"
    checklist_id = manage_transaction_checklist(transaction_id)
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [:material-file-document: **Documents API**](documents.md)

    Manage documents and digital signatures

-   [:material-swap-horizontal: **Transactions API**](transactions.md)

    Work with transaction data

-   [:material-hammer-wrench: **Transaction Builder**](transaction-builder.md)

    Create new transactions with checklists

</div> 
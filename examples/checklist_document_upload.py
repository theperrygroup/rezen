#!/usr/bin/env python3
"""
Example: Upload a document to a checklist item.

This example demonstrates how to:
1. Get a transaction with a checklist
2. Find checklist items
3. Upload a document to a checklist item

Note: Transactions store their checklist ID in the 'checklistId' field (not a 'checklists' array).
Document uploads may require the agent to have Dropbox connected for storage.

Prerequisites:
- Transaction must have an associated checklist
- Checklist must have at least one item
- You need proper permissions to upload documents
"""

import os
from datetime import datetime
from io import BytesIO

from rezen import RezenClient
from rezen.exceptions import RezenError, ValidationError

# Try to import PDF generation library
try:
    from reportlab.lib.pagesizes import letter  # type: ignore
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer  # type: ignore
    from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("Note: Install reportlab for PDF generation: pip install reportlab")


def generate_document() -> BytesIO:
    """Generate a test document (PDF if reportlab available, otherwise text)."""
    if HAS_REPORTLAB:
        # Generate PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("ReZEN Document Upload Example", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated at: {datetime.now()}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("This document was uploaded via the ReZEN Python API.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    else:
        # Generate simple text file
        buffer = BytesIO()
        buffer.write(b"ReZEN Document Upload Example\n")
        buffer.write(f"Generated at: {datetime.now()}\n".encode())
        buffer.write(b"This document was uploaded via the ReZEN Python API.\n")
        buffer.seek(0)
        return buffer


def main() -> None:
    """Main example function."""
    client = RezenClient()
    
    # Transaction ID to work with
    # In a real application, you would get this from your system
    transaction_id = "cee51eff-a86f-4a62-a6dc-5de7a671c16e"  # Transaction with checklist
    
    try:
        # Get transaction details
        print(f"Getting transaction {transaction_id}...")
        transaction = client.transactions.get_transaction(transaction_id)
        
        # Check if transaction has a checklist ID
        checklist_id = transaction.get('checklistId')
        
        if not checklist_id:
            # Fallback: check for checklists array (legacy support)
            if transaction.get('checklists') and len(transaction['checklists']) > 0:
                checklist_id = transaction['checklists'][0].get('id')
            else:
                print("Transaction has no checklist.")
                print("You need to create a checklist first before uploading documents.")
                return
        
        print(f"Found checklist ID: {checklist_id}")
        
        # Get checklist details
        checklist = client.checklist.get_checklist(checklist_id)
        print(f"Retrieved checklist: {checklist.get('name', 'Unnamed')}")
        
        items = checklist.get('items', [])
        
        if not items:
            print("Checklist has no items to upload documents to.")
            return
        
        print(f"Checklist has {len(items)} items")
        
        # Find a suitable item for document upload
        # Prefer items that are:
        # 1. Of type DOCUMENT
        # 2. Not yet completed
        selected_item = None
        
        for item in items:
            if (item.get('type') == 'DOCUMENT' and 
                item.get('status') not in ['COMPLETED', 'COMPLETE']):
                selected_item = item
                break
                
        if not selected_item:
            # Fallback to first item
            selected_item = items[0]
        
        print(f"\nSelected checklist item:")
        print(f"  Name: {selected_item.get('name', 'Unnamed')}")
        print(f"  ID: {selected_item.get('id')}")
        print(f"  Type: {selected_item.get('type', 'N/A')}")
        print(f"  Status: {selected_item.get('status', 'N/A')}")
        
        # Get uploader ID
        # In a real application, this would be the current user's ID
        # For this example, we'll try to get it from the transaction
        uploader_id = None
        
        # Try to get current user
        try:
            current_user = client.users.get_current_user()
            uploader_id = current_user.get('id', current_user.get('yentaId'))
            print(f"\nUsing current user ID: {uploader_id}")
        except:
            # Fallback: try to get from transaction participants
            if 'participants' in transaction:
                for participant in transaction['participants']:
                    if participant.get('userId'):
                        uploader_id = participant['userId']
                        print(f"\nUsing participant ID: {uploader_id}")
                        break
                        
        if not uploader_id:
            print("\nError: Could not determine uploader ID")
            print("You need a valid user ID to upload documents")
            return
        
        # Generate document
        print("\nGenerating document...")
        document_buffer = generate_document()
        
        # Upload document
        print("Uploading document...")
        
        result = client.checklist.add_document_to_checklist_item(
            checklist_item_id=selected_item['id'],
            name="Example Document",
            description="Document uploaded via ReZEN Python API example",
            uploader_id=uploader_id,
            transaction_id=transaction_id,
            file=document_buffer
        )
        
        print("\n✅ Document uploaded successfully!")
        print(f"Document ID: {result.get('id')}")
        print(f"Document name: {result.get('name')}")
        print(f"Created at: {result.get('createdAt')}")
        
        # Optionally mark the checklist item as complete
        try:
            client.checklist.complete_checklist_item(
                checklist_item_id=selected_item['id'],
                is_complete=True
            )
            print("\n✅ Checklist item marked as complete!")
        except Exception as e:
            print(f"\nNote: Could not mark item as complete: {e}")
        
    except ValidationError as e:
        print(f"\nValidation error: {e}")
        print("\nCommon validation issues:")
        print("- Ensure all IDs are valid UUIDs")
        print("- Ensure the uploader has permission to upload")
        print("- Ensure the transaction is associated with the checklist")
        
    except RezenError as e:
        print(f"\nAPI error: {e}")
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main() 
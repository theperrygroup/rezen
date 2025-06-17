"""Upload MLS sheet to a transaction using the dropbox approach.

This example demonstrates the two-step process for uploading documents to checklist items:
1. Upload the file to the transaction's Dropbox
2. Link the uploaded file to the checklist item

Note: This approach is necessary for transactions that use Dropbox storage,
as opposed to the direct checklist upload method.
"""

import json
import os
from datetime import datetime

import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from rezen import RezenClient


def create_mls_pdf(filename: str = "mls_sheet.pdf") -> str:
    """Create a sample MLS sheet PDF."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height - 100, "MLS Listing Sheet")

    # MLS Number
    c.setFont("Helvetica", 14)
    c.drawString(100, height - 140, f"MLS #: MLS-{datetime.now().strftime('%Y%m%d')}")

    # Property Details
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 180, "Property Information")

    c.setFont("Helvetica", 12)
    y_position = height - 210
    details = [
        "Address: 123 Demo Street, Salt Lake City, UT 84101",
        "List Price: $550,000",
        "Bedrooms: 4",
        "Bathrooms: 3",
        "Square Feet: 2,500",
        "Year Built: 2020",
        "Lot Size: 0.25 acres",
    ]

    for detail in details:
        c.drawString(120, y_position, detail)
        y_position -= 25

    c.save()
    return filename


def upload_mls_sheet() -> None:
    """Upload MLS sheet to transaction f8028469-f484-4795-8247-81bb586386d5."""
    client = RezenClient()

    # Fixed transaction details
    transaction_id = "f8028469-f484-4795-8247-81bb586386d5"
    dropbox_id = "e6c20693-0ad9-482c-b155-bbf757f40722"
    checklist_item_id = "b0bce9b2-dfe9-4668-a1ae-7841a8929f3a"  # MLS Sheet item

    print(f"📋 Transaction: {transaction_id}")
    print(f"📁 Dropbox ID: {dropbox_id}")
    print(f"📄 MLS Sheet Item: {checklist_item_id}")

    # Get current user
    current_user = client.users.get_current_user()
    user_id = current_user["id"]
    print(f"👤 User ID: {user_id}\n")

    # Generate PDF
    print("📄 Generating MLS sheet PDF...")
    pdf_path = create_mls_pdf()
    print(f"✅ Created: {pdf_path}")

    try:
        # Step 1: Upload to Dropbox
        print("\n📤 Step 1: Uploading to Dropbox...")

        with open(pdf_path, "rb") as pdf_file:
            # Use the exact endpoint structure from the user's example
            dropbox_url = f"https://dropbox.therealbrokerage.com/api/v1/dropboxes/{dropbox_id}/files"

            # Get API key from one of the sub-clients
            api_key = client.transactions.api_key
            headers = {"Authorization": f"Bearer {api_key}"}

            # Match the exact payload structure shown
            files = {"file": ("MLS_Sheet.pdf", pdf_file, "application/pdf")}

            data = {"uploadedBy": user_id}

            print(f"   URL: {dropbox_url}")
            print(
                f"   Headers: Authorization Bearer ****{str(api_key)[-4:] if api_key else 'None'}"
            )
            print(f"   Data: {data}")

            response = requests.post(
                dropbox_url, headers=headers, files=files, data=data
            )

            print(f"\n   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")

            if response.status_code in [200, 201]:
                result = response.json()
                file_id = result["id"]
                filename = result["filename"]

                print("✅ File uploaded successfully!")
                print(f"   File ID: {file_id}")
                print(f"   Filename: {filename}")
                print(f"   Path: {result.get('path', 'N/A')}")

                # Step 2: Link file to checklist item
                print("\n📎 Step 2: Linking file to checklist item...")

                # Use the exact endpoint structure from the user's example
                link_url = f"https://sherlock.therealbrokerage.com/api/v1/checklists/checklist-items/{checklist_item_id}/file-references"

                # Match the exact payload structure shown
                link_payload = {
                    "references": [{"fileId": file_id, "filename": filename}]
                }

                link_response = requests.post(
                    link_url, headers=headers, json=link_payload
                )

                if link_response.status_code in [200, 201]:
                    print("✅ File successfully linked to MLS Sheet checklist item!")
                    if link_response.text:
                        print(f"   Response: {link_response.text}")
                else:
                    print(f"❌ Failed to link file: {link_response.status_code}")
                    print(f"   Response: {link_response.text}")

            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                print(
                    "\nNote: You may not have permission to upload to this transaction."
                )
                print("Make sure you are an agent or participant on the transaction.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    finally:
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print("\n🧹 Cleaned up temporary PDF file")


if __name__ == "__main__":
    upload_mls_sheet()

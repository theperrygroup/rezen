"""Example: Dropbox Integration with ReZEN API

This example demonstrates how to use the Dropbox integration
to manage files and folders for real estate transactions.
"""

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from rezen import RezenClient
from rezen.exceptions import NotFoundError, ValidationError

# Load environment variables
load_dotenv()


def demo_dropbox_oauth_flow(client: RezenClient) -> None:
    """Demonstrate the OAuth authentication flow."""
    print("\n=== Dropbox OAuth Flow Demo ===")

    try:
        # Step 1: Get authorization URL
        auth_response = client.dropbox.get_auth_url()
        auth_url = auth_response.get("url", "")

        print(f"✅ Authorization URL obtained:")
        print(f"   {auth_url}")
        print("\n   In a real application, you would:")
        print("   1. Redirect the user to this URL")
        print("   2. User authorizes access in Dropbox")
        print("   3. Dropbox redirects back with an authorization code")
        print("   4. Use that code to complete the authentication")

        # Note: In a real app, you'd get the code from the OAuth callback
        # For demo purposes, we'll show how to save the token
        print("\n   Example of saving token (not executed in demo):")
        print("   client.dropbox.save_token(code='auth_code_from_callback')")

    except Exception as e:
        print(f"❌ Error getting auth URL: {e}")


def demo_folder_operations(client: RezenClient, agent_id: str) -> None:
    """Demonstrate folder listing and creation."""
    print(f"\n=== Folder Operations Demo (Agent: {agent_id}) ===")

    try:
        # List folders (this will fail if agent hasn't authorized Dropbox)
        print("\n📁 Attempting to list folders...")
        try:
            folders = client.dropbox.get_folders(agent_id)
            print(f"✅ Found {len(folders)} folders:")
            for folder in folders[:5]:  # Show first 5
                print(
                    f"   - {folder.get('name', 'Unknown')} at {folder.get('path', '')}"
                )
            if len(folders) > 5:
                print(f"   ... and {len(folders) - 5} more")
        except (NotFoundError, ValidationError) as e:
            print(f"⚠️  Could not list folders: {e}")
            print("   (This is normal if the agent hasn't connected Dropbox)")

        # Demonstrate folder creation
        print("\n📁 Folder creation example:")
        transaction_id = f"TX-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        folder_path = f"/Transactions/{transaction_id}"

        print(f"   Would create folder: {folder_path}")
        print("   Code: client.dropbox.create_folder(agent_id, folder_path)")

        # Show folder structure creation
        print("\n📁 Transaction folder structure example:")
        base_path = f"/Transactions/{transaction_id}"
        folder_paths = [
            base_path,
            f"{base_path}/Contracts",
            f"{base_path}/Disclosures",
            f"{base_path}/Inspections",
            f"{base_path}/Financials",
            f"{base_path}/Correspondence",
        ]

        print("   Standard transaction folders:")
        for folder_path in folder_paths:
            print(f"   - {folder_path}")

    except Exception as e:
        print(f"❌ Error in folder operations: {e}")


def demo_file_upload(client: RezenClient, agent_id: str) -> None:
    """Demonstrate file upload functionality."""
    print(f"\n=== File Upload Demo (Agent: {agent_id}) ===")

    # Create a sample file for demo
    sample_file = Path("sample_document.txt")
    sample_content = f"""ReZEN Dropbox Integration Demo
Generated: {datetime.now().isoformat()}

This is a sample document that would be uploaded to Dropbox.
In a real application, this could be:
- Purchase agreements
- Inspection reports
- Disclosure documents
- Financial statements
"""

    try:
        # Write sample file
        sample_file.write_text(sample_content)
        print(f"✅ Created sample file: {sample_file}")

        # Show upload code
        dropbox_path = f"/Transactions/Demo/{sample_file.name}"
        print(f"\n📤 File upload example:")
        print(f"   Local file: {sample_file}")
        print(f"   Dropbox path: {dropbox_path}")
        print("\n   Code to upload:")
        print(
            f"""   with open('{sample_file}', 'rb') as f:
       client.dropbox.upload_file(agent_id, f, '{dropbox_path}')"""
        )

        # Show batch upload example
        print("\n📤 Batch upload example:")
        documents = {
            "Purchase_Agreement.pdf": "/Transactions/TX-2024-001/Contracts/",
            "Property_Disclosure.pdf": "/Transactions/TX-2024-001/Disclosures/",
            "Inspection_Report.pdf": "/Transactions/TX-2024-001/Inspections/",
            "Loan_Approval.pdf": "/Transactions/TX-2024-001/Financials/",
        }

        print("   Documents to upload:")
        for doc, path in documents.items():
            print(f"   - {doc} → {path}")

    finally:
        # Clean up sample file
        if sample_file.exists():
            sample_file.unlink()
            print(f"\n🧹 Cleaned up sample file")


def demo_transaction_workflow(client: RezenClient) -> None:
    """Demonstrate a complete transaction document workflow."""
    print("\n=== Complete Transaction Workflow Example ===")

    transaction_id = "TX-2024-DEMO"
    property_address = "123 Main St, Anytown, USA"
    agent_id = "agent-uuid-here"

    print(f"\n🏠 Transaction: {transaction_id}")
    print(f"📍 Property: {property_address}")

    # Show the complete workflow
    print("\n📋 Complete workflow steps:")
    print("1. Check if agent has Dropbox connected")
    print("2. Create transaction folder structure")
    print("3. Upload initial documents")
    print("4. Add documents as transaction progresses")
    print("5. Organize by transaction stage")

    # Show code structure
    print("\n💻 Implementation example:")
    print(
        """
def setup_transaction_dropbox(client, agent_id, transaction_id):
    # Create base folder
    base_path = f"/Transactions/{transaction_id}"
    
    # Create folder structure
    folders = [
        f"{base_path}/01-Listing",
        f"{base_path}/02-Offers", 
        f"{base_path}/03-Contracts",
        f"{base_path}/04-Inspections",
        f"{base_path}/05-Closing"
    ]
    
    for folder in folders:
        try:
            client.dropbox.create_folder(agent_id, folder)
        except ValidationError:
            pass  # Folder already exists
    
    return base_path
"""
    )


def main() -> None:
    """Run the Dropbox integration demo."""
    print("🚀 ReZEN Dropbox Integration Demo")
    print("=" * 50)

    # Initialize client
    api_key = os.getenv("REZEN_API_KEY")
    if not api_key:
        print("❌ Please set REZEN_API_KEY environment variable")
        return

    client = RezenClient(api_key=api_key)
    print("✅ ReZEN client initialized")

    # Use a demo agent ID (in real use, you'd get this from your system)
    demo_agent_id = "550e8400-e29b-41d4-a716-446655440000"

    # Run demos
    demo_dropbox_oauth_flow(client)
    demo_folder_operations(client, demo_agent_id)
    demo_file_upload(client, demo_agent_id)
    demo_transaction_workflow(client)

    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\nNext steps:")
    print("1. Implement OAuth flow in your application")
    print("2. Connect agent Dropbox accounts")
    print("3. Integrate with your transaction workflow")
    print("4. Set up automated document organization")


if __name__ == "__main__":
    main()

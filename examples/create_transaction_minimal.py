"""Minimal example for creating a complete transaction in ReZEN.

This example shows the absolute minimum required steps to create a transaction.
All steps are REQUIRED - skipping any will cause submission to fail.
"""
from rezen import RezenClient
from datetime import datetime, timedelta

def create_minimal_transaction() -> str:
    """Create a transaction with minimal required fields.
    
    Returns:
        str: The created transaction ID
    """
    client = RezenClient()
    
    # Step 1: Create transaction
    transaction_id = client.transaction_builder.create_transaction_builder()["id"]
    
    # Step 2: Add location (ALL fields required)
    client.transaction_builder.update_location_info(transaction_id, {
        "street": "123 Main St",
        "city": "Salt Lake City", 
        "state": "UTAH",  # Must be ALL CAPS
        "zip": "84101",
        "county": "Salt Lake",    # REQUIRED
        "yearBuilt": 2020,       # REQUIRED
        "mlsNumber": "MLS123"    # REQUIRED
    })
    
    # Step 3: Add price/date with BOTH commissions (use helper method)
    price_data = client.transaction_builder.prepare_price_and_date_data(
        sale_price=500000,
        representation_type="BUYER",
        acceptance_date=datetime.now().strftime("%Y-%m-%d"),
        closing_date=(datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
    )
    client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
    
    # Step 4: Add buyer
    client.transaction_builder.add_buyer(transaction_id, {
        "firstName": "John",
        "lastName": "Buyer",
        "email": "buyer@example.com",
        "phoneNumber": "1(555) 123-4567"  # Country code required!
    })
    
    # Step 5: Add seller (REQUIRED even for buyer representation!)
    client.transaction_builder.add_seller(transaction_id, {
        "firstName": "Jane",
        "lastName": "Seller",
        "email": "seller@example.com",
        "phoneNumber": "1(555) 987-6543"  # Country code required!
    })
    
    # Step 6: Add owner agent (uses convenience method)
    client.transaction_builder.set_current_user_as_owner_agent(
        transaction_id,
        "BUYERS_AGENT"  # Must match representationType
    )
    
    # Step 7: Get participant IDs for commission splits
    transaction = client.transaction_builder.get_transaction_builder(transaction_id)
    participant_id = transaction["agentsInfo"]["ownerAgent"][0]["id"]
    
    # Step 8: Add commission splits
    client.transaction_builder.update_commission_splits(transaction_id, [{
        "participantId": participant_id,
        "commission": {
            "commissionPercent": 100.0,
            "percentEnabled": True,
            "negativeOrEmpty": False
        }
    }])
    
    # Step 9: Add commission payer (title company)
    client.transaction_builder.add_commission_payer(transaction_id, {
        "role": "TITLE",
        "firstName": "ABC",
        "lastName": "Title",
        "email": "title@example.com",
        "phoneNumber": "1(555) 555-5555",
        "companyName": "ABC Title Company",
        "receivesInvoice": True
    })
    
    # Step 10: Submit transaction
    client.transaction_builder.submit_transaction(transaction_id)
    
    print(f"✅ Transaction created successfully: {transaction_id}")
    return str(transaction_id)

if __name__ == "__main__":
    transaction_id = create_minimal_transaction()
    print(f"\nTransaction ID saved for future use: {transaction_id}")
    # Latest created transaction ID: 582dc74b-e68d-4d30-bb13-bfcfdc5025ff 
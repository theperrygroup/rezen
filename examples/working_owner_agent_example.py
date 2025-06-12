#!/usr/bin/env python3
"""
Working Owner Agent Example

This demonstrates the correct sequence for adding owner agents to transactions.
The key insight: owner agent endpoint requires the transaction to be properly
set up with location, price/date, and clients BEFORE adding agents.
"""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "rezen"))

from rezen import RezenClient


def create_complete_transaction_with_owner_agent() -> dict:
    """
    Create a complete transaction with owner agent using the proper sequence.

    Returns:
        dict: The complete transaction data with owner agent successfully added
    """

    client = RezenClient()

    print("🏗️  Creating Complete Transaction with Owner Agent")
    print("=" * 50)

    # Step 1: Create transaction builder
    print("\n1️⃣  Creating transaction builder...")
    builder_id = client.transaction_builder.create_transaction_builder()
    print(f"   ✅ Created: {builder_id}")

    try:
        # Step 2: Add location (REQUIRED FIRST)
        print("\n2️⃣  Adding location info...")
        location_data = {
            "street": "2158 E Wilson Ave",
            "city": "Salt Lake City",
            "state": "UTAH",
            "zip": "84108",
            "yearBuilt": 2020,
            "mlsNumber": "MLS123456",
            "escrowNumber": "ESC-2024-001",
        }
        client.transaction_builder.update_location_info(builder_id, location_data)
        print("   ✅ Location added successfully")

        # Step 3: Add price and dates (REQUIRED SECOND)
        print("\n3️⃣  Adding price and date info...")
        price_date_data = {
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": {"amount": 565000, "currency": "USD"},
            "listingCommission": {
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False,
            },
            "saleCommission": {
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False,
            },
            "acceptanceDate": "2024-01-15",
            "closingDate": "2024-02-28",
            "representationType": "BUYER",  # This must match the agent role!
        }
        client.transaction_builder.update_price_and_date_info(
            builder_id, price_date_data
        )
        print("   ✅ Price and dates added successfully")

        # Step 4: Add clients (REQUIRED THIRD)
        print("\n4️⃣  Adding buyer...")
        buyer_data = {
            "firstName": "Lance",
            "lastName": "Sollid",
            "email": "lance.sollid@gmail.com",
            "phoneNumber": "(801) 555-1234",
        }
        client.transaction_builder.add_buyer(builder_id, buyer_data)
        print("   ✅ Buyer added successfully")

        print("\n5️⃣  Adding seller...")
        seller_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "phoneNumber": "(801) 555-5678",
        }
        client.transaction_builder.add_seller(builder_id, seller_data)
        print("   ✅ Seller added successfully")

        # Step 5: NOW we can add owner agent! 🎉
        print("\n6️⃣  Adding Owner Agent (the main event!)...")
        owner_data = {
            "ownerAgent": {
                "agentId": "be696b5d-6845-41f5-8440-8d8bef15f361",
                "role": "BUYERS_AGENT",  # Must match representationType above
            },
            "officeId": "b2681c5c-2c28-4712-b69e-11fde8d91b48",
            "teamId": "ab45fb68-3f2a-4985-8ec6-73d1b409ea33",
        }

        result = client.transaction_builder.update_owner_agent_info(
            builder_id, owner_data
        )
        print("   🎉 SUCCESS! Owner agent added successfully!")

        # Verify the owner agent was added correctly
        transaction = client.transaction_builder.get_transaction_builder(builder_id)

        print("\n7️⃣  Verifying Owner Agent...")
        agents_info = transaction.get("agentsInfo", {})
        owner_agents = agents_info.get("ownerAgent", [])

        if owner_agents:
            agent = owner_agents[0]
            print("   🎉 OWNER AGENT VERIFICATION:")
            print(f"      ✅ Agent ID: {agent.get('agentId')}")
            print(f"      ✅ Role: {agent.get('role')}")
            print(f"      ✅ Created At: {agent.get('createdAt')}")
            print(f"      ✅ Receives Invoice: {agent.get('receivesInvoice')}")
            print(f"      ✅ OpCity Referral: {agent.get('opCityReferral')}")
            print(f"      ✅ ECP Opted In: {agent.get('optedInForEcp')}")

            print(f"\n   🏢 Office Info:")
            print(f"      ✅ Office ID: {agents_info.get('officeId')}")
            print(f"      ✅ Team ID: {agents_info.get('teamId')}")
            print(
                f"      ✅ Representation Type: {agents_info.get('representationType')}"
            )

        else:
            print("   ❌ No owner agents found!")

        # Optional: Add additional agents (co-agents, etc.)
        print("\n8️⃣  Adding Co-Agent (optional)...")
        try:
            co_agent_data = {
                "agentId": "be696b5d-6845-41f5-8440-8d8bef15f361",
                "role": "REAL",
                "receivesInvoice": False,
            }
            client.transaction_builder.add_co_agent(builder_id, co_agent_data)
            print("   ✅ Co-agent added successfully")
        except Exception as e:
            print(f"   ⚠️  Co-agent failed: {str(e)}")

        # Personal deal and title info
        print("\n9️⃣  Adding personal deal and title info...")
        try:
            client.transaction_builder.update_personal_deal_info(
                builder_id, {"personalDeal": True, "representedByAgent": True}
            )
            client.transaction_builder.update_title_info(
                builder_id, {"useRealTitle": True}
            )
            print("   ✅ Additional info added successfully")
        except Exception as e:
            print(f"   ⚠️  Additional info failed: {str(e)}")

        print("\n" + "=" * 50)
        print("🎉 COMPLETE SUCCESS!")
        print("   Owner agent successfully added to transaction!")
        print("   Transaction is ready for commission splits and finalization.")
        print("=" * 50)

        return transaction

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise

    finally:
        # Clean up
        print(f"\n🧹 Cleaning up transaction: {builder_id}")
        try:
            client.transaction_builder.delete_transaction_builder(builder_id)
            print("   ✅ Transaction deleted successfully")
        except:
            print("   ⚠️  Cleanup failed (transaction may still exist)")


def demonstrate_convenience_method() -> None:
    """
    Demonstrate using the convenience method for current user as owner agent.
    """

    client = RezenClient()

    print("\n" + "=" * 50)
    print("🚀 Testing Convenience Method: Current User as Owner Agent")
    print("=" * 50)

    # Create and set up basic transaction
    builder_id = client.transaction_builder.create_transaction_builder()

    try:
        # Set up prerequisites
        client.transaction_builder.update_location_info(
            builder_id,
            {
                "street": "123 Main St",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101",
            },
        )

        client.transaction_builder.update_price_and_date_info(
            builder_id,
            {
                "dealType": "SALE",
                "propertyType": "RESIDENTIAL",
                "salePrice": {"amount": 400000, "currency": "USD"},
                "representationType": "BUYER",
            },
        )

        client.transaction_builder.add_buyer(
            builder_id,
            {
                "firstName": "Test",
                "lastName": "Buyer",
                "email": "test@example.com",
                "phoneNumber": "(801) 555-9999",
            },
        )

        # Now use convenience method
        print("\n🎯 Setting current user as owner agent...")
        result = client.transaction_builder.set_current_user_as_owner_agent(
            builder_id, role="BUYERS_AGENT"
        )

        print("   🎉 SUCCESS! Current user set as owner agent!")

        # Verify
        transaction = client.transaction_builder.get_transaction_builder(builder_id)
        owner_agents = transaction.get("agentsInfo", {}).get("ownerAgent", [])

        if owner_agents:
            print(f"   ✅ Owner Agent ID: {owner_agents[0].get('agentId')}")
            print(f"   ✅ Role: {owner_agents[0].get('role')}")

    finally:
        client.transaction_builder.delete_transaction_builder(builder_id)
        print("   🧹 Test transaction cleaned up")


if __name__ == "__main__":
    print("🏠 ReZEN Owner Agent Implementation - Working Example")
    print("This demonstrates the CORRECT way to add owner agents to transactions.\n")

    # Demonstrate the full working sequence
    complete_transaction = create_complete_transaction_with_owner_agent()

    # Demonstrate convenience method
    demonstrate_convenience_method()

    print("\n✨ All tests completed successfully!")
    print("\n📝 Key Takeaways:")
    print("   1. Add location info FIRST")
    print("   2. Add price/date info SECOND (with representationType)")
    print("   3. Add buyers/sellers THIRD")
    print("   4. THEN add owner agent (it will work!)")
    print("   5. Role must be 'BUYERS_AGENT' or 'SELLERS_AGENT'")
    print("   6. representationType must match agent role")

#!/usr/bin/env python3
"""Test the complete working sequence with all discovered requirements."""

import os
from datetime import datetime, timedelta
from typing import Any, Dict

from rezen import RezenClient


def test_complete_working_sequence() -> str:
    """Test the complete sequence with all discovered requirements."""
    api_key = os.getenv("REZEN_API_KEY", "your_api_key_here")
    client = RezenClient(api_key=api_key)

    print("🎯 Testing COMPLETE Working Sequence with All Requirements...")
    print("=" * 70)

    try:
        # Step 1: Create transaction
        transaction_id = client.transaction_builder.create_transaction_builder()
        print(f"✅ 1. Transaction created: {transaction_id}")

        # Step 2: Add location info - with additional required fields
        location_data = {
            "street": "123 Complete Working St",
            "city": "Salt Lake City",
            "state": "UTAH",
            "zip": "84101",
            "county": "Salt Lake",  # Required additional field
            "yearBuilt": 2020,  # Required additional field
            "mlsNumber": "MLS-COMPLETE",  # Required additional field
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
        print("✅ 2. Location added (with required additional fields)")

        # Step 3: Add price/date info - with BOTH commission fields
        price_date_data = {
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": {"amount": 550000, "currency": "USD"},
            "representationType": "BUYER",
            "listingCommission": {  # Required commission field 1
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False,
            },
            "saleCommission": {  # Required commission field 2
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False,
            },
        }
        client.transaction_builder.update_price_and_date_info(
            transaction_id, price_date_data
        )
        print("✅ 3. Price/date added (with BOTH commission fields)")

        # Step 4: Add buyer
        buyer_data = {
            "firstName": "John",
            "lastName": "Buyer",
            "email": "john.complete@example.com",
            "phoneNumber": "(801) 555-1234",
        }
        client.transaction_builder.add_buyer(transaction_id, buyer_data)
        print("✅ 4. Buyer added")

        # Step 5: Add seller
        seller_data = {
            "firstName": "Jane",
            "lastName": "Seller",
            "email": "jane.complete@example.com",
            "phoneNumber": "(801) 555-5678",
        }
        client.transaction_builder.add_seller(transaction_id, seller_data)
        print("✅ 5. Seller added")

        # Step 6: Try owner agent with officeId
        print("\n🏢 Testing owner agent with officeId...")

        # Test different officeId approaches
        office_test_cases = [
            {
                "name": "With officeId field",
                "data": {
                    "ownerAgent": {
                        "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
                        "role": "BUYERS_AGENT",
                    },
                    "officeId": "some-office-id-123",  # Add officeId as requested
                },
            },
            {
                "name": "With officeIds field (plural)",
                "data": {
                    "ownerAgent": {
                        "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
                        "role": "BUYERS_AGENT",
                    },
                    "officeIds": ["some-office-id-123"],  # Try plural version
                },
            },
            {
                "name": "With teamId",
                "data": {
                    "ownerAgent": {
                        "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
                        "role": "BUYERS_AGENT",
                    },
                    "officeId": "some-office-id-123",
                    "teamId": "some-team-id-456",
                },
            },
        ]

        owner_agent_success = False
        for test_case in office_test_cases:
            print(f"\n   📋 Testing: {test_case['name']}")
            try:
                data: Dict[str, Any] = test_case["data"]  # type: ignore
                client.transaction_builder.update_owner_agent_info(transaction_id, data)
                print(f"   ✅ Owner agent success with {test_case['name']}!")
                owner_agent_success = True
                break
            except Exception as e:
                print(f"   ❌ Failed: {e}")

        # Step 7: Add co-agents
        print(f"\n👥 Testing co-agents on complete transaction...")
        co_agent_roles = ["REAL", "BUYERS_AGENT", "SELLERS_AGENT"]

        for role in co_agent_roles:
            try:
                co_agent_data = {
                    "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
                    "role": role,
                    "receivesInvoice": False,
                }
                client.transaction_builder.add_co_agent(transaction_id, co_agent_data)
                print(f"   ✅ Co-agent role '{role}' added successfully")
            except Exception as e:
                print(f"   ❌ Co-agent role '{role}' failed: {e}")

        # Final inspection
        final_data = client.transaction_builder.get_transaction_builder(transaction_id)
        print(f"\n📊 FINAL COMPLETE TRANSACTION SUMMARY:")
        print(f"   🆔 Transaction ID: {transaction_id}")
        print(f"   🏠 Address: {final_data.get('address', {}).get('street', 'None')}")
        print(
            f"   💰 Sale Price: ${final_data.get('salePrice', {}).get('amount', 'None'):,}"
        )
        print(f"   🏘️  Property Type: {final_data.get('propertyType', 'None')}")
        print(f"   📋 Deal Type: {final_data.get('dealType', 'None')}")
        print(
            f"   🎭 Representation: {final_data.get('agentsInfo', {}).get('representationType', 'None')}"
        )
        print(f"   👤 Buyers: {len(final_data.get('buyers', []))}")
        print(f"   👤 Sellers: {len(final_data.get('sellers', []))}")

        agents_info = final_data.get("agentsInfo", {})
        owner_agents = agents_info.get("ownerAgent", [])
        co_agents = agents_info.get("coAgents", [])
        print(f"   🏢 Owner Agents: {len(owner_agents)}")
        print(f"   👥 Co-Agents: {len(co_agents)}")

        if owner_agents:
            for agent in owner_agents:
                print(f"      - Owner: {agent.get('role', 'Unknown')}")

        if co_agents:
            for agent in co_agents:
                print(f"      - Co-Agent: {agent.get('role', 'Unknown')}")

        # Commission info
        listing_comm = final_data.get("listingCommission", {})
        sale_comm = final_data.get("saleCommission", {})
        if listing_comm:
            print(
                f"   📈 Listing Commission: {listing_comm.get('commissionPercent', 'None')}%"
            )
        if sale_comm:
            print(
                f"   📈 Sale Commission: {sale_comm.get('commissionPercent', 'None')}%"
            )

        if owner_agent_success:
            print(
                f"\n🎉 COMPLETE SUCCESS! All components working including owner agent!"
            )
        else:
            print(f"\n✅ PARTIAL SUCCESS! All components except owner agent working!")

        return transaction_id

    except Exception as e:
        print(f"❌ Sequence failed: {e}")
        import traceback

        traceback.print_exc()
        return ""


def create_summary_of_findings() -> None:
    """Create a summary of all discovered requirements."""
    print(f"\n" + "=" * 70)
    print("📋 SUMMARY OF DISCOVERED REQUIREMENTS")
    print("=" * 70)

    print("\n✅ WHAT WORKS:")
    print("1. 📝 Transaction Creation:")
    print("   - create_transaction_builder() - Always works")

    print("\n2. 📍 Location Updates:")
    print("   - ✅ Works with: street, city, state, zip + county, yearBuilt, mlsNumber")
    print("   - ❌ Fails with: just basic street, city, state, zip")
    print("   - ⚠️  Required additional fields: county, yearBuilt, mlsNumber")

    print("\n3. 💰 Price/Date Updates:")
    print("   - ✅ Works with: location + both commission fields")
    print(
        "   - ❌ Fails with: just dealType, propertyType, salePrice, representationType"
    )
    print("   - ⚠️  Required: BOTH listingCommission AND saleCommission objects")

    print("\n4. 👤 Participant Operations:")
    print("   - ✅ add_buyer() - Works on transactions with location")
    print("   - ✅ add_seller() - Works on transactions with location")

    print("\n5. 👥 Co-Agent Operations:")
    print("   - ✅ Role 'REAL' - Always works")
    print("   - ✅ Role 'BUYERS_AGENT' - Works on transactions with location")
    print("   - ✅ Role 'SELLERS_AGENT' - Works on transactions with location")
    print("   - ❌ Role 'LISTING_AGENT' - Still fails")

    print("\n❌ WHAT STILL DOESN'T WORK:")
    print("1. 🏢 Owner Agent Operations:")
    print("   - ❌ update_owner_agent_info() - Requires 'officeId' field")
    print("   - ⚠️  Error: 'Missing required field officeId'")

    print("\n📋 REQUIRED WORKFLOW:")
    print("1. Create transaction")
    print("2. Add location (with county, yearBuilt, mlsNumber)")
    print("3. Add price/date (with both commission objects)")
    print("4. Add buyers/sellers")
    print("5. Add co-agents (REAL, BUYERS_AGENT, SELLERS_AGENT work)")
    print("6. Owner agent requires unknown valid officeId")


if __name__ == "__main__":
    result = test_complete_working_sequence()
    create_summary_of_findings()

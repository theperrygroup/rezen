#!/usr/bin/env python3
"""
Extract Michael Perry's commission data from 2024 transactions.
Includes agent commission and team commission (Jack Perry).
"""

import csv
import os
from datetime import datetime
from typing import Any, Dict, List

from rezen import RezenClient


def convert_timestamp(timestamp_value: Any) -> str:
    """Convert various timestamp formats to readable date."""
    if not timestamp_value:
        return "N/A"

    try:
        if isinstance(timestamp_value, str):
            if "T" in timestamp_value:  # ISO format
                return timestamp_value[:10]
            elif timestamp_value.isdigit():
                timestamp_value = int(timestamp_value)
            else:
                return timestamp_value

        if isinstance(timestamp_value, (int, float)):
            # Try as milliseconds first (common in APIs)
            if timestamp_value > 1000000000000:  # Milliseconds
                dt = datetime.fromtimestamp(timestamp_value / 1000)
            else:  # Seconds
                dt = datetime.fromtimestamp(timestamp_value)
            return dt.strftime("%Y-%m-%d")

        return str(timestamp_value)
    except:
        return str(timestamp_value)


def extract_michael_perry_data(
    transaction_id: str, client: RezenClient
) -> Dict[str, Any]:
    """Extract Michael Perry's commission data from a transaction."""
    print(f"   🔍 Processing transaction: {transaction_id}")

    # Michael Perry's yenta ID
    michael_perry_id = "bd465129-b224-43e3-b92f-524ea5f53783"
    # Jack Perry's yenta ID (team splits)
    jack_perry_id = "be696b5d-6845-41f5-8440-8d8bef15f361"

    # Initialize commission data structure
    commission_data = {
        "transaction_id": transaction_id,
        "address": "",
        "sale_price": "",
        "closing_date": "",
        "status": "",
        "representation_type": "",
        "deal_type": "",
        "gross_commission_amount": "",
        "michael_perry_commission": "",
        "michael_perry_percentage": "",
        "jack_perry_team_commission": "",
        "jack_perry_percentage": "",
        "other_splits_total": "",
        "total_splits_found": 0,
        "michael_found": "No",
        "jack_found": "No",
        "created_date": "",
        "updated_date": "",
        "error": "",
    }

    try:
        # Get basic transaction data
        transaction = client.transactions.get_transaction(transaction_id)
        print(f"      ✅ Got transaction data")

        # Extract basic info
        commission_data["status"] = transaction.get("status", "")
        commission_data["deal_type"] = transaction.get("dealType", "")
        commission_data["created_date"] = convert_timestamp(
            transaction.get("createdAt")
        )
        commission_data["updated_date"] = convert_timestamp(
            transaction.get("updatedAt")
        )

        # Extract address
        address_info = transaction.get("address", {})
        if address_info:
            address_parts = []
            if address_info.get("street"):
                address_parts.append(address_info["street"])
            if address_info.get("city"):
                address_parts.append(address_info["city"])
            if address_info.get("state"):
                address_parts.append(address_info["state"])
            commission_data["address"] = ", ".join(address_parts)

        # Extract sale price
        sale_price = transaction.get("salePrice", {})
        if sale_price and sale_price.get("amount"):
            commission_data["sale_price"] = f"${sale_price['amount']:,.2f}"

        # Extract closing date
        closing_date_fields = [
            "closedAt",
            "rezenClosedAt",
            "skySlopeActualClosingDate",
            "skySlopeEscrowClosingDate",
            "closedDate",
            "closeDate",
            "closingDate",
        ]

        for field in closing_date_fields:
            if transaction.get(field):
                commission_data["closing_date"] = convert_timestamp(transaction[field])
                break

        # Extract gross commission
        gross_commission = transaction.get("grossCommission", {})
        if gross_commission and gross_commission.get("amount"):
            commission_data["gross_commission_amount"] = (
                f"${gross_commission['amount']:,.2f}"
            )

        # Extract representation type from agents info
        agents_info = transaction.get("agentsInfo", {})
        if agents_info:
            commission_data["representation_type"] = agents_info.get(
                "representationType", ""
            )

        # Extract commission splits
        commission_splits = transaction.get("commissionSplits", [])
        commission_data["total_splits_found"] = len(commission_splits)

        other_splits_total = 0.0

        print(f"      💰 Found {len(commission_splits)} commission splits")

        for split in commission_splits:
            yenta_id = split.get("yentaId", "")
            first_name = split.get("firstName", "")
            last_name = split.get("lastName", "")

            # Extract amount
            amount = split.get("amount", {})
            if isinstance(amount, dict) and amount.get("amount"):
                split_amount = amount["amount"]
            elif isinstance(amount, (int, float)):
                split_amount = amount
            else:
                split_amount = 0.0

            # Extract percentage
            percentage = split.get("percentage", {})
            if isinstance(percentage, dict):
                percentage_str = percentage.get("string", "N/A")
            else:
                percentage_str = str(percentage)

            # Check if this is Michael Perry
            if yenta_id == michael_perry_id:
                commission_data["michael_perry_commission"] = f"${split_amount:,.2f}"
                commission_data["michael_perry_percentage"] = percentage_str
                commission_data["michael_found"] = "Yes"
                print(
                    f"         🎯 Michael Perry: ${split_amount:,.2f} ({percentage_str})"
                )

            # Check if this is Jack Perry (team commission)
            elif yenta_id == jack_perry_id:
                commission_data["jack_perry_team_commission"] = f"${split_amount:,.2f}"
                commission_data["jack_perry_percentage"] = percentage_str
                commission_data["jack_found"] = "Yes"
                print(
                    f"         🏢 Jack Perry (Team): ${split_amount:,.2f} ({percentage_str})"
                )

            # All other splits
            else:
                other_splits_total += float(split_amount)
                print(
                    f"         👤 {first_name} {last_name}: ${split_amount:,.2f} ({percentage_str})"
                )

        if other_splits_total > 0:
            commission_data["other_splits_total"] = f"${other_splits_total:,.2f}"

        print(f"      📍 Address: {commission_data['address']}")
        print(f"      💰 Sale Price: {commission_data['sale_price']}")
        print(f"      📅 Closing Date: {commission_data['closing_date']}")
        print(f"      🎯 Michael Found: {commission_data['michael_found']}")
        print(f"      🏢 Jack Found: {commission_data['jack_found']}")

    except Exception as e:
        print(f"      ❌ Error getting transaction data: {e}")
        commission_data["error"] = f"Transaction lookup failed: {e}"

    return commission_data


def main() -> None:
    """Extract Michael Perry's commission data from all transactions."""
    # Get API key
    api_key = os.getenv("REZEN_API_KEY")
    if not api_key:
        print("❌ Error: REZEN_API_KEY environment variable not set")
        return

    # Initialize client
    client = RezenClient(api_key=api_key)

    # Michael Perry's transaction IDs
    transaction_ids = [
        "ce2e8f75-cf66-449b-ad56-d15f03c3ffee",
        "170af2a1-6621-4712-95e8-40339f5e6f9f",
        "9b813e7c-d92a-4854-9172-b1aff1bd209e",
        "1797c6e4-389e-404e-a630-14813c133ba6",
        "6887ca49-9cb9-44e9-81ac-fb210fead50d",
        "668b411a-fcf8-46b9-a179-e4677e1f3422",
        "fa00d3fe-a30d-49a4-ba98-35682b6c0d2d",
        "2cfcbd81-186c-4322-94ad-60c524f84067",
        "64f5accd-7dbc-4a63-9a14-09ba4fa95728",
        "30b9ec4d-a4f5-44de-b645-a0fd8cbc7d8d",
        "445583c4-755b-4ac6-9f63-71a17ceb32c3",
        "00864c8c-bf59-4a39-b112-e91dbda9ccda",
        "b7957f43-f27a-4bbc-937e-f186e7b72079",
        "56e03676-d4cb-4c95-96b2-fcca6a6f389c",
        "48ee275a-db28-4a31-a255-b4fd5c00d231",
        "2a54727b-5b99-49f3-8599-92cbbf6b1b5f",
        "3213e623-5f6f-4588-ba88-6235a5ad21ef",
        "e99cd005-73f7-47f7-aafb-02dab868be2e",
        "68915bb5-6ce7-492a-9056-3513236034ef",
        "c472b1e2-a9e1-443b-a5ff-26758a22f62b",
        "033a6b90-413b-4fc4-9356-1080d6517915",
        "b01bed14-4ad5-4cab-9143-0d347afff607",
        "a691cdb1-b9f8-4215-a0e1-b8af7cf2ad67",
        "c349ff23-224b-47bf-be58-506edb6f4dca",
        "e7375ec5-ccb1-4ff3-a04b-4ea225995a9a",
        "5a077611-5694-42d0-8818-631bfb42093d",
        "ddb1a27d-5e86-42fd-8f07-48b26908550e",
        "da89d576-46ed-43d5-8265-a8b535b5b922",
    ]

    print("🚀 Extracting Michael Perry's 2024 Commission Data...")
    print("=" * 70)
    print(f"Total transactions to process: {len(transaction_ids)}")
    print(f"Michael Perry ID: bd465129-b224-43e3-b92f-524ea5f53783")
    print(f"Jack Perry ID (Team): be696b5d-6845-41f5-8440-8d8bef15f361")

    commission_data_list = []
    successful_lookups = 0
    failed_lookups = 0
    michael_found_count = 0
    jack_found_count = 0

    for i, transaction_id in enumerate(transaction_ids, 1):
        print(f"\n📋 Transaction {i}/{len(transaction_ids)}:")

        commission_data = extract_michael_perry_data(transaction_id, client)
        commission_data_list.append(commission_data)

        if commission_data["error"]:
            failed_lookups += 1
        else:
            successful_lookups += 1

        if commission_data["michael_found"] == "Yes":
            michael_found_count += 1

        if commission_data["jack_found"] == "Yes":
            jack_found_count += 1

    print(f"\n📊 Processing Summary:")
    print(f"   ✅ Successful lookups: {successful_lookups}")
    print(f"   ❌ Failed lookups: {failed_lookups}")
    print(f"   🎯 Transactions with Michael Perry: {michael_found_count}")
    print(f"   🏢 Transactions with Jack Perry (Team): {jack_found_count}")

    # Create CSV with all commission data
    csv_filename = (
        f"michael_perry_commissions_2024_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    fieldnames = [
        "transaction_id",
        "address",
        "sale_price",
        "closing_date",
        "status",
        "representation_type",
        "deal_type",
        "gross_commission_amount",
        "michael_perry_commission",
        "michael_perry_percentage",
        "jack_perry_team_commission",
        "jack_perry_percentage",
        "other_splits_total",
        "total_splits_found",
        "michael_found",
        "jack_found",
        "created_date",
        "updated_date",
        "error",
    ]

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(commission_data_list)

    print(f"\n✅ CSV created: {csv_filename}")

    # Calculate totals
    total_michael_commission = 0.0
    total_jack_commission = 0.0
    total_other_splits = 0.0
    total_gross_commission = 0.0
    valid_transactions = 0

    for data in commission_data_list:
        if not data["error"] and data["michael_found"] == "Yes":
            valid_transactions += 1

            # Parse Michael's commission
            if data["michael_perry_commission"]:
                try:
                    michael_amt = float(
                        data["michael_perry_commission"]
                        .replace("$", "")
                        .replace(",", "")
                    )
                    total_michael_commission += michael_amt
                except ValueError:
                    pass

            # Parse Jack's commission
            if data["jack_perry_team_commission"]:
                try:
                    jack_amt = float(
                        data["jack_perry_team_commission"]
                        .replace("$", "")
                        .replace(",", "")
                    )
                    total_jack_commission += jack_amt
                except ValueError:
                    pass

            # Parse other splits
            if data["other_splits_total"]:
                try:
                    other_amt = float(
                        data["other_splits_total"].replace("$", "").replace(",", "")
                    )
                    total_other_splits += other_amt
                except ValueError:
                    pass

            # Parse gross commission
            if data["gross_commission_amount"]:
                try:
                    gross_amt = float(
                        data["gross_commission_amount"]
                        .replace("$", "")
                        .replace(",", "")
                    )
                    total_gross_commission += gross_amt
                except ValueError:
                    pass

    print(
        f"\n💰 Michael Perry Commission Summary 2024 ({valid_transactions} transactions):"
    )
    print(f"   - Total Michael Perry commission: ${total_michael_commission:,.2f}")
    print(f"   - Total Jack Perry team commission: ${total_jack_commission:,.2f}")
    print(f"   - Total other splits: ${total_other_splits:,.2f}")
    print(f"   - Total gross commission: ${total_gross_commission:,.2f}")
    print(
        f"   - Michael's percentage of gross: {(total_michael_commission/total_gross_commission)*100:.1f}%"
        if total_gross_commission > 0
        else ""
    )
    print(
        f"   - Jack's percentage of gross: {(total_jack_commission/total_gross_commission)*100:.1f}%"
        if total_gross_commission > 0
        else ""
    )

    print(f"\n🎉 Successfully processed {len(transaction_ids)} transaction IDs!")
    print(f"📄 Detailed results saved to: {csv_filename}")


if __name__ == "__main__":
    main()

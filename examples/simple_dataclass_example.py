#!/usr/bin/env python3
"""Simple example of ReZEN API dataclasses.

This example demonstrates the basic usage of dataclasses for type-safe
interactions with the ReZEN API.
"""

import sys
from pathlib import Path

# Add the rezen package to the path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from decimal import Decimal
from uuid import uuid4

from rezen.models import (
    Address,
    Agent,
    AgentStatus,
    Commission,
    Country,
    Money,
    StateOrProvince,
)


def main() -> None:
    """Main function demonstrating basic dataclass usage."""

    print("ReZEN API Dataclasses Example")
    print("=" * 40)

    # Example 1: Creating an Address
    print("\n1. Address Example:")
    address = Address(
        street="123 Main Street",
        city="Los Angeles",
        state=StateOrProvince.CALIFORNIA,
        zip="90210",
    )
    print(f"   {address.street}, {address.city}, {address.state.value} {address.zip}")

    # Example 2: Creating Money and Commission
    print("\n2. Money and Commission Example:")
    money = Money(amount=Decimal("5000.00"))
    commission = Commission(commission_amount=money, commission_percent=3.0)
    print(
        f"   Commission: ${commission.commission_amount.amount} ({commission.commission_percent}%)"
    )

    # Example 3: Creating an Agent
    print("\n3. Agent Example:")
    agent = Agent(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email_address="john.doe@example.com",
        agent_status=AgentStatus.ACTIVE,
        agent_account_country=Country.UNITED_STATES,
    )
    print(f"   Agent: {agent.first_name} {agent.last_name}")
    print(f"   Email: {agent.email_address}")
    print(f"   Status: {agent.agent_status.value}")

    # Example 4: Type safety with enums
    print("\n4. Enum Type Safety:")
    if agent.agent_status == AgentStatus.ACTIVE:
        print("   ✓ Agent is active!")

    print(f"   Available statuses: {[status.value for status in AgentStatus]}")

    # Example 5: Default values
    print("\n5. Default Values:")
    print(f"   Agent type (default): {agent.type}")
    print(f"   Opted into SMS (default): {agent.opted_into_sms}")
    print(f"   Address country (default): {address.country.value}")

    print("\n" + "=" * 40)
    print("Example completed successfully!")
    print("Dataclasses provide type safety and better developer experience.")


if __name__ == "__main__":
    main()

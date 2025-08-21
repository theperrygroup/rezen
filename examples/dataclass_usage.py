"""Example usage of ReZEN API dataclasses.

This example demonstrates how to use the new dataclasses for type-safe
API interactions with the ReZEN library.
"""

from decimal import Decimal
from uuid import uuid4

from rezen import Address, Agent, Commission, Money, Team, TeamConfig
from rezen.models import AgentStatus, Country, StateOrProvince, TeamStatus, TeamType


def main() -> None:
    """Main function demonstrating dataclass usage."""

    # Example 1: Creating an Address with type safety
    print("=== Address Example ===")

    address = Address(
        street="123 Main Street",
        city="Los Angeles",
        state=StateOrProvince.CALIFORNIA,
        zip="90210",
        country=Country.UNITED_STATES,
        street2="Suite 100",
    )

    print(
        f"Address: {address.street}, {address.city}, {address.state.value} {address.zip}"
    )
    print(f"Country: {address.country.value}")
    print(
        f"Complete address: {address.street}, {address.street2}, {address.city}, {address.state.value} {address.zip}"
    )

    # Example 2: Creating Money and Commission objects
    print("\n=== Money and Commission Example ===")

    commission_amount = Money(amount=Decimal("5000.00"), currency="USD")

    commission = Commission(
        commission_amount=commission_amount,
        commission_percent=3.0,
        percent_enabled=True,
    )

    print(
        f"Commission Amount: ${commission.commission_amount.amount} {commission.commission_amount.currency}"
    )
    print(f"Commission Percentage: {commission.commission_percent}%")
    print(f"Percentage Enabled: {commission.percent_enabled}")

    # Example 3: Creating an Agent with comprehensive data
    print("\n=== Agent Example ===")

    agent = Agent(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email_address="john.doe@realestate.com",
        agent_status=AgentStatus.ACTIVE,
        agent_account_country=Country.UNITED_STATES,
        phone_number="555-123-4567",
        title="Senior Real Estate Agent",
        company="Elite Realty Group",
    )

    print(f"Agent: {agent.first_name} {agent.last_name}")
    print(f"Email: {agent.email_address}")
    print(f"Status: {agent.agent_status.value}")
    print(f"Country: {agent.agent_account_country.value}")
    print(f"Phone: {agent.phone_number}")
    print(f"Title: {agent.title}")
    print(f"Company: {agent.company}")

    # Example 4: Working with optional fields and defaults
    print("\n=== Optional Fields and Defaults Example ===")

    # Create agent with minimal required fields
    minimal_agent = Agent(
        id=uuid4(),
        first_name="Jane",
        last_name="Smith",
        email_address="jane.smith@realestate.com",
        agent_status=AgentStatus.CANDIDATE,
        agent_account_country=Country.CANADA,
    )

    print(f"Minimal Agent: {minimal_agent.first_name} {minimal_agent.last_name}")
    print(f"Type (default): {minimal_agent.type}")
    print(f"Created At (optional): {minimal_agent.created_at}")
    print(f"Divisions (default empty list): {minimal_agent.divisions}")
    print(f"Opted into SMS (default): {minimal_agent.opted_into_sms}")

    # Example 5: Type safety with enums
    print("\n=== Enum Type Safety Example ===")

    # This demonstrates how enums provide type safety
    active_statuses = [AgentStatus.ACTIVE, AgentStatus.RESURRECTING]
    inactive_statuses = [
        AgentStatus.INACTIVE,
        AgentStatus.REJECTED,
        AgentStatus.CANDIDATE,
    ]

    print("Active Agent Statuses:")
    for status in active_statuses:
        print(f"  - {status.value}")

    print("Inactive Agent Statuses:")
    for status in inactive_statuses:
        print(f"  - {status.value}")

    # Check agent status
    if agent.agent_status in active_statuses:
        print(f"Agent {agent.first_name} is currently active!")

    # Example 6: Accessing nested dataclass properties
    print("\n=== Nested Dataclass Properties Example ===")

    # Demonstrate how nested objects work
    print(f"Commission Currency: {commission.commission_amount.currency}")
    print(f"Commission Value: {commission.commission_amount.amount}")

    # Example 7: Converting dataclasses to dictionaries (for API serialization)
    print("\n=== Dataclass Serialization Example ===")

    from dataclasses import asdict

    # Convert to dictionary for API calls or JSON serialization
    address_dict = asdict(address)
    print("Address as dictionary:")
    for key, value in address_dict.items():
        if value is not None:
            print(f"  {key}: {value}")

    # Example 8: Creating objects from API responses
    print("\n=== Creating Objects from API Data Example ===")

    # Simulate API response data
    api_response_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "first_name": "Alice",
        "last_name": "Johnson",
        "email_address": "alice.johnson@realestate.com",
        "agent_status": "ACTIVE",
        "agent_account_country": "UNITED_STATES",
        "phone_number": "555-987-6543",
        "type": "AGENT",
        "opted_into_sms": True,
    }

    # Create agent from API data (you would need to handle UUID conversion in real usage)
    print("Creating agent from API response:")
    print(f"  Name: {api_response_data['first_name']} {api_response_data['last_name']}")
    print(f"  Status: {api_response_data['agent_status']}")
    print(f"  Phone: {api_response_data['phone_number']}")

    print("\n=== Example Complete ===")
    print(
        "The dataclasses provide type safety, IDE autocompletion, and better developer experience!"
    )


if __name__ == "__main__":
    main()

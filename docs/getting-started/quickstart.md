# Quick Start Guide

Get up and running with the ReZEN API in a few minutes. This guide focuses on the current client signatures and a minimal, truthful first workflow.

## Goal

By the end of this guide, you will have:

- configured authentication
- created a client
- run a team search
- run an agent search
- created a transaction builder and captured its ID

## Prerequisites

- Python 3.8 or newer
- A ReZEN API key

## Step 1: Install and Authenticate

```bash
python -m pip install rezen
export REZEN_API_KEY="your_api_key_here"
```

If you prefer a `.env` file, see the [Installation Guide](installation.md) and [Authentication Guide](authentication.md).

## Step 2: Create a Client

```python
from rezen import RezenClient

client: RezenClient = RezenClient()
print("ReZEN client initialized")
```

## Step 3: Search for Teams

`search_teams()` returns a paginated response object, so read from its `content` list.

```python
from typing import Any, Dict, List

from rezen import RezenClient

client: RezenClient = RezenClient()
team_results: Dict[str, Any] = client.teams.search_teams(
    status="ACTIVE",
    page_size=5,
)
teams: List[Dict[str, Any]] = team_results.get("content", [])

for team in teams:
    print(f"{team.get('name', 'Unknown team')} ({team.get('id', 'no-id')})")
```

## Step 4: Search for Agents

`search_active_agents()` also returns a paginated response object.

```python
from typing import Any, Dict, List

from rezen import RezenClient

client: RezenClient = RezenClient()
agent_results: Dict[str, Any] = client.agents.search_active_agents(
    name="John",
    page_size=3,
)
agents: List[Dict[str, Any]] = agent_results.get("content", [])

for agent in agents:
    print(f"{agent.get('firstName', '')} {agent.get('lastName', '')}".strip())
```

## Step 5: Create a Transaction Builder

`create_transaction_builder()` creates an empty builder. Save the returned ID for later calls.

```python
from typing import Any, Dict

from rezen import RezenClient

client: RezenClient = RezenClient()
builder_response: Dict[str, Any] = client.transaction_builder.create_transaction_builder()
transaction_id: str = builder_response["id"]

print(f"Created transaction builder: {transaction_id}")
```

Creating a usable transaction requires follow-up calls such as `update_location_info()` and `update_price_and_date_info()`. For the full sequence, continue to the [Transaction Workflows Guide](../guides/transactions.md).

## Error Handling

```python
from typing import Any, Dict

from rezen import RezenClient
from rezen.exceptions import AuthenticationError, RezenError, ValidationError

client: RezenClient = RezenClient()

try:
    results: Dict[str, Any] = client.teams.search_teams(page_size=1)
    print(results.get("content", []))
except AuthenticationError as exc:
    print(f"Authentication failed: {exc}")
except ValidationError as exc:
    print(f"Invalid request: {exc}")
except RezenError as exc:
    print(f"ReZEN API error: {exc}")
```

## Next Steps

- [Installation Guide](installation.md)
- [Authentication Guide](authentication.md)
- [Transaction Workflows Guide](../guides/transactions.md)
- [Examples](../guides/examples.md)
- [API Reference](../api/index.md)

# ReZEN Python Client

[![PyPI version](https://badge.fury.io/py/rezen.svg)](https://badge.fury.io/py/rezen)
[![Python support](https://img.shields.io/pypi/pyversions/rezen.svg)](https://pypi.org/project/rezen/)
[![License](https://img.shields.io/github/license/your-org/rezen-python-client.svg)](https://github.com/your-org/rezen-python-client/blob/main/LICENSE)
[![Coverage](https://img.shields.io/codecov/c/github/your-org/rezen-python-client.svg)](https://codecov.io/gh/your-org/rezen-python-client)

The **official Python client** for the ReZEN Real Estate API. Build powerful real estate applications with comprehensive transaction management, agent networking, and team operations.

## 🚀 Quick Start

Get up and running in 60 seconds:

```bash
pip install rezen
```

```python
from rezen import RezenClient

# Initialize client
client = RezenClient()

# Search for teams
teams = client.teams.search_teams(status="ACTIVE")

# Create a transaction
response = client.transaction_builder.create_transaction_builder()
transaction_id = response['id']

# Add property details
client.transaction_builder.update_location_info(transaction_id, {
    "address": "123 Main Street",
    "city": "Anytown",
    "state": "CA",
    "zipCode": "90210"
})
```

**[→ Get Started](quickstart.md)**{ .md-button .md-button--primary }
**[→ API Reference](api-reference.md)**{ .md-button }

---

## ✨ Features

<div class="grid cards" markdown>

-   :material-home: **Transaction Management**

    ---

    Complete transaction lifecycle management from creation to closing, with support for all participant types and financial operations.

    [:octicons-arrow-right-24: Learn more](api-reference.md#transaction-builder-api)

-   :material-account-group: **Agent & Team Operations**

    ---

    Comprehensive agent search, network hierarchy management, and team operations with advanced filtering capabilities.

    [:octicons-arrow-right-24: Learn more](api-reference.md#agents-api)

-   :material-cog: **Type-Safe & Robust**

    ---

    Complete type hints, comprehensive error handling, and 100% test coverage for production-ready applications.

    [:octicons-arrow-right-24: Learn more](contributing.md#testing-guidelines)

-   :material-book-open: **Well Documented**

    ---

    Extensive documentation with real-world examples, troubleshooting guides, and comprehensive API reference.

    [:octicons-arrow-right-24: Learn more](examples.md)

</div>

---

## 🎯 Use Cases

### Real Estate Transaction Processing

Build applications that handle the complete real estate transaction lifecycle:

- **Property listings** and transaction creation
- **Participant management** (buyers, sellers, agents, service providers)
- **Financial operations** (commissions, payments, escrow)
- **Document management** and reporting

### Agent Network Management

Manage complex agent networks and hierarchies:

- **Agent discovery** and search capabilities
- **Network analysis** with sponsor trees and downlines
- **Team management** and assignments
- **Performance tracking** and analytics

### Integration & Automation

Integrate ReZEN with your existing systems:

- **CRM integrations** for customer management
- **Accounting systems** for financial tracking
- **Document management** for transaction records
- **Workflow automation** for process optimization

---

## 📊 API Coverage

| **API Section** | **Endpoints** | **Status** |
|-----------------|---------------|------------|
| Transaction Builder | 60+ endpoints | ✅ Complete |
| Transactions | 50+ endpoints | ✅ Complete |
| Agents | 35+ endpoints | ✅ Complete |
| Teams | 10+ endpoints | ✅ Complete |
| **Total** | **150+ endpoints** | **✅ Complete** |

---

## 🏗️ Architecture

The ReZEN Python client is built with modern Python best practices:

```mermaid
graph TB
    A[RezenClient] --> B[TransactionBuilderClient]
    A --> C[TransactionsClient]
    A --> D[TeamsClient]
    A --> E[AgentsClient]
    
    B --> F[BaseClient]
    C --> F
    D --> F
    E --> F
    
    F --> G[HTTP Session]
    F --> H[Error Handling]
    F --> I[Authentication]
    
    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style G fill:#e8f5e8
    style H fill:#fff3e0
    style I fill:#fce4ec
```

### Key Design Principles

- **🎯 Simple Interface**: Intuitive method names and clear parameter structures
- **🔒 Type Safety**: Complete type hints for excellent IDE support
- **⚡ Performance**: Efficient HTTP session management and connection pooling
- **🛡️ Reliability**: Comprehensive error handling and retry mechanisms
- **📚 Extensible**: Clean architecture for easy customization and extension

---

## 💡 Examples

### Create a Complete Transaction

```python
from rezen import RezenClient
from datetime import datetime, timedelta

client = RezenClient()

# Create transaction builder
response = client.transaction_builder.create_transaction_builder()
transaction_id = response['id']

# Add property details
client.transaction_builder.update_location_info(transaction_id, {
    "address": "1234 Elm Street",
    "city": "San Francisco",
    "state": "CA",
    "zipCode": "94102"
})

# Set pricing and timeline
closing_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
client.transaction_builder.update_price_and_date_info(transaction_id, {
    "purchase_price": 850000,
    "closing_date": closing_date
})

# Add participants
client.transaction_builder.add_buyer(transaction_id, {
    "first_name": "Alice",
    "last_name": "Johnson",
    "email": "alice@email.com"
})

# Submit for processing
client.transaction_builder.submit_transaction(transaction_id)
```

### Agent Network Analysis

```python
# Find agents in California
agents = client.agents.search_active_agents(
    state_or_province=["CALIFORNIA"],
    page_size=50
)

# Analyze agent's network
for agent in agents[:5]:
    agent_id = agent['id']
    
    # Get network statistics
    network_stats = client.agents.get_network_size_by_tier(agent_id)
    front_line = client.agents.get_front_line_agents_info(agent_id)
    
    print(f"Agent {agent['first_name']} {agent['last_name']}:")
    print(f"  Network tiers: {len(network_stats)}")
    print(f"  Front line agents: {len(front_line)}")
```

**[→ More Examples](examples.md)**

---

## 🚦 Getting Started

### 1. Installation

Choose your installation method:

=== "pip"

    ```bash
    pip install rezen
    ```

=== "poetry"

    ```bash
    poetry add rezen
    ```

=== "conda"

    ```bash
    conda install -c conda-forge rezen
    ```

### 2. Authentication

Set up your API credentials:

=== "Environment Variable"

    ```bash
    export REZEN_API_KEY="your_api_key_here"
    ```

=== ".env File"

    ```bash
    # .env
    REZEN_API_KEY=your_api_key_here
    ```

=== "Direct"

    ```python
    client = RezenClient(api_key="your_api_key_here")
    ```

### 3. First API Call

```python
from rezen import RezenClient

client = RezenClient()
teams = client.teams.search_teams(status="ACTIVE", page_size=10)
print(f"Found {len(teams)} active teams")
```

**[→ Complete Installation Guide](installation.md)**

---

## 📖 Documentation

<div class="grid cards" markdown>

-   **[🚀 Quick Start](quickstart.md)**

    5-minute guide to get up and running

-   **[📚 API Reference](api-reference.md)**

    Complete API documentation with examples

-   **[💡 Examples](examples.md)**

    Real-world usage patterns and best practices

-   **[🔧 Troubleshooting](troubleshooting.md)**

    Common issues and debugging techniques

-   **[🤝 Contributing](contributing.md)**

    Help improve the ReZEN Python client

-   **[📋 Changelog](changelog.md)**

    Version history and release notes

</div>

---

## 🆘 Support

### Community & Help

- **📖 Documentation**: Comprehensive guides and API reference
- **💬 GitHub Issues**: Bug reports and feature requests
- **📧 Email Support**: [support@rezen.com](mailto:support@rezen.com)
- **🌐 Website**: [rezen.com](https://rezen.com)

### Status & Monitoring

- **🔍 API Status**: [status.rezen.com](https://status.rezen.com)
- **📊 PyPI Package**: [pypi.org/project/rezen](https://pypi.org/project/rezen/)
- **🐙 GitHub Repo**: [github.com/your-org/rezen-python-client](https://github.com/your-org/rezen-python-client)

---

## 📄 License

The ReZEN Python client is released under the [MIT License](https://github.com/your-org/rezen-python-client/blob/main/LICENSE).

---

**Ready to build powerful real estate applications?** **[Get Started →](quickstart.md)** 
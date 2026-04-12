# ReZEN Python Client

[![PyPI version](https://badge.fury.io/py/rezen.svg)](https://badge.fury.io/py/rezen)
[![Python support](https://img.shields.io/pypi/pyversions/rezen.svg)](https://pypi.org/project/rezen/)
[![License](https://img.shields.io/github/license/theperrygroup/rezen.svg)](https://github.com/theperrygroup/rezen/blob/main/LICENSE)
[![Coverage](https://img.shields.io/codecov/c/github/theperrygroup/rezen.svg)](https://codecov.io/gh/theperrygroup/rezen)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://theperrygroup.github.io/rezen)

> **The official Python client for the ReZEN Real Estate API**

Build powerful real estate applications with comprehensive transaction management, agent networking, and team operations. Type-safe, production-ready, and extensively documented.

## 🚀 Quick Start

**Install:**
```bash
pip install rezen
```

**Use:**
```python
from rezen import RezenClient

# Initialize client (reads REZEN_API_KEY from environment)
client = RezenClient()

# Search for active teams
teams = client.teams.search_teams(status="ACTIVE")

# Create a transaction
response = client.transaction_builder.create_transaction_builder()
transaction_id = response['id']

# Add property details
client.transaction_builder.update_location_info(transaction_id, {
    "address": "123 Main Street",
    "city": "San Francisco",
    "state": "CA",
    "zipCode": "94102"
})
```

**[📖 Full Documentation](https://theperrygroup.github.io/rezen)** | **[🚀 Quick Start Guide](https://theperrygroup.github.io/rezen/getting-started/quickstart/)**

---

## ✨ Key Features

| **Feature** | **Description** |
|-------------|-----------------|
| 🏠 **Transaction Management** | Complete transaction lifecycle from creation to closing |
| 👥 **Agent & Team Operations** | Comprehensive search, network analysis, and team management |
| 🔒 **Type-Safe & Robust** | Full type hints, comprehensive error handling, 100% test coverage |
| 📚 **Well Documented** | Extensive docs with real-world examples and troubleshooting |
| ⚡ **Production Ready** | Battle-tested with retry logic, rate limiting, and connection pooling |

## 🎯 Use Cases

**Real Estate Transaction Processing**
- Property listings and transaction creation
- Participant management (buyers, sellers, agents, service providers)
- Financial operations (commissions, payments, escrow)
- Document management and reporting

**Agent Network Management**
- Agent discovery and search capabilities
- Network analysis with sponsor trees and downlines
- Team management and assignments
- Performance tracking and analytics

**System Integration**
- CRM integrations for customer management
- Accounting systems for financial tracking
- Workflow automation for process optimization

## 📊 API Coverage

| **API Section** | **Endpoints** | **Status** |
|-----------------|---------------|------------|
| Transaction Builder | 52 endpoints | ✅ Complete |
| Transactions | 49 endpoints | ✅ Complete |
| Agents | 36 endpoints | ✅ Complete |
| Teams | 2 endpoints | ✅ Complete |
| Directory | 16 endpoints | ✅ Complete |
| **Total** | **155 endpoints** | **✅ Complete** |

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or newer (CI-tested on Python 3.8 through 3.12)
- ReZEN API key

### Install the Package

**With pip:**
```bash
pip install rezen
```

**With poetry:**
```bash
poetry add rezen
```

### Configure Authentication

**Option 1: Environment Variable (Recommended)**
```bash
export REZEN_API_KEY="your_api_key_here"
```

**Option 2: Direct in Code**
```python
client = RezenClient(api_key="your_api_key_here")
```

**Option 3: .env File**
```bash
# .env
REZEN_API_KEY=your_api_key_here
```

## 💡 Examples

### Complete Transaction Workflow

```python
from datetime import datetime, timedelta
from rezen import RezenClient

client = RezenClient()

# Create transaction
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
from rezen import RezenClient

client = RezenClient()

# Find agents in California
agents = client.agents.search_active_agents(
    state_or_province=["CALIFORNIA"],
    page_size=50
)

# Analyze agent networks
for agent in agents[:5]:
    agent_id = agent['id']

    # Get network statistics
    network_stats = client.agents.get_network_size_by_tier(agent_id)
    front_line = client.agents.get_front_line_agents_info(agent_id)

    print(f"Agent {agent['first_name']} {agent['last_name']}:")
    print(f"  Network tiers: {len(network_stats)}")
    print(f"  Front line agents: {len(front_line)}")
```

### Directory Management

```python
from rezen import RezenClient

client = RezenClient()

# Search for vendors
vendors = client.directory.search_vendors(
    page_number=0,
    page_size=20,
    roles=["TITLE_ESCROW", "LENDER"]
)

# Create and link contacts
person_data = {
    "firstName": "Jane",
    "lastName": "Smith",
    "emailAddress": "jane@example.com",
    "phoneNumber": "555-0123"
}

person = client.directory.create_person(person_data)
client.directory.link_person(person['id'], {"vendorId": "vendor-123"})
```

**[📚 More Examples →](https://theperrygroup.github.io/rezen/guides/examples/)**

## 📖 Documentation

| Resource | Description |
|----------|-------------|
| **[📖 Full Documentation](https://theperrygroup.github.io/rezen)** | Complete documentation site |
| **[🚀 Quick Start](https://theperrygroup.github.io/rezen/getting-started/quickstart/)** | 5-minute setup guide |
| **[📋 API Reference](https://theperrygroup.github.io/rezen/api/)** | Complete API documentation |
| **[💡 Examples](https://theperrygroup.github.io/rezen/guides/examples/)** | Real-world usage patterns |
| **[🔧 Troubleshooting](https://theperrygroup.github.io/rezen/guides/troubleshooting/)** | Common issues and solutions |

## 🏗️ Architecture

The ReZEN Python client follows modern Python best practices:

```
RezenClient
├── TransactionBuilderClient  (52 endpoints)
├── TransactionsClient        (49 endpoints)
├── TeamsClient              (2 endpoints)
├── AgentsClient             (36 endpoints)
└── DirectoryClient          (16 endpoints)
```

**Design Principles:**
- 🎯 **Simple Interface**: Intuitive method names and clear parameters
- 🔒 **Type Safety**: Complete type hints for excellent IDE support
- ⚡ **Performance**: Efficient session management and connection pooling
- 🛡️ **Reliability**: Comprehensive error handling and retry mechanisms
- 📚 **Extensible**: Clean architecture for easy customization

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/theperrygroup/rezen.git
cd rezen

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install development dependencies
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

# Install docs dependencies if you plan to build the site locally
python -m pip install -r docs/requirements.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rezen --cov-report=html

# Run specific test file
pytest tests/test_teams.py -v
```

### Code Quality

```bash
# Match the default CI checks
black --check --diff --line-length=88 .
isort --check-only --diff --profile=black --line-length=88 .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
mypy rezen/ --strict --ignore-missing-imports
```

### Build Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation with the same strictness used for contributor checks
mkdocs build --strict
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://theperrygroup.github.io/rezen/development/contributing/) for workflow details and the repository [`STYLE_GUIDE.md`](https://github.com/theperrygroup/rezen/blob/main/STYLE_GUIDE.md) for code conventions.

**Quick Contribution Steps:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`pytest`)
5. Submit a pull request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Get Help
- **📖 Documentation**: [theperrygroup.github.io/rezen](https://theperrygroup.github.io/rezen)
- **💬 GitHub Issues**: [Report bugs or request features](https://github.com/theperrygroup/rezen/issues)
- **📧 Email**: [support@rezen.com](mailto:support@rezen.com)
- **🌐 Website**: [rezen.com](https://rezen.com)

### Status & Monitoring
- **🔍 API Status**: [status.rezen.com](https://status.rezen.com)
- **📦 PyPI Package**: [pypi.org/project/rezen](https://pypi.org/project/rezen/)

---

**Ready to build powerful real estate applications?** **[Get Started →](https://theperrygroup.github.io/rezen/getting-started/quickstart/)**

*Built with ❤️ by [The Perry Group](https://github.com/theperrygroup)*

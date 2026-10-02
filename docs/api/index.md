# API Reference

Complete method reference for the ReZEN Python API client. This section covers all available API endpoints, parameters, and return types.

---

## 🚀 API Overview

!!! success "✅ All APIs Operational"
    All ReZEN API endpoints are fully operational with real-time data access.

<div class="grid cards" markdown>

-   **Buyer Records**

    ---

    Create pre-contract buyer records, manage participants, and convert to builders

    [:octicons-arrow-right-24: Buyer Record API](buyer-records.md)

-   🔧 **Transaction Builder**

    ---

    Create and manage transaction builders with participants and properties

    [:octicons-arrow-right-24: Transaction Builder API](transaction-builder.md)

-   🤝 **Transactions**

    ---

    Work with live transactions, manage participants, and handle payments

    [:octicons-arrow-right-24: Transactions API](transactions.md)

-   👥 **Teams**

    ---

    Search and manage team information with comprehensive filtering

    [:octicons-arrow-right-24: Teams API](teams.md)

-   👔 **Agents**

    ---

    Agent search, network management, and detailed information retrieval

    [:octicons-arrow-right-24: Agents API](agents.md)

-   👤 **Users**

    ---

    Access user profiles, team membership, and office details

    [:octicons-arrow-right-24: Users API](users.md)

-   📖 **Directory**

    ---

    Access directory services for agent and contact information

    [:octicons-arrow-right-24: Directory API](directory.md)

-   ☑️ **Checklist**

    ---

    Manage transaction checklists and document uploads

    [:octicons-arrow-right-24: Checklist API](checklist.md)

-   📄 **Documents**

    ---

    Handle documents, digital signatures, and workflows

    [:octicons-arrow-right-24: Documents API](documents.md)

-   ☁️ **Dropbox**

    ---

    Integrate with Dropbox for file storage and management

    [:octicons-arrow-right-24: Dropbox API](dropbox.md)

</div>

---

## 📊 API Status Overview

| **API Section** | **Status** | **Endpoints** | **Coverage** |
|-----------------|------------|---------------|--------------|
| Transaction Builder | ✅ **Available** | 52+ endpoints | Complete |
| Transactions | ✅ **Available** | 49+ endpoints | Complete |
| Rev Share | ✅ **Available** | 12 endpoints | Complete |
| Agents | ✅ **Available** | 36+ endpoints | Complete |
| Teams | ✅ **Available** | 4 endpoints | Complete |
| Users | ✅ **Available** | 3 endpoints | Complete |
| Directory | ✅ **Available** | 16 endpoints | Complete |
| Checklist | ✅ **Available** | 9 endpoints | Complete |
| Documents | ✅ **Available** | 13 endpoints | Complete |
| Dropbox | ✅ **Available** | 5 endpoints | Complete |

---

## 📋 Quick Reference

### Core Components

!!! abstract "Main Client"

    The **`RezenClient`** serves as the main entry point, providing access to all API modules through a unified interface.

!!! abstract "Specialized Clients"

    - **Transaction Builder**: Create and configure new transactions
    - **Transactions**: Manage live transactions and participants
    - **Rev Share**: Revenue share payments, contributions, and performance
    - **Teams**: Search and filter team information
    - **Agents**: Comprehensive agent search and network management
    - **Users**: Access user profiles and team/office membership
    - **Directory**: Standalone directory services
    - **Checklist**: Transaction checklists and item management
    - **Documents**: Document uploads and digital signatures
    - **Dropbox**: Dropbox integration for file management

### Common Patterns

=== "Basic Usage"

    ```python
    from rezen import RezenClient

    # Initialize client
    client = RezenClient()

    # Access specialized APIs
    teams = client.teams.search_teams(status="ACTIVE")
    agents = client.agents.search_active_agents(name="John")
    checklist = client.checklist.get_checklist("checklist-123")
    dropbox_folders = client.dropbox.get_folders("agent-id")
    revshare_overview = client.rev_share.get_current_performance("agent-id")
    ```

=== "Error Handling"

    ```python
    from rezen import RezenClient
    from rezen.exceptions import RezenError, NotFoundError

    try:
        client = RezenClient()
        transaction = client.transactions.get_transaction("tx-123")
    except NotFoundError:
        print("Transaction not found")
    except RezenError as e:
        print(f"API error: {e}")
    ```

=== "Advanced Filtering"

    ```python
    from rezen import RezenClient
    from rezen.enums import TeamStatus, SortDirection

    client = RezenClient()

    # Advanced team search with enums
    teams = client.teams.search_teams(
        status=TeamStatus.ACTIVE,
        sort_direction=SortDirection.DESC,
        page_size=50
    )
    ```

---

## 🔧 Client Setup

!!! info "Getting Started"

    Before using any API methods, you need to set up authentication. See the [Authentication Guide](../getting-started/authentication.md) for setup instructions.

### Quick Setup

```python
from rezen import RezenClient

# Using environment variable (recommended)
client = RezenClient()

# Or with explicit API key
client = RezenClient(api_key="your_api_key_here")
```

---

## 📖 API Endpoints by Category

### **🏗️ Transaction Management**
Build and manage real estate transactions:

- **[Transaction Builder](transaction-builder.md)** - Create new transactions with participants
- **[Transactions](transactions.md)** - Manage live transactions and processing
- **Rev Share** - Revenue share payments, contributions, and performance (via `client.rev_share`)
- **[Checklist](checklist.md)** - Track transaction requirements and documents

### **👥 People & Organizations**
Work with agents, teams, and contacts:

- **[Teams](teams.md)** - Search and manage team information
- **[Agents](agents.md)** - Agent search and network management
- **[Users](users.md)** - User profiles and team/office membership
- **[Directory](directory.md)** - Contact and agent directory services

### **📄 Documents & Compliance**
Handle documents and digital workflows:

- **[Documents](documents.md)** - Digital signatures and document management
- **[Checklist](checklist.md)** - Transaction checklists and compliance tracking

### **☁️ Cloud Storage**
Integrate with cloud storage providers:

- **[Dropbox](dropbox.md)** - Dropbox integration for transaction documents

---

## 🎯 Key Features

### **Type Safety**
- Full type hints for all methods and parameters
- IDE autocompletion and error detection
- Runtime type validation with Pydantic

### **Error Handling**
- Specific exception types for different error conditions
- Rich error context with request/response details
- Comprehensive error handling patterns

### **Developer Experience**
- Google-style docstrings with examples
- Automatic retry logic for transient failures
- Built-in rate limiting and pagination support

---

## 📚 Related Documentation

!!! tip "Additional Resources"

    - **[Data Types & Enums](../reference/data-types.md)** - Type definitions and constants
    - **[Exception Reference](../reference/exceptions.md)** - Error handling guide
    - **[Examples & Guides](../guides/examples.md)** - Practical usage examples
    - **[Authentication Setup](../getting-started/authentication.md)** - Client configuration

---

## 🚀 Quick Start

New to the ReZEN API? Start here:

1. **[Install the client](../getting-started/installation.md)** - Get up and running
2. **[Configure authentication](../getting-started/authentication.md)** - Set up your API key
3. **[Try the quick start](../getting-started/quickstart.md)** - Make your first API call
4. **[Explore examples](../guides/examples.md)** - See real-world use cases

---

## 🔍 Method Lookup

Looking for a specific method? Use the search function above or browse by category:

- **Transaction creation** → [Transaction Builder](transaction-builder.md)
- **Agent search** → [Agents API](agents.md)
- **Team management** → [Teams API](teams.md)
- **Payment processing** → [Transactions API](transactions.md)
- **Contact lookup** → [Directory API](directory.md)
- **Document signatures** → [Documents API](documents.md)
- **Checklist tracking** → [Checklist API](checklist.md)
- **Cloud file storage** → [Dropbox API](dropbox.md)
- **Rev share** → Use `client.rev_share` (payments, contributors, contributions, history, performance)

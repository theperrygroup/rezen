# Frequently Asked Questions (FAQ)

Common questions and answers about the ReZEN Python API client. Find quick solutions to typical issues and learn best practices.

---

## 🚀 Getting Started

### Q: How do I get an API key for ReZEN?

**A:** Contact your ReZEN administrator or The Perry Group to obtain an API key. You'll need:

1. A valid ReZEN account
2. Appropriate permissions for API access
3. Your organization's approval for API usage

Once you have your API key, set it as an environment variable:

```bash
export REZEN_API_KEY="your_api_key_here"
```

### Q: Which Python versions are supported?

**A:** The ReZEN Python client supports:

- **Python 3.8+** (minimum requirement)
- **Python 3.12** (recommended for best performance)
- All major operating systems (Windows, macOS, Linux)

Check your Python version:

```bash
python --version
```

### Q: How do I install the ReZEN client?

**A:** Install using pip:

```bash
# Latest stable version
pip install rezen

# Specific version
pip install rezen==1.5.4

# With development dependencies
pip install rezen[dev]
```

For Poetry users:

```bash
poetry add rezen
```

---

## 🔐 Authentication & Security

### Q: How should I store my API key securely?

**A:** **Never** hardcode API keys in your source code. Use these secure methods:

=== "Environment Variables (Recommended)"

    ```bash
    # In your shell or .bashrc/.zshrc
    export REZEN_API_KEY="your_api_key_here"
    ```

    ```python
    from rezen import RezenClient
    
    # Automatically uses REZEN_API_KEY environment variable
    client = RezenClient()
    ```

=== ".env File"

    ```bash
    # .env file (add to .gitignore!)
    REZEN_API_KEY=your_api_key_here
    ```

    ```python
    from dotenv import load_dotenv
    from rezen import RezenClient
    
    load_dotenv()
    client = RezenClient()
    ```

=== "Configuration File"

    ```python
    import json
    from rezen import RezenClient
    
    # config.json (add to .gitignore!)
    with open('config.json') as f:
        config = json.load(f)
    
    client = RezenClient(api_key=config['rezen_api_key'])
    ```

### Q: What should I do if my API key is compromised?

**A:** Take immediate action:

1. **Contact ReZEN support** to revoke the compromised key
2. **Generate a new API key** through your ReZEN administrator
3. **Update your applications** with the new key
4. **Review access logs** for any unauthorized usage
5. **Audit your code** to ensure keys aren't exposed

### Q: Can I use multiple API keys in the same application?

**A:** Yes, create separate client instances:

```python
from rezen import RezenClient

# Different clients for different purposes
production_client = RezenClient(api_key="prod_key_here")
staging_client = RezenClient(api_key="staging_key_here")

# Or different organizations
org1_client = RezenClient(api_key="org1_key")
org2_client = RezenClient(api_key="org2_key")
```

---

## 🔍 API Usage

### Q: How do I handle pagination efficiently?

**A:** Use the built-in pagination parameters:

```python
from rezen import RezenClient

client = RezenClient()

# Get first page
response = client.agents.search_active_agents(
    page_number=0,  # Zero-based
    page_size=100   # Max 100 per page
)

agents = response["agents"]
total_count = response["totalCount"]

# Calculate total pages
import math
total_pages = math.ceil(total_count / 100)

# Iterate through all pages
all_agents = []
for page in range(total_pages):
    response = client.agents.search_active_agents(
        page_number=page,
        page_size=100
    )
    all_agents.extend(response["agents"])
```

### Q: What's the maximum page size I can request?

**A:** The maximum page size varies by endpoint:

- **Agents**: 100 items per page
- **Teams**: 100 items per page  
- **Transactions**: 50 items per page
- **Directory**: 100 items per page

Requesting larger page sizes will result in a validation error.

### Q: How do I search for agents by location?

**A:** Use the `state_or_province` parameter:

```python
from rezen import RezenClient

client = RezenClient()

# Single state
california_agents = client.agents.search_active_agents(
    state_or_province=["CALIFORNIA"]
)

# Multiple states
west_coast_agents = client.agents.search_active_agents(
    state_or_province=["CALIFORNIA", "OREGON", "WASHINGTON"]
)

# With additional filters
filtered_agents = client.agents.search_active_agents(
    state_or_province=["TEXAS"],
    name="Smith",
    page_size=50
)
```

### Q: How do I create a transaction with multiple participants?

**A:** Use the Transaction Builder API:

```python
from rezen import RezenClient

client = RezenClient()

# Create transaction builder
response = client.transaction_builder.create_transaction_builder()
transaction_id = response['id']

# Add property information
client.transaction_builder.update_location_info(transaction_id, {
    "address": "123 Main Street",
    "city": "Anytown", 
    "state": "CA",
    "zipCode": "90210"
})

# Add buyer
client.transaction_builder.add_buyer(transaction_id, {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "555-0123"
})

# Add seller
client.transaction_builder.add_seller(transaction_id, {
    "first_name": "Jane",
    "last_name": "Smith", 
    "email": "jane@example.com"
})

# Add listing agent
client.transaction_builder.add_listing_agent(transaction_id, {
    "agent_id": "agent-123"
})

# Submit transaction
client.transaction_builder.submit_transaction(transaction_id)
```

---

## ⚠️ Error Handling

### Q: How do I handle API rate limits?

**A:** Implement exponential backoff:

```python
import time
from rezen import RezenClient
from rezen.exceptions import RateLimitError

def make_request_with_backoff(client, max_retries=3):
    """Make API request with rate limit handling."""
    for attempt in range(max_retries):
        try:
            return client.agents.search_active_agents(page_size=100)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise the error
            
            # Wait with exponential backoff
            wait_time = (2 ** attempt) * 60  # 1min, 2min, 4min
            print(f"Rate limited, waiting {wait_time} seconds...")
            time.sleep(wait_time)

client = RezenClient()
result = make_request_with_backoff(client)
```

### Q: What do the different error types mean?

**A:** The ReZEN client provides specific exception types:

```python
from rezen.exceptions import (
    RezenError,           # Base exception
    AuthenticationError,  # Invalid API key
    ValidationError,      # Invalid parameters
    NotFoundError,        # Resource not found
    RateLimitError,       # Too many requests
    ServerError,          # Server-side error
    NetworkError          # Network connectivity issue
)

try:
    client = RezenClient()
    agents = client.agents.search_active_agents()
except AuthenticationError:
    print("Check your API key")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except NotFoundError:
    print("Resource not found")
except RateLimitError:
    print("Rate limit exceeded, slow down")
except ServerError:
    print("Server error, try again later")
except NetworkError:
    print("Network connectivity issue")
except RezenError as e:
    print(f"General API error: {e}")
```

### Q: How do I debug API request issues?

**A:** Enable detailed logging:

```python
import logging
from rezen import RezenClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Create client
client = RezenClient()

# Make request - will show detailed HTTP logs
try:
    response = client.agents.search_active_agents(page_size=10)
    print("Request successful")
except Exception as e:
    print(f"Request failed: {e}")
```

---

## 🔧 Performance & Optimization

### Q: How can I improve API response times?

**A:** Follow these optimization strategies:

1. **Use appropriate page sizes**:
   ```python
   # Good: Balanced page size
   agents = client.agents.search_active_agents(page_size=100)
   
   # Avoid: Too small (more requests)
   agents = client.agents.search_active_agents(page_size=10)
   ```

2. **Filter at the API level**:
   ```python
   # Good: Server-side filtering
   agents = client.agents.search_active_agents(
       state_or_province=["CALIFORNIA"],
       name="Smith"
   )
   
   # Avoid: Client-side filtering
   all_agents = client.agents.search_active_agents(page_size=1000)
   filtered = [a for a in all_agents["agents"] if "Smith" in a["lastName"]]
   ```

3. **Cache frequently accessed data**:
   ```python
   import time
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_agent_info(agent_id):
       return client.agents.get_agent_info(agent_id)
   ```

### Q: How do I handle large datasets efficiently?

**A:** Use pagination and generators:

```python
def get_all_agents(client):
    """Generator to efficiently iterate through all agents."""
    page_number = 0
    page_size = 100
    
    while True:
        response = client.agents.search_active_agents(
            page_number=page_number,
            page_size=page_size
        )
        
        agents = response.get("agents", [])
        if not agents:
            break
            
        for agent in agents:
            yield agent
            
        # Check if we've reached the end
        total_count = response.get("totalCount", 0)
        if (page_number + 1) * page_size >= total_count:
            break
            
        page_number += 1

# Usage
client = RezenClient()
for agent in get_all_agents(client):
    print(f"Processing {agent['firstName']} {agent['lastName']}")
    # Process one agent at a time without loading all into memory
```

### Q: Can I make concurrent API requests?

**A:** Yes, but be mindful of rate limits:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from rezen import RezenClient

def search_agents_by_state(state):
    """Search agents in a specific state."""
    client = RezenClient()
    return client.agents.search_active_agents(
        state_or_province=[state],
        page_size=50
    )

# Make concurrent requests
states = ["CALIFORNIA", "TEXAS", "FLORIDA", "NEW_YORK"]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(search_agents_by_state, states))

for i, result in enumerate(results):
    print(f"{states[i]}: {len(result['agents'])} agents")
```

---

## 🏗️ Integration & Development

### Q: How do I integrate ReZEN with my existing CRM?

**A:** Create a data synchronization layer:

```python
from rezen import RezenClient
from typing import Dict, List, Any

class CRMIntegration:
    """Integration layer between ReZEN and your CRM."""
    
    def __init__(self, rezen_api_key: str):
        self.rezen_client = RezenClient(api_key=rezen_api_key)
    
    def sync_agents_to_crm(self) -> List[Dict[str, Any]]:
        """Sync ReZEN agents to your CRM system."""
        # Get agents from ReZEN
        response = self.rezen_client.agents.search_active_agents(page_size=100)
        agents = response.get("agents", [])
        
        synced_agents = []
        for agent in agents:
            # Transform ReZEN data to CRM format
            crm_agent = {
                "external_id": agent["id"],
                "first_name": agent["firstName"],
                "last_name": agent["lastName"],
                "email": agent.get("emailAddress"),
                "phone": agent.get("phoneNumber"),
                "state": agent.get("stateOrProvince"),
                "source": "ReZEN"
            }
            
            # Save to your CRM (implement this method)
            # self.save_to_crm(crm_agent)
            synced_agents.append(crm_agent)
        
        return synced_agents

# Usage
integration = CRMIntegration(rezen_api_key="your_key")
synced_agents = integration.sync_agents_to_crm()
```

### Q: How do I test my ReZEN integration?

**A:** Use mocking for unit tests:

```python
import unittest
from unittest.mock import patch, MagicMock
from rezen import RezenClient

class TestRezenIntegration(unittest.TestCase):
    
    @patch('rezen.RezenClient')
    def test_agent_search(self, mock_client_class):
        """Test agent search functionality."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock response
        mock_response = {
            "agents": [
                {"id": "agent-123", "firstName": "John", "lastName": "Doe"}
            ],
            "totalCount": 1
        }
        mock_client.agents.search_active_agents.return_value = mock_response
        
        # Test your code
        client = RezenClient()
        result = client.agents.search_active_agents(name="John")
        
        # Assertions
        self.assertEqual(len(result["agents"]), 1)
        self.assertEqual(result["agents"][0]["firstName"], "John")
        mock_client.agents.search_active_agents.assert_called_once_with(name="John")

if __name__ == "__main__":
    unittest.main()
```

### Q: How do I handle different environments (dev/staging/prod)?

**A:** Use environment-specific configuration:

```python
import os
from rezen import RezenClient

class RezenConfig:
    """Environment-specific ReZEN configuration."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.api_key = self._get_api_key()
    
    def _get_api_key(self) -> str:
        """Get API key based on environment."""
        key_map = {
            "development": "REZEN_DEV_API_KEY",
            "staging": "REZEN_STAGING_API_KEY", 
            "production": "REZEN_PROD_API_KEY"
        }
        
        env_var = key_map.get(self.environment, "REZEN_API_KEY")
        api_key = os.getenv(env_var)
        
        if not api_key:
            raise ValueError(f"Missing API key for {self.environment} environment")
        
        return api_key
    
    def create_client(self) -> RezenClient:
        """Create ReZEN client for current environment."""
        return RezenClient(api_key=self.api_key)

# Usage
config = RezenConfig()
client = config.create_client()
```

---

## 🐛 Troubleshooting

### Q: Why am I getting "Authentication Error"?

**A:** Check these common issues:

1. **Invalid API key**:
   ```bash
   # Verify your API key is set
   echo $REZEN_API_KEY
   ```

2. **Expired API key**: Contact your ReZEN administrator

3. **Wrong environment**: Ensure you're using the correct API key for your environment

4. **Key format**: API keys should be strings without quotes in environment variables

### Q: Why are my requests timing out?

**A:** Several possible causes:

1. **Large page sizes**: Reduce page size to 50-100 items
2. **Network issues**: Check your internet connection
3. **Server load**: Try again during off-peak hours
4. **Complex queries**: Simplify your search parameters

```python
# Add timeout handling
import requests
from rezen import RezenClient

try:
    client = RezenClient()
    # This will timeout after 30 seconds
    response = client.agents.search_active_agents(page_size=50)
except requests.exceptions.Timeout:
    print("Request timed out, try reducing page size or check network")
```

### Q: Why am I getting empty results?

**A:** Verify your search parameters:

```python
from rezen import RezenClient

client = RezenClient()

# Debug your search
response = client.agents.search_active_agents(
    state_or_province=["CALIFORNIA"],
    name="Smith",
    page_size=10
)

print(f"Total count: {response.get('totalCount', 0)}")
print(f"Returned agents: {len(response.get('agents', []))}")

# Try broader search
broad_response = client.agents.search_active_agents(page_size=10)
print(f"Broad search returned: {len(broad_response.get('agents', []))}")
```

### Q: How do I report bugs or request features?

**A:** Use these channels:

1. **GitHub Issues**: [github.com/theperrygroup/rezen/issues](https://github.com/theperrygroup/rezen/issues)
2. **Email Support**: [support@rezen.com](mailto:support@rezen.com)
3. **Documentation**: Check the [troubleshooting guide](troubleshooting.md)

When reporting issues, include:
- Python version
- ReZEN client version
- Complete error message
- Minimal code example
- Expected vs actual behavior

---

## 📚 Additional Resources

### Q: Where can I find more examples?

**A:** Check these resources:

- **[Examples Guide](examples.md)** - Comprehensive code examples
- **[API Reference](../api/index.md)** - Complete method documentation
- **[GitHub Repository](https://github.com/theperrygroup/rezen)** - Source code and examples
- **[Transaction Guide](transactions.md)** - End-to-end transaction workflows

### Q: How do I stay updated on new features?

**A:** Follow these channels:

- **[Changelog](../reference/changelog.md)** - Version history and new features
- **[GitHub Releases](https://github.com/theperrygroup/rezen/releases)** - Release notifications
- **[PyPI Package](https://pypi.org/project/rezen/)** - Version updates

### Q: Can I contribute to the ReZEN client?

**A:** Yes! See the [Contributing Guide](../development/contributing.md) for:

- Development setup
- Code quality standards
- Pull request process
- Testing requirements

---

**Still have questions?** Check the [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/theperrygroup/rezen/issues) on GitHub.
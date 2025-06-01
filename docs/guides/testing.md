# Testing Guide

Comprehensive guide for testing applications that use the ReZEN Python client. Learn how to write effective tests, mock API responses, and ensure your integration is robust and reliable.

---

## 🧪 Testing Overview

Testing ReZEN API integrations requires a combination of unit tests, integration tests, and end-to-end tests. This guide covers best practices for each testing approach.

### Testing Pyramid

```
    🔺 E2E Tests (Few)
   🔺🔺 Integration Tests (Some)
  🔺🔺🔺 Unit Tests (Many)
```

- **Unit Tests**: Test individual functions with mocked API responses
- **Integration Tests**: Test API client behavior with real or realistic responses
- **End-to-End Tests**: Test complete workflows with actual API calls

---

## 🏗️ Test Setup

### Basic Test Structure

```python
import unittest
from unittest.mock import patch, MagicMock
import responses
from rezen import RezenClient
from rezen.exceptions import RezenError, AuthenticationError

class TestRezenIntegration(unittest.TestCase):
    """Test suite for ReZEN API integration."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.client = RezenClient(api_key="test_api_key")
        self.mock_agent_data = {
            "id": "agent-123",
            "firstName": "John",
            "lastName": "Doe",
            "emailAddress": "john.doe@example.com",
            "stateOrProvince": "CALIFORNIA"
        }
    
    def tearDown(self):
        """Clean up after each test method."""
        # Reset any global state if needed
        pass

if __name__ == "__main__":
    unittest.main()
```

### Test Dependencies

Add these to your `requirements-test.txt`:

```txt
pytest>=7.0.0
pytest-cov>=4.0.0
responses>=0.23.0
unittest-mock>=1.0.0
factory-boy>=3.2.0
faker>=18.0.0
```

---

## 🎭 Mocking API Responses

### Using `responses` Library

The `responses` library is excellent for mocking HTTP requests:

```python
import responses
import json
from rezen import RezenClient

class TestAgentSearch(unittest.TestCase):
    
    @responses.activate
    def test_search_active_agents_success(self):
        """Test successful agent search."""
        # Mock API response
        mock_response = {
            "agents": [
                {
                    "id": "agent-123",
                    "firstName": "John",
                    "lastName": "Doe",
                    "emailAddress": "john@example.com",
                    "stateOrProvince": "CALIFORNIA"
                }
            ],
            "totalCount": 1,
            "pageNumber": 0,
            "pageSize": 50
        }
        
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json=mock_response,
            status=200
        )
        
        # Test the client
        client = RezenClient(api_key="test_key")
        result = client.agents.search_active_agents(
            state_or_province=["CALIFORNIA"],
            page_size=50
        )
        
        # Assertions
        self.assertEqual(result, mock_response)
        self.assertEqual(len(result["agents"]), 1)
        self.assertEqual(result["agents"][0]["firstName"], "John")
        
        # Verify the request was made correctly
        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertIn("stateOrProvince=CALIFORNIA", request.url)
        self.assertIn("pageSize=50", request.url)
    
    @responses.activate
    def test_search_agents_authentication_error(self):
        """Test authentication error handling."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json={"error": "Invalid API key"},
            status=401
        )
        
        client = RezenClient(api_key="invalid_key")
        
        with self.assertRaises(AuthenticationError):
            client.agents.search_active_agents()
    
    @responses.activate
    def test_search_agents_empty_results(self):
        """Test handling of empty search results."""
        mock_response = {
            "agents": [],
            "totalCount": 0,
            "pageNumber": 0,
            "pageSize": 50
        }
        
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json=mock_response,
            status=200
        )
        
        client = RezenClient(api_key="test_key")
        result = client.agents.search_active_agents(name="NonexistentAgent")
        
        self.assertEqual(len(result["agents"]), 0)
        self.assertEqual(result["totalCount"], 0)
```

### Using `unittest.mock`

For more complex mocking scenarios:

```python
from unittest.mock import patch, MagicMock
from rezen import RezenClient

class TestTransactionBuilder(unittest.TestCase):
    
    @patch('rezen.transaction_builder.TransactionBuilderClient._make_request')
    def test_create_transaction_builder(self, mock_request):
        """Test transaction builder creation."""
        # Mock the API response
        mock_response = {
            "id": "tb-123",
            "status": "DRAFT",
            "createdAt": "2024-01-01T00:00:00Z"
        }
        mock_request.return_value = mock_response
        
        client = RezenClient(api_key="test_key")
        result = client.transaction_builder.create_transaction_builder()
        
        # Verify the result
        self.assertEqual(result["id"], "tb-123")
        self.assertEqual(result["status"], "DRAFT")
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            "POST",
            "/transaction-builder",
            data=None
        )
    
    @patch('rezen.transaction_builder.TransactionBuilderClient._make_request')
    def test_add_buyer_to_transaction(self, mock_request):
        """Test adding a buyer to a transaction."""
        mock_request.return_value = {"success": True}
        
        buyer_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice@example.com"
        }
        
        client = RezenClient(api_key="test_key")
        result = client.transaction_builder.add_buyer("tb-123", buyer_data)
        
        self.assertTrue(result["success"])
        mock_request.assert_called_once_with(
            "POST",
            "/transaction-builder/tb-123/buyer",
            data=buyer_data
        )
```

---

## 🏭 Test Factories

Use factories to generate test data consistently:

```python
import factory
from faker import Faker

fake = Faker()

class AgentFactory(factory.Factory):
    """Factory for generating agent test data."""
    
    class Meta:
        model = dict
    
    id = factory.LazyFunction(lambda: f"agent-{fake.uuid4()}")
    firstName = factory.LazyFunction(lambda: fake.first_name())
    lastName = factory.LazyFunction(lambda: fake.last_name())
    emailAddress = factory.LazyFunction(lambda: fake.email())
    phoneNumber = factory.LazyFunction(lambda: fake.phone_number())
    stateOrProvince = factory.LazyFunction(lambda: fake.random_element([
        "CALIFORNIA", "TEXAS", "FLORIDA", "NEW_YORK"
    ]))
    city = factory.LazyFunction(lambda: fake.city())
    status = "ACTIVE"
    joinDate = factory.LazyFunction(lambda: fake.date_this_year().isoformat())

class TransactionFactory(factory.Factory):
    """Factory for generating transaction test data."""
    
    class Meta:
        model = dict
    
    id = factory.LazyFunction(lambda: f"tx-{fake.uuid4()}")
    status = "ACTIVE"
    purchasePrice = factory.LazyFunction(lambda: fake.random_int(100000, 2000000))
    address = factory.LazyFunction(lambda: fake.street_address())
    city = factory.LazyFunction(lambda: fake.city())
    state = factory.LazyFunction(lambda: fake.state_abbr())
    zipCode = factory.LazyFunction(lambda: fake.zipcode())

# Usage in tests
class TestWithFactories(unittest.TestCase):
    
    @responses.activate
    def test_agent_search_with_factory_data(self):
        """Test agent search using factory-generated data."""
        # Generate test agents
        agents = [AgentFactory() for _ in range(5)]
        
        mock_response = {
            "agents": agents,
            "totalCount": len(agents),
            "pageNumber": 0,
            "pageSize": 50
        }
        
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json=mock_response,
            status=200
        )
        
        client = RezenClient(api_key="test_key")
        result = client.agents.search_active_agents()
        
        self.assertEqual(len(result["agents"]), 5)
        for agent in result["agents"]:
            self.assertIn("id", agent)
            self.assertIn("firstName", agent)
            self.assertIn("lastName", agent)
```

---

## 🔄 Integration Testing

### Testing with Real API Responses

For integration tests, you might want to use real API calls with test data:

```python
import os
import unittest
from rezen import RezenClient

@unittest.skipUnless(
    os.getenv("REZEN_TEST_API_KEY"),
    "REZEN_TEST_API_KEY environment variable not set"
)
class TestRezenIntegration(unittest.TestCase):
    """Integration tests using real API calls."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client with real API key."""
        cls.client = RezenClient(api_key=os.getenv("REZEN_TEST_API_KEY"))
    
    def test_agent_search_integration(self):
        """Test agent search with real API."""
        result = self.client.agents.search_active_agents(page_size=5)
        
        # Verify response structure
        self.assertIn("agents", result)
        self.assertIn("totalCount", result)
        self.assertIsInstance(result["agents"], list)
        self.assertIsInstance(result["totalCount"], int)
        
        # Verify agent data structure
        if result["agents"]:
            agent = result["agents"][0]
            required_fields = ["id", "firstName", "lastName"]
            for field in required_fields:
                self.assertIn(field, agent)
    
    def test_team_search_integration(self):
        """Test team search with real API."""
        result = self.client.teams.search_teams(page_size=5)
        
        self.assertIn("teams", result)
        self.assertIn("totalCount", result)
        
        if result["teams"]:
            team = result["teams"][0]
            self.assertIn("id", team)
            self.assertIn("name", team)
```

### Rate Limiting in Tests

Handle rate limits gracefully in integration tests:

```python
import time
from rezen.exceptions import RateLimitError

class TestWithRateLimit(unittest.TestCase):
    
    def make_request_with_retry(self, request_func, max_retries=3):
        """Make API request with retry logic for rate limits."""
        for attempt in range(max_retries):
            try:
                return request_func()
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) * 60  # Exponential backoff
                time.sleep(wait_time)
    
    def test_multiple_requests_with_rate_limiting(self):
        """Test multiple requests with rate limit handling."""
        client = RezenClient(api_key=os.getenv("REZEN_TEST_API_KEY"))
        
        # Make multiple requests with retry logic
        results = []
        for i in range(3):
            result = self.make_request_with_retry(
                lambda: client.agents.search_active_agents(page_size=10)
            )
            results.append(result)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn("agents", result)
```

---

## 🎯 Testing Patterns

### Testing Error Scenarios

```python
class TestErrorHandling(unittest.TestCase):
    
    @responses.activate
    def test_network_error_handling(self):
        """Test handling of network errors."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            body=ConnectionError("Network error")
        )
        
        client = RezenClient(api_key="test_key")
        
        with self.assertRaises(ConnectionError):
            client.agents.search_active_agents()
    
    @responses.activate
    def test_server_error_handling(self):
        """Test handling of server errors."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json={"error": "Internal server error"},
            status=500
        )
        
        client = RezenClient(api_key="test_key")
        
        with self.assertRaises(RezenError):
            client.agents.search_active_agents()
    
    @responses.activate
    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json={"error": "Invalid page size"},
            status=400
        )
        
        client = RezenClient(api_key="test_key")
        
        with self.assertRaises(RezenError):
            client.agents.search_active_agents(page_size=1000)  # Invalid size
```

### Testing Pagination

```python
class TestPagination(unittest.TestCase):
    
    @responses.activate
    def test_pagination_workflow(self):
        """Test pagination through multiple pages."""
        # Mock first page
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json={
                "agents": [AgentFactory() for _ in range(50)],
                "totalCount": 150,
                "pageNumber": 0,
                "pageSize": 50
            },
            status=200
        )
        
        # Mock second page
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json={
                "agents": [AgentFactory() for _ in range(50)],
                "totalCount": 150,
                "pageNumber": 1,
                "pageSize": 50
            },
            status=200
        )
        
        # Mock third page
        responses.add(
            responses.GET,
            "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
            json={
                "agents": [AgentFactory() for _ in range(50)],
                "totalCount": 150,
                "pageNumber": 2,
                "pageSize": 50
            },
            status=200
        )
        
        client = RezenClient(api_key="test_key")
        
        # Test pagination logic
        all_agents = []
        page_number = 0
        page_size = 50
        
        while True:
            result = client.agents.search_active_agents(
                page_number=page_number,
                page_size=page_size
            )
            
            agents = result["agents"]
            if not agents:
                break
            
            all_agents.extend(agents)
            
            # Check if we've reached the end
            total_count = result["totalCount"]
            if (page_number + 1) * page_size >= total_count:
                break
            
            page_number += 1
        
        self.assertEqual(len(all_agents), 150)
        self.assertEqual(len(responses.calls), 3)
```

### Testing Custom Business Logic

```python
class TestBusinessLogic(unittest.TestCase):
    """Test custom business logic that uses ReZEN client."""
    
    def setUp(self):
        self.client = RezenClient(api_key="test_key")
    
    @patch.object(RezenClient, 'agents')
    def test_find_agents_by_state(self, mock_agents):
        """Test custom function that finds agents by state."""
        # Mock the agents client
        mock_agents.search_active_agents.return_value = {
            "agents": [
                AgentFactory(stateOrProvince="CALIFORNIA"),
                AgentFactory(stateOrProvince="CALIFORNIA")
            ],
            "totalCount": 2
        }
        
        # Your custom business logic
        def find_agents_by_state(client, state):
            """Find all agents in a specific state."""
            result = client.agents.search_active_agents(
                state_or_province=[state]
            )
            return result["agents"]
        
        # Test the function
        agents = find_agents_by_state(self.client, "CALIFORNIA")
        
        self.assertEqual(len(agents), 2)
        for agent in agents:
            self.assertEqual(agent["stateOrProvince"], "CALIFORNIA")
        
        # Verify the mock was called correctly
        mock_agents.search_active_agents.assert_called_once_with(
            state_or_province=["CALIFORNIA"]
        )
```

---

## 📊 Test Coverage

### Measuring Coverage

Use `pytest-cov` to measure test coverage:

```bash
# Run tests with coverage
pytest --cov=your_app --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Coverage Configuration

Create a `.coveragerc` file:

```ini
[run]
source = your_app
omit = 
    */tests/*
    */venv/*
    */migrations/*
    manage.py
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

---

## 🚀 Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-test.txt
        pip install -e .
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=your_app --cov-report=xml
    
    - name: Run integration tests
      env:
        REZEN_TEST_API_KEY: ${{ secrets.REZEN_TEST_API_KEY }}
      run: |
        pytest tests/integration/ -v
      if: env.REZEN_TEST_API_KEY != ''
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

---

## 🛠️ Testing Utilities

### Custom Test Helpers

```python
# tests/helpers.py
import json
from typing import Dict, Any, List
from unittest.mock import MagicMock

class RezenTestHelper:
    """Helper class for ReZEN API testing."""
    
    @staticmethod
    def create_mock_response(data: Dict[str, Any], status_code: int = 200) -> MagicMock:
        """Create a mock HTTP response."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = data
        mock_response.text = json.dumps(data)
        return mock_response
    
    @staticmethod
    def create_agent_list(count: int) -> List[Dict[str, Any]]:
        """Create a list of mock agents."""
        return [AgentFactory() for _ in range(count)]
    
    @staticmethod
    def create_paginated_response(
        items: List[Dict[str, Any]], 
        page_number: int = 0, 
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Create a paginated API response."""
        return {
            "agents": items,
            "totalCount": len(items),
            "pageNumber": page_number,
            "pageSize": page_size
        }

# Usage in tests
class TestWithHelpers(unittest.TestCase):
    
    def test_with_helper(self):
        """Test using helper functions."""
        agents = RezenTestHelper.create_agent_list(10)
        response = RezenTestHelper.create_paginated_response(agents)
        
        self.assertEqual(len(response["agents"]), 10)
        self.assertEqual(response["totalCount"], 10)
```

### Test Configuration

```python
# tests/conftest.py (for pytest)
import pytest
import os
from rezen import RezenClient

@pytest.fixture
def mock_client():
    """Fixture for mocked ReZEN client."""
    return RezenClient(api_key="test_api_key")

@pytest.fixture
def real_client():
    """Fixture for real ReZEN client (integration tests)."""
    api_key = os.getenv("REZEN_TEST_API_KEY")
    if not api_key:
        pytest.skip("REZEN_TEST_API_KEY not set")
    return RezenClient(api_key=api_key)

@pytest.fixture
def sample_agent():
    """Fixture for sample agent data."""
    return AgentFactory()

# Usage in tests
def test_with_fixtures(mock_client, sample_agent):
    """Test using pytest fixtures."""
    assert mock_client is not None
    assert "id" in sample_agent
```

---

## 📋 Testing Checklist

### Unit Tests
- [ ] Test all public methods
- [ ] Test error handling scenarios
- [ ] Test edge cases and boundary conditions
- [ ] Mock external dependencies
- [ ] Achieve >90% code coverage

### Integration Tests
- [ ] Test with real API responses
- [ ] Test authentication flows
- [ ] Test rate limiting behavior
- [ ] Test pagination workflows
- [ ] Test error recovery

### End-to-End Tests
- [ ] Test complete business workflows
- [ ] Test with production-like data
- [ ] Test performance under load
- [ ] Test deployment scenarios

### Best Practices
- [ ] Use descriptive test names
- [ ] Keep tests independent
- [ ] Use factories for test data
- [ ] Mock external services
- [ ] Test both success and failure paths

---

This comprehensive testing guide provides the foundation for building robust, well-tested ReZEN API integrations. Remember to adapt these patterns to your specific use case and testing requirements.
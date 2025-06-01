# The Perry Group Python Style Guide

This document outlines the coding standards and practices for the Perry Group Python API wrapper projects. Following these guidelines ensures consistent, maintainable, and high-quality code.

## General Principles

- **Readability**: Code should be easily readable by others
- **Consistency**: Follow established patterns in the codebase
- **Simplicity**: Prefer simpler solutions over complex ones
- **Documentation**: Document code thoroughly with docstrings
- **Type Safety**: Use type hints for all function parameters and return values

## Code Organization

### File Structure

- One client class per file when possible (with exceptions for closely related utility classes)
- Group related API endpoints in modules (e.g., `agents.py`, `transactions.py`, `teams.py`)
- Follow logical API grouping and service boundaries

### Import Order

1. Python standard library imports
2. Third-party library imports (requests, pydantic, etc.)
3. Local package imports
4. Import specific classes/functions rather than modules where practical

Example:
```python
import re
import logging
from datetime import datetime
from typing import Dict, Optional, List

import requests
from pydantic import BaseModel
from requests.adapters import HTTPAdapter

from .base_client import BaseClient
from .exceptions import RezenError, ValidationError
```

## Code Style

### Class Structure

- Use object-oriented design principles
- Break large client classes into focused endpoint groups
- Follow single responsibility principle for each client class

```python
class AgentsClient:
    """Client for agent-related API endpoints."""

    def __init__(self, base_client: BaseClient) -> None:
        """Initialize the agents client."""
        self._client = base_client

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent by ID."""
        # Implementation
```

### Method Organization

- Public methods first, followed by private methods
- Group related methods together
- Use descriptive method names

### Naming Conventions

- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods/attributes**: Prefix with underscore `_private_method`

## Type Hints

Use comprehensive type hints for all function/method signatures:

```python
def process_lead(
    lead_data: Dict[str, str],
    reference_id: str,
    create_date: Optional[datetime] = None
) -> Optional[Lead]:
    """Process lead data and create a Lead object if valid."""
    # Implementation
```

## Docstrings

Use Google-style docstrings for all public methods, functions, and classes:

```python
def clean_phone(phone: str) -> str:
    """Clean and standardize phone number format.

    Args:
        phone: Raw phone number string

    Returns:
        Cleaned phone number in format (XXX) XXX-XXXX

    Raises:
        ValueError: If the phone number is invalid
    """
    # Implementation
```

## Error Handling

- Use specific exception types for different API error conditions
- Always log API errors with context including request details
- Handle errors at appropriate levels (network, authentication, validation)

```python
try:
    response = self._client.make_request("GET", f"/agents/{agent_id}")
    return response.json()
except requests.ConnectionError as e:
    logger.error(f"Network error fetching agent {agent_id}: {e}")
    raise NetworkError(f"Failed to connect to ReZEN API: {e}")
except requests.HTTPError as e:
    if e.response.status_code == 404:
        raise NotFoundError(f"Agent {agent_id} not found")
    elif e.response.status_code == 401:
        raise AuthenticationError("Invalid API credentials")
    else:
        raise RezenError(f"API error: {e}")
```

## Testing

- Write tests for all new functionality
- Use descriptive test method names that explain what they test
- Separate unit tests from integration tests

## Tools and Enforcement

This project uses the following tools to enforce style:

1. **Black**: For code formatting
2. **isort**: For import sorting
3. **mypy**: For type checking
4. **flake8**: For linting
5. **pylint**: For deeper code analysis

Configuration files for these tools are in the project root.

## Data Models and Validation

- Use Pydantic models for request/response validation when appropriate
- Include docstrings for model classes and complex fields
- Use appropriate type hints and validators
- Define clear data transformation methods for API responses

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Agent(BaseModel):
    """Agent data model."""

    id: str = Field(..., description="Unique agent identifier")
    email: str = Field(..., description="Agent email address")
    first_name: str = Field(..., description="Agent first name")
    last_name: str = Field(..., description="Agent last name")
    status: str = Field(..., description="Agent status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")

    class Config:
        """Pydantic model configuration."""
        allow_population_by_field_name = True
        validate_assignment = True
```

## Git Commits

- Write descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issue numbers in commit messages

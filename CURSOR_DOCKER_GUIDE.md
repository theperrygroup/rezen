# Running ReZEN Background Agents in Cursor

This guide shows you how to quickly set up and run ReZEN API background agents using Docker in Cursor.

## Quick Setup

### 1. Build and Start the Agent

Open your Cursor terminal and run:

```bash
# Build the Docker image
docker compose build

# Start the background agent
docker compose up -d rezen-agent
```

### 2. Run Your First Agent

```bash
# Test the sample agent (runs once and exits)
docker exec rezen-background-agent python agents/sample_agent.py

# Or run the transaction monitor (continuous monitoring)
docker exec rezen-background-agent python agents/transaction_monitor.py
```

### 3. View Logs

```bash
# View real-time logs
docker compose logs -f rezen-agent

# Or check the log files directly
cat logs/agent.log
```

## Running Agents in Background

### Start a Long-Running Agent

To run an agent continuously in the background:

```bash
# Start the sample agent in background (runs every 60 seconds)
docker exec -d rezen-background-agent python agents/sample_agent.py

# Start transaction monitor in background (runs every 5 minutes)
docker exec -d rezen-background-agent python agents/transaction_monitor.py
```

### Monitor Running Agents

```bash
# Check running processes in the container
docker exec rezen-background-agent ps aux

# View container stats
docker stats rezen-background-agent

# Follow logs in real-time
tail -f logs/agent.log
```

## Custom Agent Development

### 1. Create Your Agent

Create a new file in the `agents/` directory (e.g., `agents/my_agent.py`):

```python
#!/usr/bin/env python3
"""My Custom ReZEN Agent"""

import os
import time
from rezen import RezenClient

def main():
    # Get API key from environment
    api_key = os.getenv("REZEN_API_KEY")
    client = RezenClient(api_key=api_key)

    print("Starting my custom agent...")

    # Your custom logic here
    try:
        # Example: Monitor active teams
        teams = client.teams.search_teams(status="ACTIVE")
        print(f"Found {len(teams.get('data', []))} active teams")

        # Example: Check agents
        agents = client.agents.search_active_agents(name="")
        print(f"Found {len(agents.get('data', []))} active agents")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

### 2. Run Your Custom Agent

```bash
# Make it executable
chmod +x agents/my_agent.py

# Run it once
docker exec rezen-background-agent python agents/my_agent.py

# Run it in background
docker exec -d rezen-background-agent python agents/my_agent.py
```

## Environment Configuration

### Set Custom Environment Variables

```bash
# Run with custom settings
docker exec -e AGENT_INTERVAL=30 -e LOG_LEVEL=DEBUG rezen-background-agent python agents/sample_agent.py

# Or modify the .env file and restart
echo "AGENT_INTERVAL=30" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
docker compose restart rezen-agent
```

## Common Commands

### Container Management

```bash
# Start the agent container
docker compose up -d rezen-agent

# Stop the agent container
docker compose down

# Restart the agent container
docker compose restart rezen-agent

# View container status
docker compose ps
```

### Debugging

```bash
# Open interactive shell in container
docker exec -it rezen-background-agent /bin/bash

# Test ReZEN client interactively
docker exec -it rezen-background-agent python
>>> from rezen import RezenClient
>>> client = RezenClient()
>>> # Test your API calls here

# View all logs
docker compose logs
```

### Development

```bash
# Start development container (with full access to source code)
docker compose --profile dev up -d rezen-dev

# Connect to development container
docker exec -it rezen-dev /bin/bash

# Run tests in development container
docker exec rezen-dev python -m pytest tests/
```

## Integration with Cursor

### Using Terminal in Cursor

1. Open Cursor terminal (`` Ctrl+` `` or `Cmd+`` )
2. Run any of the commands above directly in the terminal
3. The Docker containers will run in the background while you continue coding

### File Watching

The `agents/` and `logs/` directories are mounted as volumes, so:
- Any changes you make to agent files are immediately available in the container
- Log files are written to your local `logs/` directory for easy viewing

### VS Code Integration

You can also:
- Use the Docker extension in Cursor to manage containers
- View logs directly in the Cursor terminal
- Edit agent files with full IntelliSense support

## Stopping Everything

When you're done:

```bash
# Stop all containers
docker compose down

# Stop and remove volumes (clears logs)
docker compose down -v

# Remove the Docker image (saves space)
docker rmi rezen-rezen-agent
```

## Next Steps

1. **Customize Agents**: Modify the sample agents for your specific use cases
2. **Add Monitoring**: Set up alerts and notifications in your agents
3. **Scale Up**: Use Docker Swarm or Kubernetes for production deployments
4. **Integrate**: Connect your agents with other tools and systems

For more detailed information, see the full [DOCKER_README.md](./DOCKER_README.md).

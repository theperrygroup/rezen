# ReZEN Docker Setup

This guide explains how to run ReZEN API clients as background agents using Docker.

## Quick Start

### 1. Build the Docker Image

```bash
docker-compose build
```

### 2. Run Background Agent

```bash
# Start the container in the background
docker-compose up -d rezen-agent

# View logs
docker-compose logs -f rezen-agent
```

### 3. Run Your Custom Agent

```bash
# Execute your agent script in the running container
docker exec rezen-background-agent python agents/sample_agent.py

# Or run a specific agent with custom environment variables
docker exec -e AGENT_INTERVAL=30 rezen-background-agent python agents/transaction_monitor.py
```

## Configuration

### Environment Variables

The following environment variables can be configured:

| Variable | Description | Default |
|----------|-------------|---------|
| `REZEN_API_KEY` | Your ReZEN API key | `real_v2neAIGs2QEYJ14ck8uypMsBqOquT9TgmMzf` |
| `AGENT_INTERVAL` | Interval between agent executions (seconds) | `60` |
| `MONITOR_INTERVAL` | Interval for transaction monitoring (seconds) | `300` |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

### Custom Environment File

Create a `.env` file in the project root:

```bash
REZEN_API_KEY=your_api_key_here
AGENT_INTERVAL=30
LOG_LEVEL=DEBUG
```

## Available Agents

### 1. Sample Agent (`agents/sample_agent.py`)

A basic example that demonstrates:
- API client initialization
- Error handling
- Logging
- Graceful shutdown

**Usage:**
```bash
docker exec rezen-background-agent python agents/sample_agent.py
```

### 2. Transaction Monitor (`agents/transaction_monitor.py`)

A more advanced agent that:
- Monitors transaction changes
- Maintains state between runs
- Handles transaction status updates
- Provides extensible hooks for custom logic

**Usage:**
```bash
docker exec rezen-background-agent python agents/transaction_monitor.py
```

## Creating Custom Agents

### 1. Create Your Agent Script

Create a new Python file in the `agents/` directory:

```python
#!/usr/bin/env python3
"""My Custom Agent"""

import os
from rezen import RezenClient

def main():
    api_key = os.getenv("REZEN_API_KEY")
    client = RezenClient(api_key=api_key)

    # Your custom logic here
    print("Running custom agent...")

    # Example: Get teams
    teams = client.teams.search_teams(status="ACTIVE")
    print(f"Found {len(teams.get('data', []))} active teams")

if __name__ == "__main__":
    main()
```

### 2. Make It Executable

```bash
chmod +x agents/my_custom_agent.py
```

### 3. Run Your Agent

```bash
docker exec rezen-background-agent python agents/my_custom_agent.py
```

## Docker Commands

### Start Services

```bash
# Start main agent service
docker-compose up -d rezen-agent

# Start development service (interactive)
docker-compose up -d rezen-dev --profile dev
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs

```bash
# View agent logs
docker-compose logs -f rezen-agent

# View logs from specific container
docker logs rezen-background-agent
```

### Execute Commands

```bash
# Run bash in the container
docker exec -it rezen-background-agent /bin/bash

# Run Python commands
docker exec rezen-background-agent python -c "from rezen import RezenClient; print('ReZEN is ready!')"

# Run agent with custom environment
docker exec -e LOG_LEVEL=DEBUG rezen-background-agent python agents/sample_agent.py
```

### Development Mode

For development and testing:

```bash
# Start development container
docker-compose --profile dev up -d rezen-dev

# Connect to development container
docker exec -it rezen-dev /bin/bash

# Run tests in development container
docker exec rezen-dev python -m pytest tests/
```

## Production Deployment

### 1. Update docker-compose.yml

For production, modify the docker-compose.yml:

```yaml
services:
  rezen-agent:
    # ... existing configuration ...
    command: python agents/my_production_agent.py
    restart: always
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
```

### 2. Use Docker Swarm or Kubernetes

For orchestrated deployments, consider:
- Docker Swarm
- Kubernetes
- AWS ECS
- Google Cloud Run

### 3. Health Checks

Add health checks to your agents:

```python
# In your agent script
def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
```

## Monitoring and Logging

### Log Files

Logs are stored in the `logs/` directory:
- `logs/agent.log` - Sample agent logs
- `logs/transaction_monitor.log` - Transaction monitor logs
- `logs/transaction_state.json` - Transaction monitor state

### Log Rotation

For production, consider implementing log rotation:

```bash
# Add to your Docker setup
volumes:
  - ./logs:/app/logs
  - /etc/logrotate.d/rezen:/etc/logrotate.d/rezen
```

### Monitoring

Monitor your agents using:
- Docker stats: `docker stats rezen-background-agent`
- Log aggregation tools (ELK stack, Fluentd)
- Application monitoring (Prometheus, Grafana)

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   Error: REZEN_API_KEY environment variable is required
   ```
   **Solution:** Set the `REZEN_API_KEY` environment variable.

2. **Permission Denied**
   ```bash
   docker: permission denied
   ```
   **Solution:** Add your user to the docker group or use `sudo`.

3. **Container Exits Immediately**
   ```bash
   docker-compose logs rezen-agent
   ```
   **Solution:** Check logs for errors and ensure your agent script is correct.

### Debug Mode

Run agents in debug mode:

```bash
docker exec -e LOG_LEVEL=DEBUG rezen-background-agent python agents/sample_agent.py
```

### Interactive Debugging

```bash
# Start an interactive Python session
docker exec -it rezen-background-agent python

# Import and test the ReZEN client
>>> from rezen import RezenClient
>>> client = RezenClient()
>>> teams = client.teams.search_teams(status="ACTIVE")
>>> print(teams)
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Network**: Use Docker networks to isolate containers
3. **User**: The container runs as a non-root user for security
4. **Updates**: Regularly update the base image and dependencies

## Next Steps

1. Customize the provided agent templates for your use case
2. Set up monitoring and alerting for your agents
3. Implement proper error handling and retry logic
4. Consider using a message queue for more complex workflows
5. Set up automated deployments with CI/CD

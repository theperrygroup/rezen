# Performance & Optimization Guide

Learn how to build high-performance applications with the ReZEN Python client, including best practices for handling large datasets, optimizing API calls, and managing resources efficiently.

---

## 🚀 Performance Overview

The ReZEN Python client is designed for high-performance applications with built-in optimizations:

- **Connection pooling** for efficient HTTP session management
- **Automatic retry logic** with exponential backoff
- **Request/response caching** for frequently accessed data
- **Pagination support** for handling large datasets
- **Rate limiting compliance** to prevent API throttling

---

## 📊 Benchmarking & Monitoring

### Performance Metrics

Monitor these key metrics in your applications:

```python
import time
from typing import Dict, List, Any
from rezen import RezenClient

def benchmark_api_call(client: RezenClient, operation: str) -> Dict[str, Any]:
    """Benchmark an API operation and return performance metrics."""
    start_time = time.time()
    
    try:
        if operation == "search_agents":
            result = client.agents.search_active_agents(page_size=100)
        elif operation == "search_teams":
            result = client.teams.search_teams(page_size=50)
        else:
            raise ValueError(f"Unknown operation: {operation}")
            
        end_time = time.time()
        
        return {
            "operation": operation,
            "duration_ms": (end_time - start_time) * 1000,
            "success": True,
            "result_count": len(result.get("agents", result.get("teams", []))),
            "total_count": result.get("totalCount", 0)
        }
    except Exception as e:
        end_time = time.time()
        return {
            "operation": operation,
            "duration_ms": (end_time - start_time) * 1000,
            "success": False,
            "error": str(e)
        }

# Example usage
client = RezenClient()
metrics = benchmark_api_call(client, "search_agents")
print(f"Operation took {metrics['duration_ms']:.2f}ms")
```

### Application Performance Monitoring

```python
import logging
from contextlib import contextmanager
from typing import Generator, Dict, Any
from rezen import RezenClient

# Configure performance logging
logging.basicConfig(level=logging.INFO)
performance_logger = logging.getLogger("rezen.performance")

@contextmanager
def performance_monitor(operation: str) -> Generator[Dict[str, Any], None, None]:
    """Context manager for monitoring API operation performance."""
    start_time = time.time()
    metrics = {"operation": operation, "start_time": start_time}
    
    try:
        yield metrics
        metrics["success"] = True
    except Exception as e:
        metrics["success"] = False
        metrics["error"] = str(e)
        raise
    finally:
        end_time = time.time()
        metrics["duration"] = end_time - start_time
        
        performance_logger.info(
            f"Operation: {operation}, "
            f"Duration: {metrics['duration']:.3f}s, "
            f"Success: {metrics['success']}"
        )

# Usage example
client = RezenClient()

with performance_monitor("bulk_agent_search") as metrics:
    agents = client.agents.search_active_agents(page_size=100)
    metrics["result_count"] = len(agents.get("agents", []))
```

---

## 🔄 Efficient Pagination

### Handling Large Datasets

When working with large datasets, use efficient pagination patterns:

```python
from typing import Iterator, Dict, Any, List
from rezen import RezenClient

def paginate_all_agents(
    client: RezenClient,
    page_size: int = 100,
    max_pages: int = None
) -> Iterator[Dict[str, Any]]:
    """Efficiently paginate through all agents."""
    page_number = 0
    
    while True:
        # Check max pages limit
        if max_pages and page_number >= max_pages:
            break
            
        response = client.agents.search_active_agents(
            page_number=page_number,
            page_size=page_size
        )
        
        agents = response.get("agents", [])
        if not agents:
            break
            
        # Yield individual agents
        for agent in agents:
            yield agent
            
        # Check if we've reached the end
        total_count = response.get("totalCount", 0)
        current_count = (page_number + 1) * page_size
        if current_count >= total_count:
            break
            
        page_number += 1

# Process agents efficiently
client = RezenClient()
processed_count = 0

for agent in paginate_all_agents(client, page_size=50, max_pages=10):
    # Process each agent
    print(f"Processing agent: {agent['firstName']} {agent['lastName']}")
    processed_count += 1
    
    # Optional: Add processing delay to avoid overwhelming the API
    if processed_count % 100 == 0:
        time.sleep(0.1)  # 100ms delay every 100 agents

print(f"Processed {processed_count} agents")
```

### Batch Processing

Process data in batches for better memory management:

```python
from typing import List, Dict, Any, Callable
import asyncio
from concurrent.futures import ThreadPoolExecutor

def process_agents_in_batches(
    agents: List[Dict[str, Any]],
    batch_size: int = 50,
    processor: Callable[[Dict[str, Any]], Any] = None
) -> List[Any]:
    """Process agents in batches to manage memory usage."""
    results = []
    
    for i in range(0, len(agents), batch_size):
        batch = agents[i:i + batch_size]
        batch_results = []
        
        for agent in batch:
            if processor:
                result = processor(agent)
                batch_results.append(result)
            else:
                # Default processing
                batch_results.append({
                    "id": agent["id"],
                    "name": f"{agent['firstName']} {agent['lastName']}",
                    "processed": True
                })
        
        results.extend(batch_results)
        
        # Optional: Progress reporting
        print(f"Processed batch {i//batch_size + 1}, "
              f"total processed: {len(results)}")
    
    return results

# Example usage
def custom_agent_processor(agent: Dict[str, Any]) -> Dict[str, Any]:
    """Custom processing logic for each agent."""
    return {
        "agent_id": agent["id"],
        "full_name": f"{agent['firstName']} {agent['lastName']}",
        "email": agent.get("emailAddress"),
        "state": agent.get("stateOrProvince"),
        "processed_at": time.time()
    }

# Get agents and process in batches
client = RezenClient()
response = client.agents.search_active_agents(page_size=200)
agents = response.get("agents", [])

processed_agents = process_agents_in_batches(
    agents,
    batch_size=25,
    processor=custom_agent_processor
)
```

---

## ⚡ Connection Optimization

### Session Management

The ReZEN client automatically manages HTTP sessions, but you can optimize for specific use cases:

```python
from rezen import RezenClient
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_optimized_client(
    max_retries: int = 3,
    pool_connections: int = 10,
    pool_maxsize: int = 20,
    timeout: int = 30
) -> RezenClient:
    """Create a ReZEN client with optimized connection settings."""
    
    # Create custom session with optimized settings
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
    )
    
    # Configure HTTP adapter
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default timeout
    session.timeout = timeout
    
    # Create client with custom session
    client = RezenClient()
    # Note: This is conceptual - actual implementation may vary
    # client._session = session
    
    return client

# Usage
optimized_client = create_optimized_client(
    max_retries=5,
    pool_connections=20,
    pool_maxsize=50,
    timeout=45
)
```

### Concurrent Requests

For applications that need to make multiple independent API calls:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable
from rezen import RezenClient

def make_concurrent_requests(
    client: RezenClient,
    requests: List[Dict[str, Any]],
    max_workers: int = 5
) -> List[Dict[str, Any]]:
    """Make multiple API requests concurrently."""
    
    def execute_request(request_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single API request."""
        try:
            method = request_config["method"]
            params = request_config.get("params", {})
            
            if method == "search_agents":
                result = client.agents.search_active_agents(**params)
            elif method == "search_teams":
                result = client.teams.search_teams(**params)
            elif method == "get_agent_network":
                agent_id = params["agent_id"]
                result = client.agents.get_network_size_by_tier(agent_id)
            else:
                raise ValueError(f"Unknown method: {method}")
                
            return {
                "request": request_config,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "request": request_config,
                "error": str(e),
                "success": False
            }
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all requests
        future_to_request = {
            executor.submit(execute_request, req): req 
            for req in requests
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_request):
            result = future.result()
            results.append(result)
    
    return results

# Example usage
client = RezenClient()

# Define multiple requests
requests = [
    {
        "method": "search_agents",
        "params": {"page_size": 50, "state_or_province": ["CALIFORNIA"]}
    },
    {
        "method": "search_agents", 
        "params": {"page_size": 50, "state_or_province": ["TEXAS"]}
    },
    {
        "method": "search_teams",
        "params": {"status": "ACTIVE", "page_size": 25}
    }
]

# Execute concurrently
results = make_concurrent_requests(client, requests, max_workers=3)

# Process results
for result in results:
    if result["success"]:
        method = result["request"]["method"]
        data = result["result"]
        print(f"{method}: {len(data.get('agents', data.get('teams', [])))} items")
    else:
        print(f"Error in {result['request']['method']}: {result['error']}")
```

---

## 🎯 Caching Strategies

### Response Caching

Implement caching for frequently accessed data:

```python
import time
from typing import Dict, Any, Optional
from functools import wraps
from rezen import RezenClient

class ResponseCache:
    """Simple in-memory cache for API responses."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if not expired."""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry["expires_at"]:
                return entry["data"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Dict[str, Any], ttl: int = None) -> None:
        """Cache response with TTL."""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl
        }
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()

# Global cache instance
response_cache = ResponseCache(default_ttl=600)  # 10 minutes

def cached_api_call(cache_key_template: str, ttl: int = None):
    """Decorator to cache API responses."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_key_template.format(*args, **kwargs)
            
            # Try to get from cache
            cached_result = response_cache.get(cache_key)
            if cached_result is not None:
                print(f"Cache hit for {cache_key}")
                return cached_result
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Cache the result
            response_cache.set(cache_key, result, ttl)
            print(f"Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator

class CachedRezenClient:
    """ReZEN client wrapper with caching capabilities."""
    
    def __init__(self, api_key: str = None):
        self.client = RezenClient(api_key=api_key)
    
    @cached_api_call("agents_search_{page_size}_{state_or_province}", ttl=300)
    def search_agents_cached(
        self,
        page_size: int = 50,
        state_or_province: List[str] = None
    ) -> Dict[str, Any]:
        """Search agents with caching."""
        return self.client.agents.search_active_agents(
            page_size=page_size,
            state_or_province=state_or_province
        )
    
    @cached_api_call("teams_search_{status}_{page_size}", ttl=600)
    def search_teams_cached(
        self,
        status: str = "ACTIVE",
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Search teams with caching."""
        return self.client.teams.search_teams(
            status=status,
            page_size=page_size
        )

# Usage example
cached_client = CachedRezenClient()

# First call - hits API
agents1 = cached_client.search_agents_cached(
    page_size=100,
    state_or_province=["CALIFORNIA"]
)

# Second call - uses cache
agents2 = cached_client.search_agents_cached(
    page_size=100,
    state_or_province=["CALIFORNIA"]
)
```

---

## 📈 Memory Management

### Efficient Data Processing

Handle large datasets without excessive memory usage:

```python
from typing import Iterator, Dict, Any
import gc
from rezen import RezenClient

def process_large_dataset_efficiently(
    client: RezenClient,
    processor: Callable[[Dict[str, Any]], None],
    batch_size: int = 100,
    memory_threshold_mb: int = 500
) -> None:
    """Process large datasets with memory management."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    page_number = 0
    total_processed = 0
    
    while True:
        # Check memory usage
        memory_mb = process.memory_info().rss / 1024 / 1024
        if memory_mb > memory_threshold_mb:
            print(f"Memory usage ({memory_mb:.1f}MB) exceeds threshold, "
                  f"forcing garbage collection")
            gc.collect()
        
        # Get next batch
        response = client.agents.search_active_agents(
            page_number=page_number,
            page_size=batch_size
        )
        
        agents = response.get("agents", [])
        if not agents:
            break
        
        # Process batch
        for agent in agents:
            processor(agent)
            total_processed += 1
        
        # Clear local references
        del agents
        del response
        
        # Progress reporting
        if total_processed % 1000 == 0:
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"Processed {total_processed} agents, "
                  f"memory usage: {memory_mb:.1f}MB")
        
        page_number += 1

# Example processor
def lightweight_processor(agent: Dict[str, Any]) -> None:
    """Lightweight processing that doesn't accumulate data."""
    # Process agent data without storing it
    agent_id = agent["id"]
    name = f"{agent['firstName']} {agent['lastName']}"
    
    # Example: Write to file instead of keeping in memory
    with open("processed_agents.txt", "a") as f:
        f.write(f"{agent_id},{name}\n")

# Usage
client = RezenClient()
process_large_dataset_efficiently(
    client,
    processor=lightweight_processor,
    batch_size=50,
    memory_threshold_mb=200
)
```

---

## 🔧 Error Handling & Resilience

### Robust Error Handling

Implement comprehensive error handling for production applications:

```python
import time
import random
from typing import Dict, Any, Optional, Callable
from rezen import RezenClient
from rezen.exceptions import (
    RezenError, 
    RateLimitError, 
    NetworkError, 
    ServerError
)

class ResilientRezenClient:
    """ReZEN client wrapper with enhanced error handling and resilience."""
    
    def __init__(
        self,
        api_key: str = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ):
        self.client = RezenClient(api_key=api_key)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.1, 0.3) * delay
        return delay + jitter
    
    def _retry_with_backoff(
        self,
        operation: Callable[[], Dict[str, Any]],
        operation_name: str
    ) -> Dict[str, Any]:
        """Execute operation with retry logic and exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation()
            
            except RateLimitError as e:
                last_exception = e
                if attempt < self.max_retries:
                    # For rate limits, use longer delays
                    delay = self._exponential_backoff(attempt) * 2
                    print(f"Rate limited on {operation_name}, "
                          f"retrying in {delay:.1f}s (attempt {attempt + 1})")
                    time.sleep(delay)
                    continue
            
            except (NetworkError, ServerError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self._exponential_backoff(attempt)
                    print(f"Transient error on {operation_name}: {e}, "
                          f"retrying in {delay:.1f}s (attempt {attempt + 1})")
                    time.sleep(delay)
                    continue
            
            except RezenError as e:
                # Don't retry on client errors (4xx)
                print(f"Client error on {operation_name}: {e}")
                raise
            
            except Exception as e:
                # Don't retry on unexpected errors
                print(f"Unexpected error on {operation_name}: {e}")
                raise
        
        # All retries exhausted
        print(f"All retries exhausted for {operation_name}")
        raise last_exception
    
    def search_agents_resilient(self, **kwargs) -> Dict[str, Any]:
        """Search agents with resilient error handling."""
        def operation():
            return self.client.agents.search_active_agents(**kwargs)
        
        return self._retry_with_backoff(operation, "search_agents")
    
    def search_teams_resilient(self, **kwargs) -> Dict[str, Any]:
        """Search teams with resilient error handling."""
        def operation():
            return self.client.teams.search_teams(**kwargs)
        
        return self._retry_with_backoff(operation, "search_teams")

# Usage example
resilient_client = ResilientRezenClient(
    max_retries=5,
    base_delay=2.0,
    max_delay=120.0
)

try:
    agents = resilient_client.search_agents_resilient(
        page_size=100,
        state_or_province=["CALIFORNIA"]
    )
    print(f"Successfully retrieved {len(agents.get('agents', []))} agents")
    
except RezenError as e:
    print(f"Failed to retrieve agents after all retries: {e}")
```

---

## 📊 Performance Best Practices

### 1. **Optimize Page Sizes**

```python
# Good: Use appropriate page sizes
agents = client.agents.search_active_agents(page_size=100)  # Efficient

# Avoid: Very small page sizes (more API calls)
agents = client.agents.search_active_agents(page_size=10)   # Inefficient

# Avoid: Very large page sizes (memory issues, timeouts)
agents = client.agents.search_active_agents(page_size=1000) # Risky
```

### 2. **Minimize API Calls**

```python
# Good: Get all needed data in one call
response = client.agents.search_active_agents(
    page_size=100,
    state_or_province=["CALIFORNIA", "TEXAS"],
    name="Smith"
)

# Avoid: Multiple calls for related data
ca_agents = client.agents.search_active_agents(state_or_province=["CALIFORNIA"])
tx_agents = client.agents.search_active_agents(state_or_province=["TEXAS"])
```

### 3. **Use Appropriate Filtering**

```python
# Good: Filter at API level
specific_agents = client.agents.search_active_agents(
    state_or_province=["CALIFORNIA"],
    name="Smith"
)

# Avoid: Over-fetching and filtering locally
all_agents = client.agents.search_active_agents(page_size=1000)
filtered = [a for a in all_agents["agents"] 
           if a.get("stateOrProvince") == "CALIFORNIA" 
           and "Smith" in a.get("lastName", "")]
```

### 4. **Handle Rate Limits Gracefully**

```python
from rezen.exceptions import RateLimitError
import time

def rate_limit_aware_operation(client: RezenClient) -> Dict[str, Any]:
    """Perform operation with rate limit awareness."""
    try:
        return client.agents.search_active_agents(page_size=100)
    except RateLimitError as e:
        # Extract retry-after header if available
        retry_after = getattr(e, 'retry_after', 60)
        print(f"Rate limited, waiting {retry_after} seconds")
        time.sleep(retry_after)
        # Retry the operation
        return client.agents.search_active_agents(page_size=100)
```

---

## 🎯 Production Deployment Tips

### Environment Configuration

```python
import os
from rezen import RezenClient

# Production configuration
def create_production_client() -> RezenClient:
    """Create ReZEN client optimized for production."""
    
    # Validate environment
    api_key = os.getenv("REZEN_API_KEY")
    if not api_key:
        raise ValueError("REZEN_API_KEY environment variable required")
    
    # Create client with production settings
    client = RezenClient(api_key=api_key)
    
    return client

# Health check endpoint
def health_check() -> Dict[str, Any]:
    """Perform health check on ReZEN API connectivity."""
    try:
        client = create_production_client()
        # Simple API call to verify connectivity
        response = client.teams.search_teams(page_size=1)
        
        return {
            "status": "healthy",
            "api_accessible": True,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api_accessible": False,
            "error": str(e),
            "timestamp": time.time()
        }
```

### Monitoring & Alerting

```python
import logging
from typing import Dict, Any
from rezen import RezenClient

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MonitoredRezenClient:
    """ReZEN client with comprehensive monitoring."""
    
    def __init__(self, api_key: str = None):
        self.client = RezenClient(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0.0
        }
    
    def _log_request(
        self,
        method: str,
        params: Dict[str, Any],
        duration: float,
        success: bool,
        error: str = None
    ) -> None:
        """Log request details for monitoring."""
        self.metrics["total_requests"] += 1
        self.metrics["total_response_time"] += duration
        
        if success:
            self.metrics["successful_requests"] += 1
            self.logger.info(
                f"API call successful: {method}, "
                f"duration: {duration:.3f}s, "
                f"params: {params}"
            )
        else:
            self.metrics["failed_requests"] += 1
            self.logger.error(
                f"API call failed: {method}, "
                f"duration: {duration:.3f}s, "
                f"error: {error}, "
                f"params: {params}"
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        total_requests = self.metrics["total_requests"]
        if total_requests > 0:
            avg_response_time = self.metrics["total_response_time"] / total_requests
            success_rate = self.metrics["successful_requests"] / total_requests
        else:
            avg_response_time = 0.0
            success_rate = 0.0
        
        return {
            "total_requests": total_requests,
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "success_rate": success_rate,
            "average_response_time": avg_response_time
        }

# Usage in production
monitored_client = MonitoredRezenClient()

# Periodic metrics reporting
def report_metrics():
    """Report current metrics (call this periodically)."""
    metrics = monitored_client.get_metrics()
    print(f"ReZEN API Metrics: {metrics}")
    
    # Alert on high failure rate
    if metrics["success_rate"] < 0.95 and metrics["total_requests"] > 10:
        print("ALERT: ReZEN API success rate below 95%")
```

---

## 🔍 Troubleshooting Performance Issues

### Common Performance Problems

1. **Slow Response Times**
   - Check network connectivity
   - Verify API endpoint status
   - Review request parameters (large page sizes)
   - Monitor server-side processing time

2. **Memory Usage Issues**
   - Implement pagination for large datasets
   - Use generators instead of loading all data
   - Clear object references after processing
   - Monitor memory usage patterns

3. **Rate Limiting**
   - Implement exponential backoff
   - Respect rate limit headers
   - Consider request batching
   - Use caching for repeated requests

4. **Connection Issues**
   - Implement connection pooling
   - Configure appropriate timeouts
   - Handle network errors gracefully
   - Use retry mechanisms

### Performance Debugging

```python
import cProfile
import pstats
from rezen import RezenClient

def profile_api_operations():
    """Profile API operations to identify bottlenecks."""
    client = RezenClient()
    
    # Profile the operation
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your API operations here
    agents = client.agents.search_active_agents(page_size=100)
    teams = client.teams.search_teams(page_size=50)
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions by cumulative time

# Run profiling
profile_api_operations()
```

---

This performance guide provides comprehensive strategies for optimizing your ReZEN API client usage in production environments. Implement these patterns based on your specific use case and performance requirements.
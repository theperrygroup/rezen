#!/usr/bin/env python3
"""
Sample ReZEN Background Agent

This is a template for creating background agents that use the ReZEN API.
You can customize this script to perform periodic tasks, monitor transactions,
or handle real estate data processing.
"""

import asyncio
import logging
import os
import signal
import sys
import time
import types
from typing import Optional

from rezen import RezenClient


class RezenBackgroundAgent:
    """A background agent for ReZEN API operations.

    This agent runs continuously and performs periodic tasks using the ReZEN API.
    You can extend this class to implement your specific business logic.
    """

    def __init__(self, api_key: Optional[str] = None, interval: int = 60) -> None:
        """Initialize the background agent.

        Args:
            api_key: ReZEN API key. If None, will use REZEN_API_KEY environment variable
            interval: Interval between task executions in seconds (default: 60)
        """
        self.api_key = api_key or os.getenv("REZEN_API_KEY")
        self.interval = interval
        self.client = RezenClient(api_key=self.api_key)
        self.running = False

        # Setup logging
        self.setup_logging()

        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Create logs directory if it doesn't exist
        os.makedirs("/app/logs", exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            handlers=[
                logging.FileHandler("/app/logs/agent.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )

        self.logger = logging.getLogger(__name__)

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum: int, frame: Optional[types.FrameType]) -> None:
            self.logger.info(f"Received signal {signum}. Shutting down gracefully...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def perform_task(self) -> None:
        """Perform the main task of the agent.

        Override this method to implement your specific business logic.
        This example demonstrates basic API calls.
        """
        try:
            self.logger.info("Starting periodic task execution...")

            # Example: Get active agents
            try:
                agents = self.client.agents.search_active_agents(name="")
                self.logger.info(f"Found {len(agents.get('data', []))} active agents")
            except Exception as e:
                self.logger.error(f"Error fetching agents: {e}")

            # Example: Search for active teams
            try:
                teams = self.client.teams.search_teams(status="ACTIVE")
                self.logger.info(f"Found {len(teams.get('data', []))} active teams")
            except Exception as e:
                self.logger.error(f"Error fetching teams: {e}")

            # Example: Search vendors in directory
            try:
                vendors = self.client.directory.search_vendors(
                    page_number=0, page_size=10, is_archived=False
                )
                self.logger.info(f"Found {len(vendors.get('content', []))} vendors")
            except Exception as e:
                self.logger.error(f"Error fetching vendors: {e}")

            self.logger.info("Task execution completed successfully")

        except Exception as e:
            self.logger.error(f"Error during task execution: {e}")

    async def run(self) -> None:
        """Run the background agent continuously."""
        self.logger.info(
            f"Starting ReZEN background agent (interval: {self.interval}s)"
        )
        self.running = True

        while self.running:
            start_time = time.time()

            try:
                await self.perform_task()
            except Exception as e:
                self.logger.error(f"Unexpected error during task execution: {e}")

            # Calculate sleep time to maintain interval
            execution_time = time.time() - start_time
            sleep_time = max(0, self.interval - execution_time)

            if self.running and sleep_time > 0:
                self.logger.debug(f"Sleeping for {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)

        self.logger.info("Background agent stopped")

    def start(self) -> None:
        """Start the background agent."""
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            self.logger.info("Agent interrupted by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            sys.exit(1)


def main() -> None:
    """Main entry point for the agent."""
    # Configuration from environment variables
    api_key = os.getenv("REZEN_API_KEY")
    interval = int(os.getenv("AGENT_INTERVAL", "60"))

    if not api_key:
        print("Error: REZEN_API_KEY environment variable is required")
        sys.exit(1)

    # Create and start the agent
    agent = RezenBackgroundAgent(api_key=api_key, interval=interval)
    agent.start()


if __name__ == "__main__":
    main()

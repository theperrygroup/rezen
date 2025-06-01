#!/usr/bin/env python3
"""
Transaction Monitor Agent

This agent monitors transactions and can perform actions based on transaction status changes.
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
import types
from datetime import datetime
from typing import Any, Dict, Optional, Set

from rezen import RezenClient


class TransactionMonitor:
    """A background agent that monitors ReZEN transactions.

    This agent can track transaction status changes, send notifications,
    or trigger automated workflows based on transaction events.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        interval: int = 300,  # 5 minutes default
        state_file: str = "/app/logs/transaction_state.json",
    ) -> None:
        """Initialize the transaction monitor.

        Args:
            api_key: ReZEN API key. If None, will use REZEN_API_KEY environment variable
            interval: Interval between checks in seconds (default: 300 = 5 minutes)
            state_file: File to store transaction state between runs
        """
        self.api_key = api_key or os.getenv("REZEN_API_KEY")
        self.interval = interval
        self.state_file = state_file
        self.client = RezenClient(api_key=self.api_key)
        self.running = False
        self.last_checked_transactions: Set[str] = set()

        # Setup logging
        self.setup_logging()

        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()

        # Load previous state
        self.load_state()

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
                logging.FileHandler("/app/logs/transaction_monitor.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )

        self.logger = logging.getLogger(__name__)

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum: int, frame: Optional[types.FrameType]) -> None:
            self.logger.info(f"Received signal {signum}. Shutting down gracefully...")
            self.running = False
            self.save_state()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def load_state(self) -> None:
        """Load previous state from file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    self.last_checked_transactions = set(state.get("transactions", []))
                    self.logger.info(
                        f"Loaded {len(self.last_checked_transactions)} transactions from state"
                    )
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
            self.last_checked_transactions = set()

    def save_state(self) -> None:
        """Save current state to file."""
        try:
            state = {
                "transactions": list(self.last_checked_transactions),
                "last_updated": datetime.utcnow().isoformat(),
            }
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)
            self.logger.debug("State saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")

    def process_new_transaction(self, transaction: Dict[str, Any]) -> None:
        """Process a newly discovered transaction.

        Args:
            transaction: Transaction data from the API
        """
        transaction_id = transaction.get("id", "unknown")
        status = transaction.get("status", "unknown")

        self.logger.info(
            f"New transaction detected: {transaction_id} (Status: {status})"
        )

        # Add your custom logic here
        # Examples:
        # - Send notifications for high-value transactions
        # - Check for missing documents
        # - Update external systems
        # - Generate reports

        # Example: Log important transaction details
        if "amount" in transaction:
            amount = transaction["amount"]
            self.logger.info(f"Transaction {transaction_id} amount: ${amount:,.2f}")

        if status.lower() in ["pending", "under_contract"]:
            self.logger.warning(
                f"Transaction {transaction_id} requires attention (Status: {status})"
            )

    def process_transaction_update(
        self, transaction: Dict[str, Any], previous_status: str
    ) -> None:
        """Process a transaction status update.

        Args:
            transaction: Updated transaction data
            previous_status: Previous status of the transaction
        """
        transaction_id = transaction.get("id", "unknown")
        current_status = transaction.get("status", "unknown")

        self.logger.info(
            f"Transaction {transaction_id} status changed: {previous_status} -> {current_status}"
        )

        # Add your custom logic for status changes
        # Examples:
        # - Send alerts for critical status changes
        # - Trigger automated workflows
        # - Update tracking systems
        # - Generate status reports

    async def monitor_transactions(self) -> None:
        """Monitor transactions for changes."""
        try:
            self.logger.info("Checking for transaction updates...")

            # This is a simplified example - you might want to implement pagination
            # and date filtering for production use
            try:
                # Note: You'll need to implement actual transaction fetching
                # This is a placeholder showing the structure

                # Example of how you might search for recent transactions
                # transactions = self.client.transactions.search_transactions(
                #     date_from=(datetime.utcnow() - timedelta(days=7)).isoformat(),
                #     date_to=datetime.utcnow().isoformat()
                # )

                # For now, we'll just log that we're monitoring
                self.logger.info(
                    "Monitoring active... (implement actual transaction fetching)"
                )

                # Placeholder for transaction processing logic
                current_transactions: Set[str] = set()

                # Save updated state
                self.last_checked_transactions = current_transactions
                self.save_state()

            except Exception as e:
                self.logger.error(f"Error fetching transactions: {e}")

        except Exception as e:
            self.logger.error(f"Error during transaction monitoring: {e}")

    async def run(self) -> None:
        """Run the transaction monitor continuously."""
        self.logger.info(f"Starting transaction monitor (interval: {self.interval}s)")
        self.running = True

        while self.running:
            start_time = time.time()

            try:
                await self.monitor_transactions()
            except Exception as e:
                self.logger.error(f"Unexpected error during monitoring: {e}")

            # Calculate sleep time to maintain interval
            execution_time = time.time() - start_time
            sleep_time = max(0, self.interval - execution_time)

            if self.running and sleep_time > 0:
                self.logger.debug(f"Sleeping for {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)

        self.logger.info("Transaction monitor stopped")

    def start(self) -> None:
        """Start the transaction monitor."""
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            self.logger.info("Monitor interrupted by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            sys.exit(1)


def main() -> None:
    """Main entry point for the transaction monitor."""
    # Configuration from environment variables
    api_key = os.getenv("REZEN_API_KEY")
    interval = int(os.getenv("MONITOR_INTERVAL", "300"))  # 5 minutes default

    if not api_key:
        print("Error: REZEN_API_KEY environment variable is required")
        sys.exit(1)

    # Create and start the monitor
    monitor = TransactionMonitor(api_key=api_key, interval=interval)
    monitor.start()


if __name__ == "__main__":
    main()

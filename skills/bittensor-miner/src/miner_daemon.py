#!/usr/bin/env python3
"""
Bittensor Miner Daemon
Main process that runs 24/7, listening for tasks and coordinating responses.
Phase 1: Stub implementation with socket IPC and basic task flow.
"""

import json
import logging
import signal
import sys
import time
import socket
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from utils.bittensor_client import BittensorClientWrapper
from wallet_manager import WalletManager

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "miner.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class MinerDaemon:
    """
    Main miner daemon process.
    Listens for tasks, routes to task_handler, returns responses.
    """

    def __init__(self, config_path: str = "config/miner-config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.running = False
        self.tasks_processed = 0
        self.socket = None

        # Initialize components
        self.bittensor = None
        self.wallet = WalletManager()
        self.state_file = Path("state/miner-state.json")

        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info("MinerDaemon initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Config loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config: {e}")
            sys.exit(1)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received shutdown signal {signum}")
        self.running = False
        self.shutdown()
        sys.exit(0)

    def _save_state(self) -> None:
        """Save daemon state to file"""
        try:
            state = {
                'status': 'running' if self.running else 'stopped',
                'daemon_pid': os.getpid(),
                'socket_path': self.config['daemon']['socket_path'],
                'last_task_received': None,  # Phase 1
                'tasks_processed': self.tasks_processed,
                'uptime_seconds': int(time.time()),
            }
            self.state_file.parent.mkdir(exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def initialize(self) -> bool:
        """
        Initialize all components.
        Phase 1: Basic Bittensor client setup.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Initializing miner daemon...")

        # Initialize wallet
        if not self.wallet.start_mcp_server():
            logger.error("Failed to start wallet MCP server")
            return False

        # Initialize Bittensor client
        bittensor_config = self.config['bittensor']
        self.bittensor = BittensorClientWrapper(
            wallet_name=bittensor_config['wallet_name'],
            hotkey=bittensor_config['hotkey'],
            subnet_id=bittensor_config['subnet_id'],
            network=bittensor_config['network']
        )

        if not self.bittensor.initialize():
            logger.error("Failed to initialize Bittensor client")
            return False

        # Check registration
        if not self.bittensor.is_registered():
            logger.error(
                f"Hotkey not registered to subnet {bittensor_config['subnet_id']}\n"
                "Register with: btcli subnet register --wallet.name openclawd-miner --subnet.id 1"
            )
            return False

        logger.info("✅ All components initialized")
        return True

    def setup_ipc_socket(self) -> bool:
        """
        Setup Unix socket for IPC communication with task_handler.
        Phase 1: Basic socket setup.

        Returns:
            True if successful, False otherwise
        """
        try:
            socket_path = self.config['daemon']['socket_path']
            logger.info(f"Setting up IPC socket at {socket_path}...")

            # Remove existing socket file if present
            if os.path.exists(socket_path):
                os.remove(socket_path)

            # Create Unix socket
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.bind(socket_path)
            self.socket.listen(1)

            logger.info(f"✅ IPC socket ready at {socket_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to setup IPC socket: {e}")
            return False

    def run(self) -> None:
        """
        Main daemon loop.
        Phase 1: Stub - logs that it's running.
        """
        if not self.initialize():
            logger.error("Initialization failed")
            return

        if not self.setup_ipc_socket():
            logger.error("IPC socket setup failed")
            return

        self.running = True
        self._save_state()

        logger.info("=" * 60)
        logger.info("🤖 BITTENSOR MINER DAEMON STARTED")
        logger.info(f"   Subnet: {self.config['bittensor']['subnet_id']}")
        logger.info(f"   Network: {self.config['bittensor']['network']}")
        logger.info(f"   Socket: {self.config['daemon']['socket_path']}")
        logger.info("=" * 60)

        try:
            while self.running:
                logger.info("Waiting for tasks...")
                # Phase 1: Mock task receiving
                # In real implementation, would listen on socket and poll Bittensor

                # Simulate task reception every 10 seconds
                time.sleep(10)
                logger.debug(f"Status: {self.tasks_processed} tasks processed")

                self._save_state()

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Daemon error: {e}", exc_info=True)
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Shutdown the daemon gracefully"""
        logger.info("Shutting down miner daemon...")
        self.running = False

        if self.socket:
            try:
                self.socket.close()
                if os.path.exists(self.config['daemon']['socket_path']):
                    os.remove(self.config['daemon']['socket_path'])
            except Exception as e:
                logger.error(f"Error closing socket: {e}")

        if self.bittensor:
            self.bittensor.shutdown()

        if self.wallet:
            self.wallet.stop_mcp_server()

        self._save_state()
        logger.info("✅ Daemon shutdown complete")


def main():
    """Entry point for miner daemon"""
    daemon = MinerDaemon()
    daemon.run()


if __name__ == "__main__":
    main()

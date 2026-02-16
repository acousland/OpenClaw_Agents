"""Bittensor Miner Skill for OpenClawd"""

__version__ = "1.0.0-alpha"
__author__ = "Patrick (OpenClawd)"

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Bittensor Miner Skill loaded")

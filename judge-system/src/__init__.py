"""
Judge System - A modular monolith architecture for problem solving platform

This package provides:
- Core domain: Problem management, test cases, user management
- Judge domain: Code execution, evaluation, result management
- Shared infrastructure: Database, logging, authentication
"""

__version__ = "1.0.0"
__author__ = "Judge System Team"

import logging
import sys
from pathlib import Path

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path.home() / ".python-problem" / "app.log"),
    ],
)

logger = logging.getLogger(__name__)
logger.info(f"Judge System v{__version__} initialized")

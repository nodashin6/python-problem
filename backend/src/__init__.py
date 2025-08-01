"""
Judge System - A modular monolith architecture for problem solving platform

This package provides:
- Core domain: Problem management, test cases, user management
- Judge domain: Code execution, evaluation, result management
- Shared infrastructure: Database, logging, authentication
"""

import logging
import sys
from pathlib import Path

try:
    from .const import LOGS_DIR
except ImportError:
    # Fallback when running directly
    LOGS_DIR = Path(__file__).parent.parent / "app_data" / "logs"

# Version from pyproject.toml
__version__ = "0.2.0"

__author__ = "nodashin"


log_path: Path = LOGS_DIR / "app.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
if not log_path.exists():
    log_path.touch()
# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path, mode="a", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)
logger.info(f"Judge System v{__version__} initialized")

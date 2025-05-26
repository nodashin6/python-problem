"""
Core Domain API Layer
コアドメインAPI層

Author: Judge System Team
Date: 2025-01-12
"""

from .routes import core_router
from .middleware import setup_core_middleware

__all__ = ["core_router", "setup_core_middleware"]

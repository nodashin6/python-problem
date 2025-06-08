"""
Core Domain API Layer
コアドメインAPI層

Author: Judge System Team
Date: 2025-01-12
"""

from .routers import core_router

__all__ = ["core_router", "setup_core_middleware"]

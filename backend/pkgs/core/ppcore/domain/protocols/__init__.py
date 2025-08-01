"""
Core Domain Protocols
コアドメインプロトコル
"""

from .database_protocols import DatabaseConfig, DatabaseHealthCheck, DatabaseTransaction

__all__ = [
    "DatabaseConfig",
    "DatabaseHealthCheck", 
    "DatabaseTransaction",
]
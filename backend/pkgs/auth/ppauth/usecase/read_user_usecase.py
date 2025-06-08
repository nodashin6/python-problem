# filepath: /mnt/d/nodashin/python-problem/backend/pkgs/auth/ppauth/usecase/read_user_usecase.py
"""
Compatibility module for importing read user use cases.
This module re-exports all user reading use cases from their individual files.
"""

# Import individual use cases
from .read_user_by_email_usecase import (
    ReadUserByEmailCommand,
    ReadUserByEmailResult,
    ReadUserByEmailUseCase,
)
from .read_user_by_id_usecase import (
    ReadUserByIdCommand,
    ReadUserByIdResult,
    ReadUserByIdUseCase,
)
from .read_users_by_role_usecase import (
    ReadUsersByRoleCommand,
    ReadUsersByRoleResult,
    ReadUsersByRoleUseCase,
)
from .user_types import ReadUserListResult, UserResult

__all__ = [
    # New naming convention
    "ReadUserByIdCommand",
    "ReadUserByIdUseCase",
    "ReadUserByIdResult",
    "ReadUserByEmailCommand",
    "ReadUserByEmailUseCase",
    "ReadUserByEmailResult",
    "ReadUsersByRoleCommand",
    "ReadUsersByRoleUseCase",
    "ReadUsersByRoleResult",
    # Common types
    "UserResult",
    "ReadUserListResult",
    "ReadUserListResult",
]

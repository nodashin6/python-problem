"""
Use cases for PPAuth
"""

from .create_user_usecase import CreateUserCommand, CreateUserResult, CreateUserUseCase
from .delete_user_usecase import DeleteUserCommand, DeleteUserResult, DeleteUserUseCase
from .read_user_usecase import (
    ReadUserByEmailCommand,
    ReadUserByEmailUseCase,
    ReadUserByIdCommand,
    ReadUserByIdUseCase,
    ReadUserListResult,
    ReadUsersByRoleCommand,
    ReadUsersByRoleUseCase,
    UserResult,
)
from .update_user_usecase import UpdateUserCommand, UpdateUserResult, UpdateUserUseCase

__all__ = [
    # Create
    "CreateUserCommand",
    "CreateUserResult",
    "CreateUserUseCase",
    # Update
    "UpdateUserCommand",
    "UpdateUserResult",
    "UpdateUserUseCase",
    # Delete
    "DeleteUserCommand",
    "DeleteUserResult",
    "DeleteUserUseCase",
    # Read
    "ReadUserByIdCommand",
    "ReadUserByEmailCommand",
    "ReadUsersByRoleCommand",
    "UserResult",
    "ReadUserListResult",
    "ReadUserByIdUseCase",
    "ReadUserByEmailUseCase",
    "ReadUsersByRoleUseCase",
]

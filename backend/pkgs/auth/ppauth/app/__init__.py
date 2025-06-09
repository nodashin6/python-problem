"""
App module for PPAuth
"""

from .api import auth_router
from .dependencies import (
    get_auth_service,
    get_create_user_usecase,
    get_current_user,
    get_delete_user_usecase,
    get_read_active_users_usecase,
    get_read_user_by_email_usecase,
    get_read_user_by_id_usecase,
    get_read_users_by_role_usecase,
    get_update_user_usecase,
    get_user_service,
    require_admin,
    require_moderator_or_admin,
)

__all__ = [
    "auth_router",
    "get_current_user",
    "require_admin",
    "require_moderator_or_admin",
    "get_auth_service",
    "get_user_service",
    "get_create_user_usecase",
    "get_update_user_usecase",
    "get_delete_user_usecase",
    "get_read_user_by_id_usecase",
    "get_read_user_by_email_usecase",
    "get_read_users_by_role_usecase",
    "get_read_active_users_usecase",
]

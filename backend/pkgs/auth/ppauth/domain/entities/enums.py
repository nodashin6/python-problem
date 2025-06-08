from enum import Enum


# Core Domain Enums
class UserRole(str, Enum):
    """ユーザーロール - SQLのuser_roles.roleと対応"""

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """権限"""

    # 問題管理
    PROBLEM_CREATE = "problem:create"
    PROBLEM_READ = "problem:read"
    PROBLEM_UPDATE = "problem:update"
    PROBLEM_DELETE = "problem:delete"

    # テストケース管理
    JUDGECASE_CREATE = "judgecase:create"
    JUDGECASE_READ = "judgecase:read"
    JUDGECASE_UPDATE = "judgecase:update"
    JUDGECASE_DELETE = "judgecase:delete"

    # 提出管理
    SUBMISSION_CREATE = "submission:create"
    SUBMISSION_READ = "submission:read"
    SUBMISSION_READ_ALL = "submission:read_all"
    SUBMISSION_DELETE = "submission:delete"

    # ジャッジ管理
    JUDGE_EXECUTE = "judge:execute"
    JUDGE_READ = "judge:read"
    JUDGE_READ_ALL = "judge:read_all"
    JUDGE_MANAGE = "judge:manage"

    # ユーザー管理
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"

    # システム管理
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_MONITOR = "system:monitor"


# ロールと権限のマッピング
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.PROBLEM_CREATE,
        Permission.PROBLEM_READ,
        Permission.PROBLEM_UPDATE,
        Permission.PROBLEM_DELETE,
        Permission.JUDGECASE_CREATE,
        Permission.JUDGECASE_READ,
        Permission.JUDGECASE_UPDATE,
        Permission.JUDGECASE_DELETE,
        Permission.SUBMISSION_CREATE,
        Permission.SUBMISSION_READ,
        Permission.SUBMISSION_READ_ALL,
        Permission.SUBMISSION_DELETE,
        Permission.JUDGE_EXECUTE,
        Permission.JUDGE_READ,
        Permission.JUDGE_READ_ALL,
        Permission.JUDGE_MANAGE,
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.USER_MANAGE_ROLES,
        Permission.SYSTEM_ADMIN,
        Permission.SYSTEM_MONITOR,
    ],
    UserRole.MODERATOR: [
        Permission.PROBLEM_READ,
        Permission.PROBLEM_UPDATE,
        Permission.JUDGECASE_READ,
        Permission.JUDGECASE_UPDATE,
        Permission.SUBMISSION_READ,
        Permission.SUBMISSION_READ_ALL,
        Permission.JUDGE_READ,
        Permission.JUDGE_READ_ALL,
        Permission.USER_READ,
        Permission.SYSTEM_MONITOR,
    ],
    UserRole.USER: [
        Permission.PROBLEM_READ,
        Permission.JUDGECASE_READ,
        Permission.SUBMISSION_CREATE,
        Permission.SUBMISSION_READ,
        Permission.JUDGE_EXECUTE,
        Permission.JUDGE_READ,
    ],
    UserRole.GUEST: [
        Permission.PROBLEM_READ,
        Permission.JUDGECASE_READ,
    ],
}

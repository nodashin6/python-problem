from enum import Enum, StrEnum


# Core Domain Enums
class UserRole(StrEnum):
    """ユーザーロール - SQLのuser_roles.roleと対応"""

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """権限"""

    # 問題 ~ judge の情報は、拡張パッケージ側で管理する判断であるため、ここでは定義しない
    # # 問題管理
    # PROBLEM_CREATE = "problem:create"
    # PROBLEM_READ = "problem:read"
    # PROBLEM_UPDATE = "problem:update"
    # PROBLEM_DELETE = "problem:delete"

    # # テストケース管理
    # JUDGECASE_CREATE = "judgecase:create"
    # JUDGECASE_READ = "judgecase:read"
    # JUDGECASE_UPDATE = "judgecase:update"
    # JUDGECASE_DELETE = "judgecase:delete"

    # # 提出管理
    # SUBMISSION_CREATE = "submission:create"
    # SUBMISSION_READ = "submission:read"
    # SUBMISSION_READ_ALL = "submission:read_all"
    # SUBMISSION_DELETE = "submission:delete"

    # # ジャッジ管理
    # JUDGE_EXECUTE = "judge:execute"
    # JUDGE_READ = "judge:read"
    # JUDGE_READ_ALL = "judge:read_all"
    # JUDGE_MANAGE = "judge:manage"

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
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.USER_MANAGE_ROLES,
        Permission.SYSTEM_ADMIN,
        Permission.SYSTEM_MONITOR,
    ],
    UserRole.MODERATOR: [
        Permission.USER_READ,
        Permission.SYSTEM_MONITOR,
    ],
    UserRole.USER: [
        Permission.USER_READ,
        Permission.USER_UPDATE,
    ],
    UserRole.GUEST: [
        Permission.USER_READ,
    ],
}

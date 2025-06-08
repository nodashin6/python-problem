from enum import Enum


class Environment(str, Enum):
    """実行環境"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

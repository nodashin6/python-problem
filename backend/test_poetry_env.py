#!/usr/bin/env python3
"""Test script to verify poetry environment is working correctly"""

import sys

print(f"Python executable: {sys.executable}")

try:
    import pydddi

    print("✅ pydddi imported successfully")
    print(f"   pydddi version: {getattr(pydddi, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ Failed to import pydddi: {e}")
    exit(1)

try:
    from pkgs.auth.ppauth.usecase.read_users_by_role_usecase import ReadUsersByRoleUseCase

    print("✅ ReadUsersByRoleUseCase imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ReadUsersByRoleUseCase: {e}")
    exit(1)

try:
    from pkgs.auth.ppauth.domain.entities.user.user_entity import UserEntity

    print("✅ UserEntity imported successfully")
except ImportError as e:
    print(f"❌ Failed to import UserEntity: {e}")
    exit(1)

print("\n🎉 All imports successful! Poetry environment is working correctly.")

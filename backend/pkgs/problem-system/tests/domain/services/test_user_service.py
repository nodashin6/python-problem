"""
User domain service unit tests
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.const import UserRole
from src.core.domain.models import User, UserProfile
from src.core.domain.repositories import UserRepository
from src.core.domain.services.user_service import UserDomainService
from src.shared.auth import JWTManager, PasswordManager
from src.shared.events import EventBus


@pytest.mark.core
class TestUserDomainService:
    """UserDomainServiceのテスト"""

    @pytest.fixture
    def mock_user_repo(self):
        """モックUserRepositoryを作成"""
        repo = AsyncMock(spec=UserRepository)
        return repo

    @pytest.fixture
    def mock_password_manager(self):
        """モックPasswordManagerを作成"""
        manager = MagicMock(spec=PasswordManager)
        manager.hash_password.return_value = "hashed_password"
        manager.verify_password.return_value = True
        return manager

    @pytest.fixture
    def mock_token_manager(self):
        """モックJWTManagerを作成"""
        manager = MagicMock(spec=JWTManager)
        return manager

    @pytest.fixture
    def mock_event_bus(self):
        """モックEventBusを作成"""
        bus = AsyncMock(spec=EventBus)
        return bus

    @pytest.fixture
    def user_service(self, mock_user_repo, mock_password_manager, mock_token_manager, mock_event_bus):
        """UserDomainServiceのインスタンスを作成"""
        return UserDomainService(
            user_repo=mock_user_repo,
            password_manager=mock_password_manager,
            token_manager=mock_token_manager,
            event_bus=mock_event_bus,
        )

    @pytest.mark.asyncio
    async def test_is_email_available_true(self, user_service, mock_user_repo):
        """メールアドレス利用可能のテスト"""
        # モックの設定
        mock_user_repo.exists_by_email.return_value = False

        # テスト実行
        result = await user_service.is_email_available("test@example.com")

        # アサート
        assert result is True
        mock_user_repo.exists_by_email.assert_called_once_with("test@example.com")

    @pytest.mark.asyncio
    async def test_is_email_available_false(self, user_service, mock_user_repo):
        """メールアドレス利用不可のテスト"""
        # モックの設定
        mock_user_repo.exists_by_email.return_value = True

        # テスト実行
        result = await user_service.is_email_available("existing@example.com")

        # アサート
        assert result is False

    @pytest.mark.asyncio
    async def test_is_username_available_true(self, user_service, mock_user_repo):
        """ユーザー名利用可能のテスト"""
        # モックの設定
        mock_user_repo.exists_by_username.return_value = False

        # テスト実行
        result = await user_service.is_username_available("newuser")

        # アサート
        assert result is True
        mock_user_repo.exists_by_username.assert_called_once_with("newuser")

    @pytest.mark.asyncio
    async def test_is_username_available_false(self, user_service, mock_user_repo):
        """ユーザー名利用不可のテスト"""
        # モックの設定
        mock_user_repo.exists_by_username.return_value = True

        # テスト実行
        result = await user_service.is_username_available("existinguser")

        # アサート
        assert result is False

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, user_service, mock_user_repo, mock_password_manager, mock_event_bus
    ):
        """ユーザー登録成功のテスト"""
        profile = UserProfile(display_name="Test User")

        # モックの設定
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.exists_by_username.return_value = False
        mock_user_repo.create.return_value = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
        )

        # テスト実行
        result = await user_service.register_user(
            email="test@example.com",
            username="testuser",
            password="password123",
            profile=profile,
        )

        # アサート
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.role == UserRole.USER
        mock_password_manager.hash_password.assert_called_once_with("password123")
        mock_user_repo.create.assert_called_once()
        mock_event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, user_service, mock_user_repo):
        """ユーザー登録時のメールアドレス重複エラーのテスト"""
        profile = UserProfile(display_name="Test User")

        # モックの設定
        mock_user_repo.exists_by_email.return_value = True

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Email already exists"):
            await user_service.register_user(
                email="existing@example.com",
                username="testuser",
                password="password123",
                profile=profile,
            )

    @pytest.mark.asyncio
    async def test_register_user_username_exists(self, user_service, mock_user_repo):
        """ユーザー登録時のユーザー名重複エラーのテスト"""
        profile = UserProfile(display_name="Test User")

        # モックの設定
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.exists_by_username.return_value = True

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Username already exists"):
            await user_service.register_user(
                email="test@example.com",
                username="existinguser",
                password="password123",
                profile=profile,
            )

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, user_service, mock_user_repo, mock_password_manager):
        """ユーザー認証成功のテスト"""
        profile = UserProfile(display_name="Test User")
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
            is_active=True,
        )

        # モックの設定
        mock_user_repo.find_by_email.return_value = user
        mock_password_manager.verify_password.return_value = True

        # テスト実行
        result = await user_service.authenticate_user("test@example.com", "password123")

        # アサート
        assert result == user
        mock_user_repo.update_last_login.assert_called_once_with(user.id)

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, user_service, mock_user_repo):
        """ユーザー認証失敗 (ユーザー不存在) のテスト"""
        # モックの設定
        mock_user_repo.find_by_email.return_value = None

        # テスト実行
        result = await user_service.authenticate_user("nonexistent@example.com", "password123")

        # アサート
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, user_service, mock_user_repo):
        """ユーザー認証失敗 (無効化ユーザー) のテスト"""
        profile = UserProfile(display_name="Test User")
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
            is_active=False,
        )

        # モックの設定
        mock_user_repo.find_by_email.return_value = user

        # テスト実行
        result = await user_service.authenticate_user("test@example.com", "password123")

        # アサート
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, user_service, mock_user_repo, mock_password_manager
    ):
        """ユーザー認証失敗 (パスワード不一致) のテスト"""
        profile = UserProfile(display_name="Test User")
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
            is_active=True,
        )

        # モックの設定
        mock_user_repo.find_by_email.return_value = user
        mock_password_manager.verify_password.return_value = False

        # テスト実行
        result = await user_service.authenticate_user("test@example.com", "wrongpassword")

        # アサート
        assert result is None

    @pytest.mark.asyncio
    async def test_change_password_success(self, user_service, mock_user_repo, mock_password_manager):
        """パスワード変更成功のテスト"""
        user_id = uuid4()
        profile = UserProfile(display_name="Test User")
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="old_hashed_password",
            profile=profile,
        )

        # モックの設定
        mock_user_repo.get.return_value = user
        mock_password_manager.verify_password.return_value = True
        mock_password_manager.hash_password.return_value = "new_hashed_password"

        # テスト実行
        result = await user_service.change_password(user_id, "oldpassword", "newpassword")

        # アサート
        assert result is True
        mock_password_manager.verify_password.assert_called_once_with("oldpassword", "old_hashed_password")
        mock_password_manager.hash_password.assert_called_once_with("newpassword")
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, user_service, mock_user_repo):
        """パスワード変更失敗 (ユーザー不存在) のテスト"""
        user_id = uuid4()

        # モックの設定
        mock_user_repo.get.return_value = None

        # テスト実行
        result = await user_service.change_password(user_id, "oldpassword", "newpassword")

        # アサート
        assert result is False

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(
        self, user_service, mock_user_repo, mock_password_manager
    ):
        """パスワード変更失敗 (旧パスワード不一致) のテスト"""
        user_id = uuid4()
        profile = UserProfile(display_name="Test User")
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="old_hashed_password",
            profile=profile,
        )

        # モックの設定
        mock_user_repo.get.return_value = user
        mock_password_manager.verify_password.return_value = False

        # テスト実行
        result = await user_service.change_password(user_id, "wrongoldpassword", "newpassword")

        # アサート
        assert result is False

    @pytest.mark.asyncio
    async def test_update_user_profile(self, user_service, mock_user_repo):
        """ユーザープロフィール更新のテスト"""
        user_id = uuid4()
        old_profile = UserProfile(display_name="Old Name")
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=old_profile,
        )

        new_profile = UserProfile(display_name="New Name", bio="New bio", github_username="newusername")

        # モックの設定
        mock_user_repo.get.return_value = user

        # テスト実行
        result = await user_service.update_user_profile(user_id, new_profile)

        # アサート
        assert result.profile.display_name == "New Name"
        assert result.profile.bio == "New bio"
        assert result.profile.github_username == "newusername"
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_profile_not_found(self, user_service, mock_user_repo):
        """ユーザープロフィール更新失敗 (ユーザー不存在) のテスト"""
        user_id = uuid4()
        new_profile = UserProfile(display_name="New Name")

        # モックの設定
        mock_user_repo.get.return_value = None

        # テスト実行とアサート
        with pytest.raises(ValueError, match="User not found"):
            await user_service.update_user_profile(user_id, new_profile)

    @pytest.mark.asyncio
    async def test_verify_user_email(self, user_service, mock_user_repo):
        """ユーザーメール認証のテスト"""
        user_id = uuid4()
        profile = UserProfile(display_name="Test User")
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
            is_verified=False,
        )

        # モックの設定
        mock_user_repo.get.return_value = user

        # テスト実行
        result = await user_service.verify_user_email(user_id)

        # アサート
        assert result.is_verified is True
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_user(self, user_service, mock_user_repo):
        """ユーザー無効化のテスト"""
        user_id = uuid4()
        profile = UserProfile(display_name="Test User")
        user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
            is_active=True,
        )

        # モックの設定
        mock_user_repo.get.return_value = user

        # テスト実行
        result = await user_service.deactivate_user(user_id)

        # アサート
        assert result.is_active is False
        mock_user_repo.update.assert_called_once()

"""
Core domain models unit tests
"""

import pytest
from uuid import uuid4
from datetime import datetime

from src.core.domain.models import (
    User,
    Problem,
    Book,
    JudgeCase,
    ProblemContent,
    Editorial,
    EditorialContent,
    Tag,
    ProblemMetadata,
    UserProfile,
    UserRegistered,
    ProblemCreated,
    ProblemPublished,
    JudgeCaseAdded,
)
from src.const import DifficultyLevel, ProblemStatus, UserRole, JudgeCaseType


@pytest.mark.core
class TestValueObjects:
    """Value objectsのテスト"""

    def test_tag_creation(self):
        """Tagの作成をテスト"""
        tag = Tag(name="algorithms", color="#FF5733")
        assert tag.name == "algorithms"
        assert tag.color == "#FF5733"

    def test_tag_name_normalization(self):
        """Tagの名前正規化をテスト"""
        tag = Tag(name="  ALGORITHMS  ")
        assert tag.name == "algorithms"

    def test_tag_invalid_color(self):
        """不正なカラーコードでのTag作成をテスト"""
        with pytest.raises(ValueError):
            Tag(name="test", color="invalid")

    def test_problem_metadata_defaults(self):
        """ProblemMetadataのデフォルト値をテスト"""
        metadata = ProblemMetadata()
        assert metadata.time_limit_ms == 2000
        assert metadata.memory_limit_mb == 256
        assert metadata.hints == []

    def test_problem_metadata_validation(self):
        """ProblemMetadataのバリデーションをテスト"""
        with pytest.raises(ValueError):
            ProblemMetadata(time_limit_ms=50)  # 100未満

        with pytest.raises(ValueError):
            ProblemMetadata(memory_limit_mb=8)  # 16未満

    def test_user_profile_creation(self):
        """UserProfileの作成をテスト"""
        profile = UserProfile(
            display_name="Test User", bio="Test bio", github_username="testuser"
        )
        assert profile.display_name == "Test User"
        assert profile.preferred_language == "ja"


@pytest.mark.core
class TestUser:
    """Userエンティティのテスト"""

    def test_user_creation(self):
        """ユーザー作成をテスト"""
        profile = UserProfile(display_name="Test User")
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.is_verified is False
        assert len(user._events) == 1
        assert isinstance(user._events[0], UserRegistered)

    def test_user_email_validation(self):
        """メールアドレスのバリデーションをテスト"""
        profile = UserProfile(display_name="Test User")
        with pytest.raises(ValueError):
            User(
                email="invalid-email",
                username="testuser",
                password_hash="hashed_password",
                profile=profile,
            )

    def test_user_update_profile(self):
        """プロフィール更新をテスト"""
        profile = UserProfile(display_name="Old Name")
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
        )

        new_profile = UserProfile(display_name="New Name")
        old_updated_at = user.updated_at

        user.update_profile(new_profile)

        assert user.profile.display_name == "New Name"
        assert user.updated_at > old_updated_at

    def test_user_verify_email(self):
        """メール認証をテスト"""
        profile = UserProfile(display_name="Test User")
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
        )

        assert user.is_verified is False
        user.verify_email()
        assert user.is_verified is True

    def test_user_deactivate(self):
        """ユーザー無効化をテスト"""
        profile = UserProfile(display_name="Test User")
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
        )

        assert user.is_active is True
        user.deactivate()
        assert user.is_active is False


@pytest.mark.core
class TestProblem:
    """Problemエンティティのテスト"""

    def test_problem_creation(self):
        """問題作成をテスト"""
        author_id = uuid4()
        problem = Problem(
            title="Test Problem", description="Test description", author_id=author_id
        )

        assert problem.title == "Test Problem"
        assert problem.description == "Test description"
        assert problem.difficulty == DifficultyLevel.EASY
        assert problem.status == ProblemStatus.DRAFT
        assert problem.submission_count == 0
        assert problem.accepted_count == 0
        assert len(problem._events) == 1
        assert isinstance(problem._events[0], ProblemCreated)

    def test_problem_acceptance_rate(self):
        """受理率計算をテスト"""
        problem = Problem(
            title="Test Problem", description="Test description", author_id=uuid4()
        )

        # 初期状態
        assert problem.acceptance_rate == 0.0

        # 統計更新
        problem.update_statistics(100, 80)
        assert problem.acceptance_rate == 80.0

    def test_problem_add_tag(self):
        """タグ追加をテスト"""
        problem = Problem(
            title="Test Problem", description="Test description", author_id=uuid4()
        )

        tag = Tag(name="algorithms")
        problem.add_tag(tag)

        assert tag in problem.tags

    def test_problem_remove_tag(self):
        """タグ削除をテスト"""
        problem = Problem(
            title="Test Problem", description="Test description", author_id=uuid4()
        )

        tag = Tag(name="algorithms")
        problem.add_tag(tag)
        problem.remove_tag("algorithms")

        assert tag not in problem.tags

    def test_problem_publish(self):
        """問題公開をテスト"""
        problem = Problem(
            title="Test Problem", description="Test description", author_id=uuid4()
        )

        assert problem.status == ProblemStatus.DRAFT
        problem.publish()

        assert problem.status == ProblemStatus.PUBLISHED
        # ProblemPublishedイベントが追加されているかチェック
        published_events = [
            e for e in problem._events if isinstance(e, ProblemPublished)
        ]
        assert len(published_events) == 1

    def test_problem_archive(self):
        """問題アーカイブをテスト"""
        problem = Problem(
            title="Test Problem", description="Test description", author_id=uuid4()
        )

        problem.archive()
        assert problem.status == ProblemStatus.ARCHIVED


@pytest.mark.core
class TestBook:
    """Bookエンティティのテスト"""

    def test_book_creation(self):
        """問題集作成をテスト"""
        book = Book(
            title="Test Book", description="Test description", author_id=uuid4()
        )

        assert book.title == "Test Book"
        assert book.description == "Test description"
        assert book.is_published is False

    def test_book_publish(self):
        """問題集公開をテスト"""
        book = Book(title="Test Book", author_id=uuid4())

        book.publish()
        assert book.is_published is True

    def test_book_unpublish(self):
        """問題集非公開をテスト"""
        book = Book(title="Test Book", author_id=uuid4())

        book.publish()
        book.unpublish()
        assert book.is_published is False


@pytest.mark.core
class TestJudgeCase:
    """JudgeCaseエンティティのテスト"""

    def test_judge_case_creation(self):
        """ジャッジケース作成をテスト"""
        problem_id = uuid4()
        judge_case = JudgeCase(
            problem_id=problem_id,
            name="Test Case",
            input_data="test input",
            expected_output="test output",
        )

        assert judge_case.problem_id == problem_id
        assert judge_case.name == "Test Case"
        assert judge_case.case_type == JudgeCaseType.HIDDEN
        assert judge_case.points == 1
        assert len(judge_case._events) == 1
        assert isinstance(judge_case._events[0], JudgeCaseAdded)

    def test_judge_case_make_sample(self):
        """サンプルケース化をテスト"""
        judge_case = JudgeCase(
            problem_id=uuid4(),
            name="Test Case",
            input_data="test input",
            expected_output="test output",
        )

        judge_case.make_sample()
        assert judge_case.case_type == JudgeCaseType.SAMPLE

    def test_judge_case_make_hidden(self):
        """隠しケース化をテスト"""
        judge_case = JudgeCase(
            problem_id=uuid4(),
            name="Test Case",
            input_data="test input",
            expected_output="test output",
            case_type=JudgeCaseType.SAMPLE,
        )

        judge_case.make_hidden()
        assert judge_case.case_type == JudgeCaseType.HIDDEN


@pytest.mark.core
class TestProblemContent:
    """ProblemContentエンティティのテスト"""

    def test_problem_content_creation(self):
        """問題コンテンツ作成をテスト"""
        content = ProblemContent(
            problem_id=uuid4(),
            language="ja",
            title="テスト問題",
            description="問題の説明",
        )

        assert content.language == "ja"
        assert content.title == "テスト問題"
        assert content.description == "問題の説明"


@pytest.mark.core
class TestEditorial:
    """Editorialエンティティのテスト"""

    def test_editorial_creation(self):
        """解説作成をテスト"""
        editorial = Editorial(problem_id=uuid4(), author_id=uuid4())

        assert editorial.is_published is False

    def test_editorial_publish(self):
        """解説公開をテスト"""
        editorial = Editorial(problem_id=uuid4(), author_id=uuid4())

        editorial.publish()
        assert editorial.is_published is True


@pytest.mark.core
class TestEditorialContent:
    """EditorialContentエンティティのテスト"""

    def test_editorial_content_creation(self):
        """解説コンテンツ作成をテスト"""
        content = EditorialContent(
            editorial_id=uuid4(),
            language="ja",
            content="解説内容",
            approach="アプローチ",
            complexity_analysis="計算量解析",
            code_samples={"python": "print('Hello')"},
        )

        assert content.language == "ja"
        assert content.content == "解説内容"
        assert content.code_samples["python"] == "print('Hello')"


@pytest.mark.core
class TestDomainEvents:
    """ドメインイベントのテスト"""

    def test_entity_events_management(self):
        """エンティティのイベント管理をテスト"""
        profile = UserProfile(display_name="Test User")
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            profile=profile,
        )

        # イベントが追加されている
        assert len(user._events) == 1

        # イベントクリア
        events = user.clear_events()
        assert len(events) == 1
        assert len(user._events) == 0
        assert isinstance(events[0], UserRegistered)

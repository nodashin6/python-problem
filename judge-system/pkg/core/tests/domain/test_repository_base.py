"""
Repository base unit tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.core.domain.repositories.repository_base import CoreRepositoryBase
from src.core.domain.models import Entity


class TestEntity(Entity):
    """テスト用エンティティ"""

    name: str


@pytest.mark.core
class TestCoreRepositoryBase:
    """CoreRepositoryBaseのテスト"""

    @pytest.fixture
    def mock_db_session(self):
        """モックデータベースセッションを作成"""
        session = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, mock_db_session):
        """CoreRepositoryBaseの具象実装を作成"""

        class TestRepository(CoreRepositoryBase[TestEntity]):
            def __init__(self, db_session):
                super().__init__(db_session, TestEntity)

        return TestRepository(mock_db_session)

    @pytest.mark.asyncio
    async def test_create_success(self, repository, mock_db_session):
        """エンティティ作成成功のテスト"""
        entity = TestEntity(name="Test Entity")

        # モックの設定
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        # テスト実行
        result = await repository.create(entity)

        # アサート
        assert result == entity
        mock_db_session.add.assert_called_once_with(entity)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(entity)

    @pytest.mark.asyncio
    async def test_create_rollback_on_error(self, repository, mock_db_session):
        """エンティティ作成時のエラーとロールバックのテスト"""
        entity = TestEntity(name="Test Entity")

        # モックの設定 - commitでエラーを発生させる
        mock_db_session.add.return_value = None
        mock_db_session.commit.side_effect = Exception("Database error")
        mock_db_session.rollback.return_value = None

        # テスト実行とアサート
        with pytest.raises(Exception, match="Database error"):
            await repository.create(entity)

        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_success(self, repository, mock_db_session):
        """エンティティ取得成功のテスト"""
        entity_id = uuid4()
        entity = TestEntity(id=entity_id, name="Test Entity")

        # モックの設定
        mock_db_session.get.return_value = entity

        # テスト実行
        result = await repository.get(entity_id)

        # アサート
        assert result == entity
        mock_db_session.get.assert_called_once_with(TestEntity, entity_id)

    @pytest.mark.asyncio
    async def test_get_not_found(self, repository, mock_db_session):
        """エンティティ取得（存在しない）のテスト"""
        entity_id = uuid4()

        # モックの設定
        mock_db_session.get.return_value = None

        # テスト実行
        result = await repository.get(entity_id)

        # アサート
        assert result is None
        mock_db_session.get.assert_called_once_with(TestEntity, entity_id)

    @pytest.mark.asyncio
    async def test_update_success(self, repository, mock_db_session):
        """エンティティ更新成功のテスト"""
        entity = TestEntity(name="Updated Entity")

        # モックの設定
        mock_db_session.merge.return_value = entity
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None

        # テスト実行
        result = await repository.update(entity)

        # アサート
        assert result == entity
        mock_db_session.merge.assert_called_once_with(entity)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(entity)

    @pytest.mark.asyncio
    async def test_update_rollback_on_error(self, repository, mock_db_session):
        """エンティティ更新時のエラーとロールバックのテスト"""
        entity = TestEntity(name="Updated Entity")

        # モックの設定 - commitでエラーを発生させる
        mock_db_session.merge.return_value = entity
        mock_db_session.commit.side_effect = Exception("Database error")
        mock_db_session.rollback.return_value = None

        # テスト実行とアサート
        with pytest.raises(Exception, match="Database error"):
            await repository.update(entity)

        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_success(self, repository, mock_db_session):
        """エンティティ削除成功のテスト"""
        entity_id = uuid4()
        entity = TestEntity(id=entity_id, name="Test Entity")

        # モックの設定
        mock_db_session.get.return_value = entity
        mock_db_session.delete.return_value = None
        mock_db_session.commit.return_value = None

        # テスト実行
        await repository.delete(entity_id)

        # アサート
        mock_db_session.get.assert_called_once_with(TestEntity, entity_id)
        mock_db_session.delete.assert_called_once_with(entity)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_db_session):
        """エンティティ削除（存在しない）のテスト"""
        entity_id = uuid4()

        # モックの設定
        mock_db_session.get.return_value = None

        # テスト実行とアサート
        with pytest.raises(ValueError, match="Entity not found"):
            await repository.delete(entity_id)

    @pytest.mark.asyncio
    async def test_delete_rollback_on_error(self, repository, mock_db_session):
        """エンティティ削除時のエラーとロールバックのテスト"""
        entity_id = uuid4()
        entity = TestEntity(id=entity_id, name="Test Entity")

        # モックの設定 - commitでエラーを発生させる
        mock_db_session.get.return_value = entity
        mock_db_session.delete.return_value = None
        mock_db_session.commit.side_effect = Exception("Database error")
        mock_db_session.rollback.return_value = None

        # テスト実行とアサート
        with pytest.raises(Exception, match="Database error"):
            await repository.delete(entity_id)

        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_success(self, repository, mock_db_session):
        """全エンティティ取得成功のテスト"""
        entities = [
            TestEntity(name="Entity 1"),
            TestEntity(name="Entity 2"),
            TestEntity(name="Entity 3"),
        ]

        # モックの設定
        mock_query = MagicMock()
        mock_query.all.return_value = entities
        mock_db_session.query.return_value = mock_query

        # テスト実行
        result = await repository.list_all()

        # アサート
        assert len(result) == 3
        assert result == entities
        mock_db_session.query.assert_called_once_with(TestEntity)

    @pytest.mark.asyncio
    async def test_list_all_empty(self, repository, mock_db_session):
        """全エンティティ取得（空）のテスト"""
        # モックの設定
        mock_query = MagicMock()
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query

        # テスト実行
        result = await repository.list_all()

        # アサート
        assert len(result) == 0
        mock_db_session.query.assert_called_once_with(TestEntity)

    @pytest.mark.asyncio
    async def test_exists_true(self, repository, mock_db_session):
        """エンティティ存在確認（存在する）のテスト"""
        entity_id = uuid4()

        # モックの設定
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = TestEntity(id=entity_id, name="Test Entity")
        mock_db_session.query.return_value = mock_query

        # テスト実行
        result = await repository.exists(entity_id)

        # アサート
        assert result is True
        mock_db_session.query.assert_called_once_with(TestEntity)

    @pytest.mark.asyncio
    async def test_exists_false(self, repository, mock_db_session):
        """エンティティ存在確認（存在しない）のテスト"""
        entity_id = uuid4()

        # モックの設定
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query

        # テスト実行
        result = await repository.exists(entity_id)

        # アサート
        assert result is False
        mock_db_session.query.assert_called_once_with(TestEntity)

    @pytest.mark.asyncio
    async def test_count_success(self, repository, mock_db_session):
        """エンティティ数カウント成功のテスト"""
        # モックの設定
        mock_query = MagicMock()
        mock_query.count.return_value = 5
        mock_db_session.query.return_value = mock_query

        # テスト実行
        result = await repository.count()

        # アサート
        assert result == 5
        mock_db_session.query.assert_called_once_with(TestEntity)

    @pytest.mark.asyncio
    async def test_count_zero(self, repository, mock_db_session):
        """エンティティ数カウント（ゼロ）のテスト"""
        # モックの設定
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_db_session.query.return_value = mock_query

        # テスト実行
        result = await repository.count()

        # アサート
        assert result == 0
        mock_db_session.query.assert_called_once_with(TestEntity)

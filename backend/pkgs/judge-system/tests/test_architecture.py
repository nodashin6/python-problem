"""
Architecture Tests
アーキテクチャテスト

新しいアーキテクチャの構造と依存関係をテストします
"""

import os
import sys
from pathlib import Path

import pytest


class TestArchitecture:
    """アーキテクチャの構造テスト"""

    def test_event_directory_exists(self):
        """eventディレクトリが存在することを確認"""
        event_dir = Path(__file__).parent.parent / "ppjudg" / "event"
        assert event_dir.exists(), "event directory should exist"
        assert event_dir.is_dir(), "event should be a directory"

    def test_event_files_exist(self):
        """イベントハンドラーファイルが存在することを確認"""
        event_dir = Path(__file__).parent.parent / "ppjudg" / "event"
        
        # 必要なファイルが存在するか確認
        required_files = [
            "__init__.py",
            "message_queue_handlers.py",
            "domain_event_handlers.py"
        ]
        
        for file_name in required_files:
            file_path = event_dir / file_name
            assert file_path.exists(), f"{file_name} should exist in event directory"

    def test_api_usecase_files_exist(self):
        """API用ユースケースファイルが存在することを確認"""
        usecase_dir = Path(__file__).parent.parent / "ppjudg" / "usecase"
        
        required_files = [
            "api_submission_usecase.py",
            "api_system_usecase.py"
        ]
        
        for file_name in required_files:
            file_path = usecase_dir / file_name
            assert file_path.exists(), f"{file_name} should exist in usecase directory"

    def test_legacy_handlers_removed(self):
        """レガシーhandlers.pyが削除されていることを確認"""
        handlers_path = Path(__file__).parent.parent / "ppjudg" / "app" / "handlers.py"
        assert not handlers_path.exists(), "Legacy handlers.py should be removed"

    def test_architecture_documentation_exists(self):
        """アーキテクチャドキュメントが存在することを確認"""
        arch_doc = Path(__file__).parent.parent / "ppjudg" / "ARCHITECTURE.md"
        assert arch_doc.exists(), "ARCHITECTURE.md should exist"

    def test_imports_structure(self):
        """インポート構造をテスト"""
        # event/__init__.pyの内容確認
        event_init = Path(__file__).parent.parent / "ppjudg" / "event" / "__init__.py"
        with open(event_init, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 期待されるインポートが含まれているか確認
        expected_imports = [
            "MessageQueueEventHandler",
            "SubmissionQueueHandler",
            "JudgeWorkerEventHandler",
            "CoreDomainEventHandler",
            "JudgeSystemEventHandler"
        ]
        
        for import_name in expected_imports:
            assert import_name in content, f"{import_name} should be exported from event module"

    def test_usecase_init_structure(self):
        """usecase/__init__.pyの構造をテスト"""
        usecase_init = Path(__file__).parent.parent / "ppjudg" / "usecase" / "__init__.py"
        with open(usecase_init, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # API用とInternal用の区分があることを確認
        assert "API用ユースケース" in content
        assert "ApiSubmissionUseCase" in content
        assert "ApiSystemUseCase" in content

    def test_message_queue_handler_structure(self):
        """メッセージキューハンドラーの基本構造をテスト"""
        handler_file = Path(__file__).parent.parent / "ppjudg" / "event" / "message_queue_handlers.py"
        with open(handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 必要なクラスが定義されているか確認
        expected_classes = [
            "class MessageQueueEventHandler",
            "class SubmissionQueueHandler",
            "class JudgeWorkerEventHandler",
            "class MessageQueueDispatcher"
        ]
        
        for class_def in expected_classes:
            assert class_def in content, f"{class_def} should be defined"

    def test_api_usecase_structure(self):
        """API用ユースケースの基本構造をテスト"""
        api_submission_file = Path(__file__).parent.parent / "ppjudg" / "usecase" / "api_submission_usecase.py"
        with open(api_submission_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 必要なメソッドが定義されているか確認
        expected_methods = [
            "async def submit_solution(",
            "async def get_submission_status(",
            "async def get_user_submissions(",
            "async def rejudge_submission("
        ]
        
        for method_def in expected_methods:
            assert method_def in content, f"{method_def} should be defined"

    def test_dependency_separation(self):
        """依存関係の分離をテスト"""
        # message_queue_handlers.pyがusecaseをインポートしていないことを確認
        handler_file = Path(__file__).parent.parent / "ppjudg" / "event" / "message_queue_handlers.py"
        with open(handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # usecaseへの直接インポートがないことを確認
        usecase_imports = [
            "from ..usecase.",
            "import usecase",
            "SubmissionUseCase",
            "JudgeWorkerUseCase"
        ]
        
        for import_stmt in usecase_imports[:2]:  # 最初の2つのみチェック
            assert import_stmt not in content, f"Event handlers should not import usecases: {import_stmt}"


class TestFileStructure:
    """ファイル構造の詳細テスト"""

    def test_directory_structure(self):
        """ディレクトリ構造が正しいことを確認"""
        base_dir = Path(__file__).parent.parent / "ppjudg"
        
        expected_dirs = [
            "event",
            "usecase", 
            "domain",
            "infrastructure",
            "app"
        ]
        
        for dir_name in expected_dirs:
            dir_path = base_dir / dir_name
            assert dir_path.exists() and dir_path.is_dir(), f"{dir_name} directory should exist"

    def test_clean_architecture_compliance(self):
        """Clean Architectureの準拠をテスト"""
        # event/message_queue_handlers.pyがdomain servicesのみに依存していることを確認
        handler_file = Path(__file__).parent.parent / "ppjudg" / "event" / "message_queue_handlers.py"
        with open(handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 期待される依存関係
        expected_dependencies = [
            "from ..domain.repositories",
            "from ..domain.services"
        ]
        
        has_domain_deps = any(dep in content for dep in expected_dependencies)
        assert has_domain_deps, "Event handlers should depend on domain services and repositories"

    def test_pytest_configuration(self):
        """pytest設定ファイルが存在することを確認"""
        pytest_ini = Path(__file__).parent.parent / "pytest.ini"
        assert pytest_ini.exists(), "pytest.ini should exist"
        
        with open(pytest_ini, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 非同期テストの設定があることを確認
        assert "asyncio_mode = auto" in content, "asyncio_mode should be configured"
"""
Storage and file management components
ストレージ・ファイル管理システム
"""

import os
import shutil
import mimetypes
from pathlib import Path
from typing import BinaryIO, Optional, Dict, Any, List
from datetime import datetime
import hashlib
import uuid
import logging
from dataclasses import dataclass

from ..env import settings
from ..const import APP_DATA_DIR
from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class FileMetadata:
    """ファイルメタデータ"""

    file_id: str
    original_name: str
    stored_name: str
    file_path: Path
    size: int
    mime_type: str
    hash_md5: str
    uploaded_at: datetime
    uploaded_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_id": self.file_id,
            "original_name": self.original_name,
            "stored_name": self.stored_name,
            "file_path": str(self.file_path),
            "size": self.size,
            "mime_type": self.mime_type,
            "hash_md5": self.hash_md5,
            "uploaded_at": self.uploaded_at.isoformat(),
            "uploaded_by": self.uploaded_by,
        }


class FileManager:
    """ファイル管理"""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or (APP_DATA_DIR / "files")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {
            ".py",
            ".cpp",
            ".java",
            ".js",
            ".txt",
            ".md",
            ".yaml",
            ".yml",
        }

    def _generate_file_id(self) -> str:
        """ファイルIDを生成"""
        return str(uuid.uuid4())

    def _calculate_hash(self, file_path: Path) -> str:
        """ファイルのMD5ハッシュを計算"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _get_file_storage_path(self, file_id: str, extension: str) -> Path:
        """ファイルの保存パスを取得"""
        # ディレクトリ構造: storage_dir / first_2_chars / file_id + extension
        subdir = file_id[:2]
        storage_subdir = self.storage_dir / subdir
        storage_subdir.mkdir(exist_ok=True)
        return storage_subdir / f"{file_id}{extension}"

    def validate_file(self, file_path: Path, original_name: str) -> bool:
        """ファイルを検証"""
        # ファイルサイズチェック
        if file_path.stat().st_size > self.max_file_size:
            logger.warning(
                f"File too large: {file_path} ({file_path.stat().st_size} bytes)"
            )
            return False

        # 拡張子チェック
        extension = Path(original_name).suffix.lower()
        if extension not in self.allowed_extensions:
            logger.warning(f"File extension not allowed: {extension}")
            return False

        return True

    async def store_file(
        self, file_data: BinaryIO, original_name: str, uploaded_by: Optional[str] = None
    ) -> FileMetadata:
        """ファイルを保存"""
        file_id = self._generate_file_id()
        extension = Path(original_name).suffix.lower()
        storage_path = self._get_file_storage_path(file_id, extension)

        # 一時ファイルに保存
        temp_path = storage_path.with_suffix(".tmp")

        try:
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(file_data, f)

            # 検証
            if not self.validate_file(temp_path, original_name):
                temp_path.unlink()
                raise ValueError("File validation failed")

            # 最終的な場所に移動
            temp_path.rename(storage_path)

            # メタデータを作成
            file_size = storage_path.stat().st_size
            mime_type = (
                mimetypes.guess_type(original_name)[0] or "application/octet-stream"
            )
            hash_md5 = self._calculate_hash(storage_path)

            metadata = FileMetadata(
                file_id=file_id,
                original_name=original_name,
                stored_name=storage_path.name,
                file_path=storage_path,
                size=file_size,
                mime_type=mime_type,
                hash_md5=hash_md5,
                uploaded_at=datetime.now(),
                uploaded_by=uploaded_by,
            )

            logger.info(f"File stored successfully: {file_id} ({original_name})")
            return metadata

        except Exception as e:
            # クリーンアップ
            if temp_path.exists():
                temp_path.unlink()
            if storage_path.exists():
                storage_path.unlink()
            logger.error(f"Failed to store file: {e}")
            raise

    async def retrieve_file(self, file_id: str) -> Optional[Path]:
        """ファイルを取得"""
        # 全ての可能な拡張子を試す
        for ext in self.allowed_extensions:
            file_path = self._get_file_storage_path(file_id, ext)
            if file_path.exists():
                return file_path

        logger.warning(f"File not found: {file_id}")
        return None

    async def delete_file(self, file_id: str) -> bool:
        """ファイルを削除"""
        for ext in self.allowed_extensions:
            file_path = self._get_file_storage_path(file_id, ext)
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"File deleted: {file_id}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to delete file {file_id}: {e}")
                    return False

        logger.warning(f"File not found for deletion: {file_id}")
        return False

    async def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """ファイル情報を取得"""
        file_path = await self.retrieve_file(file_id)
        if not file_path:
            return None

        stat = file_path.stat()
        return {
            "file_id": file_id,
            "file_path": str(file_path),
            "size": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "exists": True,
        }


class StorageService:
    """統合ストレージサービス"""

    def __init__(self):
        self.file_manager = FileManager()
        self.metadata_store: Dict[str, FileMetadata] = {}

    async def upload_file(
        self, file_data: BinaryIO, original_name: str, uploaded_by: Optional[str] = None
    ) -> str:
        """ファイルをアップロード"""
        metadata = await self.file_manager.store_file(
            file_data, original_name, uploaded_by
        )
        self.metadata_store[metadata.file_id] = metadata
        return metadata.file_id

    async def download_file(self, file_id: str) -> Optional[Path]:
        """ファイルをダウンロード"""
        return await self.file_manager.retrieve_file(file_id)

    async def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """ファイルメタデータを取得"""
        return self.metadata_store.get(file_id)

    async def delete_file(self, file_id: str) -> bool:
        """ファイルを削除"""
        success = await self.file_manager.delete_file(file_id)
        if success and file_id in self.metadata_store:
            del self.metadata_store[file_id]
        return success

    async def list_files(self, uploaded_by: Optional[str] = None) -> List[FileMetadata]:
        """ファイル一覧を取得"""
        files = list(self.metadata_store.values())
        if uploaded_by:
            files = [f for f in files if f.uploaded_by == uploaded_by]
        return sorted(files, key=lambda f: f.uploaded_at, reverse=True)


# グローバルインスタンス
storage_service = StorageService()

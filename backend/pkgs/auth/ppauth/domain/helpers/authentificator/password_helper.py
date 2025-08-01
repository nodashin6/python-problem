"""
Authentication and Authorization components
認証・認可システム
"""



from ...protocols import CryptoProvider, Logger


class PasswordManager:
    """パスワード管理"""

    def __init__(self, crypto_provider: CryptoProvider, logger: Logger):
        self.crypto_provider = crypto_provider
        self.logger = logger

    def hash_password(self, password: str) -> str:
        """パスワードをハッシュ化 - ドメインロジック"""
        try:
            # ドメインロジック: ソルト生成とPBKDF2ハッシュ化
            salt = self.crypto_provider.generate_salt(32)
            pwdhash = self.crypto_provider.pbkdf2_hash(password, salt, 100000)
            
            # ドメインルール: ソルト + ハッシュの結合
            return salt + pwdhash
            
        except Exception as e:
            self.logger.error(f"Password hashing error: {e}")
            raise

    def verify_password(self, password: str, hashed: str) -> bool:
        """パスワードを検証 - ドメインロジック"""
        try:
            # ドメインロジック: ソルトとハッシュ1分離
            if len(hashed) < 64:
                return False
                
            salt = hashed[:64]
            stored_hash = hashed[64:]
            
            # ドメインロジック: 同じ方法でハッシュ化して比較
            pwdhash = self.crypto_provider.pbkdf2_hash(password, salt, 100000)
            return pwdhash == stored_hash
            
        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False

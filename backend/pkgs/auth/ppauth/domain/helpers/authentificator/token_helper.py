"""
Authentication and Authorization components
認証・認可システム
"""

from datetime import datetime, timedelta
from typing import Optional

from ...models.user import User
from ...protocols import JWTEncoder, Logger
from ...value_objects.jwt_token import JWTClaims, JWTToken


class JWTManager:
    """JWT管理"""

    def __init__(
        self,
        jwt_encoder: JWTEncoder,
        logger: Logger,
        token_expire_minutes: int = 60 * 24,  # 24 hours
    ):
        self.jwt_encoder = jwt_encoder
        self.logger = logger
        self.token_expire_minutes = token_expire_minutes

    def create_token(self, user: User) -> str:
        """JWTトークンを作成 - ドメインロジック"""
        try:
            # ドメインロジック: トークンの有効期限とクレーム生成
            now = datetime.now()
            expires_at = now + timedelta(minutes=self.token_expire_minutes)
            
            claims = JWTClaims(
                user_id=str(user.id),
                email=user.email,
                user_name=user.user_name,
                display_name=user.display_name,
                role=user.role.value,
                iat=now,
                exp=expires_at,
            )
            
            # 具体的なエンコーディングはインフラ層に委謗
            raw_token = self.jwt_encoder.encode_claims(claims)
            
            self.logger.info(f"JWT token created for user: {user.id}")
            return raw_token
            
        except Exception as e:
            self.logger.error(f"Failed to create JWT token: {e}")
            raise

    def verify_token(self, token: str) -> Optional[JWTToken]:
        """JWTトークンを検証 - ドメインロジック"""
        try:
            # 具体的なデコーディングはインフラ層に委謗
            claims = self.jwt_encoder.decode_token(token)
            if not claims:
                self.logger.warning("Invalid token: could not decode")
                return None
            
            # ドメインロジック: 有効期限チェック
            if claims.is_expired():
                self.logger.warning(f"Token expired for user: {claims.user_id}")
                return None
            
            jwt_token = JWTToken(
                raw_token=token,
                claims=claims,
            )
            
            return jwt_token
            
        except Exception as e:
            self.logger.error(f"Token verification error: {e}")
            return None

    def create_token_for_user(self, user: User) -> JWTToken:
        """ユーザー用JWTトークンを作成"""
        raw_token = self.create_token(user)
        claims = self.jwt_encoder.decode_token(raw_token)
        
        if not claims:
            raise ValueError("Failed to create valid token")
            
        return JWTToken(
            raw_token=raw_token,
            claims=claims,
        )
    
    def refresh_token(self, current_token: JWTToken, user: User) -> JWTToken:
        """トークンをリフレッシュ - ドメインロジック"""
        if not current_token.is_valid():
            raise ValueError("Cannot refresh expired token")
        
        # 新しいトークンを作成
        return self.create_token_for_user(user)

"""
JWT Token Domain Service
JWTトークンドメインサービス - ドメインロジックとしてのJWT処理
"""

from datetime import datetime, timedelta
from typing import Optional

from pydddi import IDomainService

from ..models.user import User
from ..protocols import JWTEncoder, Logger, TokenExpiredError, InvalidTokenError
from ..value_objects.jwt_token import JWTClaims, JWTToken


class JWTTokenService(IDomainService):
    """
    JWT Token Domain Service
    JWTトークンドメインサービス - JWTの生成・検証ロジック
    """

    def __init__(
        self,
        jwt_encoder: JWTEncoder,
        logger: Logger,
        token_expire_minutes: int = 60 * 24,  # 24 hours default
    ):
        self.jwt_encoder = jwt_encoder
        self.logger = logger
        self.token_expire_minutes = token_expire_minutes

    def create_token_for_user(self, user: User) -> JWTToken:
        """Create JWT token for user"""
        try:
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
            
            raw_token = self.jwt_encoder.encode_claims(claims)
            
            jwt_token = JWTToken(
                raw_token=raw_token,
                claims=claims,
            )
            
            self.logger.info(f"JWT token created for user: {user.id}")
            return jwt_token
            
        except Exception as e:
            self.logger.error(f"Failed to create JWT token: {e}")
            raise

    def verify_token(self, raw_token: str) -> Optional[JWTToken]:
        """Verify and decode raw token string"""
        try:
            claims = self.jwt_encoder.decode_token(raw_token)
            if not claims:
                self.logger.warning("Invalid token: could not decode")
                return None
            
            if claims.is_expired():
                self.logger.warning(f"Token expired for user: {claims.user_id}")
                raise TokenExpiredError("Token has expired")
            
            jwt_token = JWTToken(
                raw_token=raw_token,
                claims=claims,
            )
            
            return jwt_token
            
        except TokenExpiredError:
            raise
        except Exception as e:
            self.logger.warning(f"Token verification failed: {e}")
            raise InvalidTokenError(f"Invalid token: {e}")

    def refresh_token(self, current_token: JWTToken, user: User) -> JWTToken:
        """Refresh an existing token with new expiration"""
        if not current_token.is_valid():
            raise TokenExpiredError("Cannot refresh expired token")
        
        # Create new token for the user
        return self.create_token_for_user(user)

    def get_user_id_from_token(self, token: JWTToken) -> str:
        """Extract user ID from token"""
        return token.get_user_id()

    def get_user_email_from_token(self, token: JWTToken) -> str:
        """Extract user email from token"""
        return token.get_user_email()

    def get_user_role_from_token(self, token: JWTToken) -> str:
        """Extract user role from token"""
        return token.get_user_role()
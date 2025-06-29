"""
Create User UseCase
ユーザー作成ユースケース
"""

from pydddi import IUseCase

from ..domain.entities.user import UserEntity
from ..domain.helpers.password_helper import PasswordHelper
from ..domain.helpers.validation_helper import ValidationHelper
from ..domain.repositories.user_repository import UserRepository
from ..domain.services.user_service import UserDomainService


class CreateUserCommand:
    """Command for creating a user"""

    def __init__(
        self,
        user_name: str,
        display_name: str,
        email: str,
        password: str,
        avatar_url: str | None = None,
        bio: str | None = None,
    ):
        self.user_name = user_name
        self.display_name = display_name
        self.email = email
        self.password = password
        self.avatar_url = avatar_url
        self.bio = bio


class CreateUserResult:
    """Result for creating a user"""

    def __init__(self, user_entity: UserEntity | None, errors: list[str]):
        self.user_entity = user_entity
        self.errors = errors
        self.success = user_entity is not None and len(errors) == 0


class CreateUserUseCase(IUseCase[CreateUserCommand, CreateUserResult]):
    """UseCase for creating a new user"""

    def __init__(self, user_repo: UserRepository, user_service: UserDomainService):
        self.user_repo = user_repo
        self.user_service = user_service

    async def execute(self, command: CreateUserCommand) -> CreateUserResult:
        """Execute user creation"""
        try:
            # Validate input
            validation_errors = ValidationHelper.validate_user_input(
                command.user_name, command.email, command.password
            )
            if validation_errors:
                return CreateUserResult(None, validation_errors)

            # Check domain constraints
            domain_errors = await self.user_service.validate_user_data(command.user_name, command.email)
            if domain_errors:
                return CreateUserResult(None, domain_errors)

            # Generate password hash
            password_hash, salt = PasswordHelper.generate_password_hash(command.password)

            # Create user entity
            user_entity = UserEntity(
                user_name=command.user_name,
                display_name=command.display_name,
                email=command.email,
                password_hash=password_hash,
                avatar_url=command.avatar_url,
                bio=command.bio,
            )

            # Save to repository
            created_user = await self.user_repo.create(user_entity)

            return CreateUserResult(created_user, [])

        except Exception as e:
            return CreateUserResult(None, [f"User creation failed: {e!s}"])

from ...models.domain_config import DomainConfig


class HasDomainRepository:
    """
    Base repository interface that extends ICrudRepository.
    This interface can be used to define common methods for repositories.
    """

    def __init__(self, config: DomainConfig):
        self.config = config

    @property
    def language(self) -> str:
        """
        Returns the default language for the repository.
        This can be overridden in subclasses if needed.
        """
        return self.config.language

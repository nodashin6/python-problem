from supabase import Client

# Remove ppcore dependencies to avoid cross-module coupling
from .....domain.models.domain_config import DomainConfig
from .....domain.repositories.shared.has_domain_repository import HasDomainRepository


class DomainSupabaseMixin(HasDomainRepository):
    """
    Mixin for Supabase repositories that require domain configuration.
    This mixin provides access to the domain configuration and language settings.
    Remove direct ppcore infrastructure dependency for cleaner architecture.
    """

    def __init__(self, client: Client, config: DomainConfig):
        """
        Initialize the mixin with a Supabase client and domain configuration.

        args:
            client (Client): The Supabase client instance.
            config (DomainConfig): The domain configuration instance.
        """
        # Initialize domain concerns
        HasDomainRepository.__init__(self, config)
        # Store client for repository operations
        self.client = client

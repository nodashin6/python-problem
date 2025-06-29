from supabase import Client

from ppcore.infrastructure.supabase.repository import SupabaseRepository
from ppprob.domain.models.domain_config import DomainConfig

from .....domain.repositories.shared.has_domain_repository import HasDomainRepository


class DomainSupabaseMixin(HasDomainRepository, SupabaseRepository):
    """
    Mixin for Supabase repositories that require domain configuration.
    This mixin provides access to the domain configuration and language settings.

    Following DDD principles:
    - Domain concerns (HasDomainRepository) take precedence
    - Infrastructure (SupabaseRepository) depends on domain abstractions
    """

    def __init__(self, client: Client, config: DomainConfig):
        """
        Initialize the mixin with a Supabase client and domain configuration.

        args:
            client (Client): The Supabase client instance.
            config (DomainConfig): The domain configuration instance.
        """
        # Initialize domain concerns first (DDD principle)
        HasDomainRepository.__init__(self, config)
        # Then initialize infrastructure
        SupabaseRepository.__init__(self, client)

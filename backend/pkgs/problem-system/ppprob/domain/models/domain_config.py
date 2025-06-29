from pydantic import UUID4, BaseModel, Field

from ..enums import Language


class DomainConfig(BaseModel):
    language: Language = Language.JAPANESE

"""
Core domain repository interfaces
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar, Dict, Any, Union
from uuid import UUID
from datetime import datetime

from ....shared.database import BaseRepository
from ..models import Entity

T = TypeVar("T", bound=Entity)


class CoreRepositoryBase(BaseRepository[T]):
    """Core domain repository base class extending shared infrastructure"""

    pass

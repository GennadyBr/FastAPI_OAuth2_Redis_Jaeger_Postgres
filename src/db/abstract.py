from abc import ABC, abstractmethod
from typing import Any


class AbstractDB(ABC):
    @abstractmethod
    async def create(self, new_object):
        """Create new db item"""

    @abstractmethod
    async def read(self, item_id):
        """Read the db item"""

    @abstractmethod
    async def update(self, item_id, new_object):
        """Update db item"""

    @abstractmethod
    async def delete(self, item_id):
        """Delete the db item"""


class AbstractCache(ABC):
    @abstractmethod
    async def put_to_cache(self, key: str, value: Any, expire_in_sec: int):
        """Put value to cache with some key"""

    @abstractmethod
    async def get_from_cache_by_key(self, key: str):
        """Get from cache by some key"""

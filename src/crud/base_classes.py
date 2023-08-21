from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID
from typing import Union


class CrudBase(ABC):

    @abstractmethod
    async def create(
            self, name: str) -> Any:
        """создание записи в таблице"""

    @abstractmethod
    async def delete(self, uuid: Union[str, UUID]) -> Any:
        """удаление записи в таблице"""

    @abstractmethod
    async def get(self, uuid: UUID) -> Any:
        """получение записи из таблицы"""

    @abstractmethod
    async def update(self, uuid: UUID, **kwargs) -> Any:
        """редактирование записи в таблице"""

from abc import ABC, abstractmethod
from typing import Any, Type
from uuid import UUID
from typing import Union
from pydantic import BaseModel


class CrudBase(ABC):

    @abstractmethod
    async def create(
            self, name: str) -> Any:
        """создание записи в таблице"""

    @abstractmethod
    async def delete(self, id: Union[str, UUID]) -> Any:
        """удаление записи в таблице"""

    @abstractmethod
    async def get(self, id: UUID) -> Any:
        """получение записи из таблице"""


    @abstractmethod
    async def update(self, id: UUID, **kwargs) -> Any:
        """редактирование записи в таблице"""

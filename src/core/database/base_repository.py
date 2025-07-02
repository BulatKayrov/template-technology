from abc import ABC, abstractmethod


class BaseRepository(ABC):
    model = None

    @abstractmethod
    async def create(self, *args, **kwargs): ...

    @abstractmethod
    async def delete(self, *args, **kwargs): ...

    @abstractmethod
    async def update(self, *args, **kwargs): ...

    @abstractmethod
    async def find_all(self, *args, **kwargs): ...

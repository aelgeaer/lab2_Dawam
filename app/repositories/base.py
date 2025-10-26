from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')
C = TypeVar('C', bound=BaseModel)
U = TypeVar('U', bound=BaseModel)

class BaseRepository(ABC, Generic[T, C, U]):
    
    @abstractmethod
    def create(self, obj_in: C) -> T:
        pass
    
    @abstractmethod
    def get(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass
    
    @abstractmethod
    def update(self, id: int, obj_in: U) -> Optional[T]:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

"""
Базовый класс для всех Use Cases.
"""
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class AbstractUseCase(Generic[T, R], ABC):
    """
    Абстрактный базовый класс для всех Use Cases.
    
    Generic типы:
    - T: Тип входных данных
    - R: Тип возвращаемых данных
    """
    
    @abstractmethod
    async def execute(self, input_dto: T) -> R:
        """
        Выполняет основную логику Use Case.
        
        Args:
            input_dto (T): Входные данные
            
        Returns:
            R: Результат выполнения
        """
        pass 
from abc import ABC, abstractmethod
from typing import Optional


class DecisionMaker(ABC):
    @abstractmethod
    def decide(
        self,
        goal: str,
        observation: dict,
        tools: list[dict],
        history: Optional[list[str]] = None,
    ):
        pass

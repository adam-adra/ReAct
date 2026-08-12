from abc import ABC, abstractmethod


class DecisionMaker(ABC):
    @abstractmethod
    def decide(self, goal, observation, tools):
        pass

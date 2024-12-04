from __future__ import annotations
from abc import ABC, abstractmethod
from action import Action

class Player(ABC):

    @abstractmethod
    def play(
        self, actions: list[Action], fish: GoFish, player_i: int, player_you: int
    ) -> Action:
        return NotImplemented

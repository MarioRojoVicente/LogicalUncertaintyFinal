from __future__ import annotations
from dataclasses import dataclass
from abc import ABC

@dataclass(slots=True)
class World(ABC):
    p: float # How likely is this world

@dataclass(slots=True)
class WorldK1(World):
    p: float

    # For memory reasons, we don't put the true state in the representation.
    
    # Players are always certain of their own cards, so the representation 
    # only includes beliefs about the cards held by other players.  
    think: tuple[int, ...]

    def __hash__(self) -> int:
        return hash(self.think)

    def __eq__(self, value: WorldK1) -> bool:
        # Assuming we never compare to a different object
        return self.think == value.think

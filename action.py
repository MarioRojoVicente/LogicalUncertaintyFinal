from dataclasses import dataclass

@dataclass(slots=True)
class Action:
    rank: int

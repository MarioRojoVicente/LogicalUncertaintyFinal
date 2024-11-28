from players.player import Player
from action import Action
from go_fish import GoFish
from players.heuristics import *

class K1ProbabilityPlayer(Player):

    def __init__(self, heuristic = ExplotationExplorationHeuristic()):
        self.heuristic = heuristic
        super().__init__()


    def play(
        self, actions: list[Action], fish: GoFish, player_i: int, player_you: int
    ) -> Action:
        return self.heuristic.evaluate(fish=fish, actions=actions, currentPlayer=player_i)
        

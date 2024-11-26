import random
from players.player import Player
from action import Action
from go_fish import GoFish

class RandomPlayer(Player):

    def play(
        self, actions: list[Action], fish: GoFish, player_i: int, player_you: int
    ) -> Action:
        return random.choice(actions)

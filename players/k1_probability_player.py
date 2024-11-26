from players.player import Player
from action import Action
from go_fish import GoFish

class K1ProbabilityPlayer(Player):

    def play(
        self, actions: list[Action], fish: GoFish, player_i: int, player_you: int
    ) -> Action:
        possibilities = fish.probability_of_has_ranks(fish.worlds[player_i])
        return max(actions, key=lambda action: possibilities[action.rank])

from players.player import Player
from action import Action
from go_fish import GoFish

class HumanPlayer(Player):

    def play(
        self, actions: list[Action], fish: GoFish, player_i: int, player_you: int
    ) -> Action:
        print(f"Players: I {player_i} You {player_you}")

        while True:
            inp = input(
                f"Please choose one of the ranks: {" ".join(str(action.rank) for action in actions)}\n"
            )

            if inp == "p":
                print("You think they have the ranks with these probabilities")
                print_probabilities(
                    fish.probability_of_has_ranks(fish.worlds[player_i]), fish.ranks
                )

            if inp == "pi":
                print("They think you have these ranks with these probabilities")
                print_probabilities(
                    fish.probability_of_has_ranks(fish.worlds[player_you]), fish.ranks
                )

            for action in actions:
                if str(action.rank) == inp:
                    return action


def print_probabilities(probabilities, ranks):
    print(", ".join([f"{c}: {probabilities[c]:.3f}" for c in range(ranks)]))

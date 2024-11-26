from go_fish import GoFish
from players.random_player import RandomPlayer
from players.human_player import HumanPlayer
from players.k1_probability_player import K1ProbabilityPlayer

def main() -> None:
    wins = {0: 0, 1: 0}
    rounds = 10000

    for i in range(rounds):
        steps = 0
        game = GoFish(
            ranks=13, suit_size=4, initial_hand_size=7,
            player_ais=[K1ProbabilityPlayer(), RandomPlayer()],
        )

        while not game.is_over():
            game.play_turn()
            steps += 1

        wins[game.winner()] += 1
        print(f"Round {i}: {wins} - {game.winner()} won the game in {steps} steps!")

    print(f"Final ({rounds} rounds): {wins}")


if __name__ == "__main__":
    main()

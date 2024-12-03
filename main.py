from go_fish import GoFish
from players.random_player import RandomPlayer
from players.human_player import HumanPlayer
from players.k1_probability_player import K1ProbabilityPlayer
from players.heuristics import *

ROUNDS = 1000

heuristics = [RandomHeuristic(), GoForCloserPointHeuristic(), HoardingHeuristic(), FinishFastHeuristic(), ExplorationHeuristic(), ExplotationExplorationHeuristic() ]
heuristicsTags = ["Random", "GoForCloserPoint", "Hoarding", "FinishFast", "Exploration", "ExplotationExploration"]

offset = 4
everyNth = 5

benchmarks = [[0,0,0,0,0,0],
              [0,0,0,0,0,0],
              [0,0,0,0,0,0],
              [0,0,0,0,0,0],
              [0,0,0,0,0,0],
              [0,0,0,0,0,0]]

def main(h1=0, h2=0) -> None:
    wins = {0: 0, 1: 0}
    rounds = ROUNDS

    for i in range(rounds):
        steps = 0
        game = GoFish(
            ranks=13, suit_size=4, initial_hand_size=7,
            player_ais=[K1ProbabilityPlayer(heuristic=heuristics[h1]), K1ProbabilityPlayer(heuristic=heuristics[h2])],
            #player_ais=[RandomPlayer(), K1ProbabilityPlayer(heuristic=GoForCloserPoint())],
        )

        while not game.is_over():
            game.play_turn()
            steps += 1

        wins[game.winner()] += 1
        print(f"Round {i}: {wins} - {game.winner()} ({heuristicsTags[h1]} vs {heuristicsTags[h2]}) won the game in {steps} steps!")

    print(f"Final ({rounds} rounds): {wins}")
    benchmarks[h1][h2] = round(wins[0]/ROUNDS, 2)
    benchmarks[h2][h1] = round(wins[1]/ROUNDS, 2)


if __name__ == "__main__":
    for h1 in range(0, len(heuristicsTags)):
        for h2 in range(h1, len(heuristicsTags)):
            if h1 != h2:
                offset += 1
                if offset % everyNth == 0:
                    main(h1, h2)
    print("In", ROUNDS , "games probability of row winiing against column")
    print(heuristicsTags)
    idx = 0
    for row in benchmarks:
        print(row, heuristicsTags[idx])
        idx = idx + 1
    # main(1, 5)


#in 100 games probability of row winiing against column

#                    Random  Hoarding    FinishFast     Exploration     ExptExpr (0.2)     GoForCloserPoint
# Random             X       0,23        0.14           0.79            0.19               0.90
# Hoarding           0,77    X           0.34           0.98            0.54               0.93
# FinishFast         0.86    0.66        X              0.98            0.52               0.61 
# Exploration        0.21    0.02        0.02           X               0.07               0.83
# ExptExpr (0.2)     0.81    0.46        0.48           0.93            X                  0.04
# GoForCloserPoint   0.10    0.07        0.39           0.17            0.96               X
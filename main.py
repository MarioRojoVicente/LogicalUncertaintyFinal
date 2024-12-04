#main.py
from go_fish import GoFish
from players.random_player import RandomPlayer
from players.k1_probability_player import K1ProbabilityPlayer
from players.deep_learning_player import DeepLearningPlayer
from players.heuristics import *
import matplotlib.pyplot as plt
import numpy as np
import os

heuristics = [
    RandomHeuristic(),
    GoForCloserPointHeuristic(),
    HoardingHeuristic(),
    FinishFastHeuristic(),
    ExplorationHeuristic(),
    ExplotationExplorationHeuristic(),
]
heuristicsTags = [
    "Random",
    "GoForCloserPoint",
    "Hoarding",
    "FinishFast",
    "Exploration",
    "ExplotationExploration",
]

def main(player1_type='heuristic', player2_type='heuristic', h1=0, h2=0, model_file=None, train=True):
    wins = {0: 0, 1: 0}
    win_rates = []
    episodes = []
    cumulative_rewards = []
    average_steps = []
    epsilon_values = []
    action_counts = {}
    total_steps = 0
    total_reward = 0

    # Initialize epsilon decay parameters if desired
    initial_epsilon = 0.1
    min_epsilon = 0.01
    decay_rate = 0.995

    # Initialize players
    if player1_type == 'deep_learning':
        player1 = DeepLearningPlayer(model_file=model_file, train=train, epsilon=initial_epsilon)
    else:
        player1 = K1ProbabilityPlayer(heuristic=heuristics[h1])

    if player2_type == 'deep_learning':
        player2 = DeepLearningPlayer(model_file=model_file, train=train, epsilon=initial_epsilon)
    else:
        player2 = K1ProbabilityPlayer(heuristic=heuristics[h2])

    for i in range(ROUNDS):
        steps = 0

        # Reset game
        game = GoFish(
            ranks=13,
            suit_size=4,
            initial_hand_size=7,
            player_ais=[player1, player2],
        )

        while not game.is_over():
            game.play_turn()
            steps += 1

        winner = game.winner()
        wins[winner] += 1
        total_steps += steps

        # Update the deep learning player(s)
        if player1_type == 'deep_learning':
            reward = 1.0 if winner == 0 else -1.0
            total_reward += reward
            player1.update_q_values(reward)
            # Decay epsilon
            if player1.epsilon > min_epsilon:
                player1.epsilon *= decay_rate
            if (i + 1) % 10 == 0 and train:
                player1.save_model()
            # Update action counts
            for rank, count in player1.action_counts.items():
                action_counts[rank] = action_counts.get(rank, 0) + count
            # Reset action counts for the next game
            player1.action_counts.clear()

        if player2_type == 'deep_learning':
            reward = 1.0 if winner == 1 else -1.0
            total_reward += reward
            player2.update_q_values(reward)
            # Decay epsilon
            if player2.epsilon > min_epsilon:
                player2.epsilon *= decay_rate
            if (i + 1) % 10 == 0 and train:
                player2.save_model()
            # Update action counts
            for rank, count in player2.action_counts.items():
                action_counts[rank] = action_counts.get(rank, 0) + count
            # Reset action counts for the next game
            player2.action_counts.clear()

        # Record metrics every 10 games
        if (i + 1) % 10 == 0:
            current_episode = i + 1
            win_rate = (wins[0] / current_episode) if player1_type == 'deep_learning' else (wins[1] / current_episode)
            win_rates.append(win_rate)
            episodes.append(current_episode)
            cumulative_rewards.append(total_reward)
            avg_steps = total_steps / current_episode
            average_steps.append(avg_steps)
            if player1_type == 'deep_learning':
                epsilon_values.append(player1.epsilon)
            elif player2_type == 'deep_learning':
                epsilon_values.append(player2.epsilon)

        print(f"Round {i+1}: {wins} - Player {winner} won the game in {steps} steps.")

    print(f"Final ({ROUNDS} rounds): {wins}")

    # Plotting
    if player1_type == 'deep_learning':
        plot_learning_progress(episodes, win_rates, cumulative_rewards, average_steps, epsilon_values, action_counts, player_label='DeepLearningPlayer')
    elif player2_type == 'deep_learning':
        plot_learning_progress(episodes, win_rates, cumulative_rewards, average_steps, epsilon_values, action_counts, player_label='DeepLearningPlayer')

def plot_learning_progress(episodes, win_rates, cumulative_rewards, average_steps, epsilon_values, action_counts, player_label):
    plt.figure(figsize=(15, 10))

    # Plot Win Rate
    plt.subplot(2, 3, 1)
    plt.plot(episodes, win_rates, label='Win Rate', color='blue')
    plt.xlabel('Episodes')
    plt.ylabel('Win Rate')
    plt.title(f'{player_label} Win Rate Over Time')
    plt.legend()

    # Plot Cumulative Reward
    plt.subplot(2, 3, 2)
    plt.plot(episodes, cumulative_rewards, label='Cumulative Reward', color='green')
    plt.xlabel('Episodes')
    plt.ylabel('Cumulative Reward')
    plt.title(f'{player_label} Cumulative Reward Over Time')
    plt.legend()

    # Plot Average Steps per Game
    plt.subplot(2, 3, 3)
    plt.plot(episodes, average_steps, label='Average Steps', color='orange')
    plt.xlabel('Episodes')
    plt.ylabel('Average Steps per Game')
    plt.title(f'{player_label} Average Steps Over Time')
    plt.legend()

    # Plot Epsilon Value Over Time
    plt.subplot(2, 3, 4)
    plt.plot(episodes, epsilon_values, label='Epsilon Value', color='red')
    plt.xlabel('Episodes')
    plt.ylabel('Epsilon')
    plt.title(f'{player_label} Epsilon Decay Over Time')
    plt.legend()

    # Plot Action Distribution
    plt.subplot(2, 3, 5)
    if action_counts:
        ranks = list(action_counts.keys())
        counts = list(action_counts.values())
        plt.bar(ranks, counts, color='purple')
        plt.xlabel('Card Rank Asked')
        plt.ylabel('Count')
        plt.title(f'{player_label} Action Distribution')
    else:
        plt.text(0.5, 0.5, 'No Actions Recorded', horizontalalignment='center', verticalalignment='center')
        plt.axis('off')

    plt.tight_layout()
    plt.show()

ROUNDS = 5000
if __name__ == "__main__":
    # Example: Train against the first heuristic, then sequentially against others
    heuristics_to_train_against = [3]  # Indices of heuristics in heuristicsTags

    model_file = 'deep_learning_model_h333_5k.pkl'

    for h in heuristics_to_train_against:
        heuristic_name = heuristicsTags[h]
        print(f"\nTraining against {heuristicsTags[h]} heuristic.")
        main(
            player1_type='deep_learning',
            player2_type='heuristic',
            h1=0,      # Not used when player1 is DeepLearningPlayer
            h2=h,      # Index of the heuristic for player 2
            model_file=model_file,
            train=True,
        )

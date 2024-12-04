#deep_learning_player.py

import random
import numpy as np
import os
from players.player import Player
from action import Action
from go_fish import GoFish
from typing import List
import pickle

class DeepLearningPlayer(Player):
    def __init__(self, model_file: str = None, train: bool = True, epsilon: float = 0.1):
        """
        Initializes the DeepLearningPlayer.

        Args:
            model_file (str): Path to the saved model file. If None, a new model is created.
            train (bool): If True, the model will be trained during play. If False, the model is used only for inference.
            epsilon (float): Exploration rate.
        """
        super().__init__()
        self.model_file = model_file
        self.train_mode = train
        self.epsilon = epsilon  # Exploration rate
        self.gamma = 0.99       # Discount factor
        self.alpha = 0.1        # Learning rate

        # Initialize or load the model
        if model_file and os.path.exists(model_file):
            with open(model_file, 'rb') as f:
                self.q_table = pickle.load(f)
        else:
            self.q_table = {}  # Initialize an empty Q-table

        self.action_counts = {}         # To count actions taken
        self.last_state = None
        self.last_action = None

    def get_state(self, fish: GoFish, player_i: int) -> tuple:
        """
        Generates a state representation.

        Args:
            fish (GoFish): The game instance.
            player_i (int): The player index.

        Returns:
            tuple: A tuple representing the state.
        """
        # Use player's own hand and beliefs about the opponent
        hand = tuple(fish.hands[player_i])
        # For simplicity, we can use the expected values of opponent's hand
        opponent_belief = tuple(
            int(sum(world.p * world.think[i] for world in fish.worlds[player_i]))
            for i in range(fish.ranks)
        )
        # Combine hand and opponent belief into a state
        state = hand + opponent_belief
        return state

    def play(
        self, actions: List[Action], fish: GoFish, player_i: int, player_you: int
    ) -> Action:
        # Get the current state
        state = self.get_state(fish, player_i)

        # Initialize Q-values for unseen states
        if state not in self.q_table:
            self.q_table[state] = {action.rank: 0.0 for action in actions}

        # Epsilon-greedy action selection
        if self.train_mode and random.random() < self.epsilon:
            # Exploration: choose a random action
            action = random.choice(actions)
        else:
            # Exploitation: choose the best action based on Q-values
            q_values = self.q_table[state]
            max_q = max(q_values.values())
            best_actions = [Action(rank) for rank, q in q_values.items() if q == max_q]
            action = random.choice(best_actions)

        # Record action counts
        self.action_counts[action.rank] = self.action_counts.get(action.rank, 0) + 1

        # Store the state and action for training
        self.last_state = state
        self.last_action = action.rank

        return action

    def update(self, fish: GoFish, player_i: int, reward: float):
        """
        Updates the Q-values based on the immediate reward.

        Args:
            fish (GoFish): The game instance.
            player_i (int): The player index.
            reward (float): The immediate reward.
        """
        next_state = self.get_state(fish, player_i)

        # Initialize Q-values if states are unseen
        if self.last_state not in self.q_table:
            self.q_table[self.last_state] = {rank: 0.0 for rank in range(fish.ranks)}
        if next_state not in self.q_table:
            self.q_table[next_state] = {rank: 0.0 for rank in range(fish.ranks)}

        q_values = self.q_table[self.last_state]
        current_q = q_values.get(self.last_action, 0.0)
        max_future_q = max(self.q_table[next_state].values())

        # Q-learning update
        target = reward + self.gamma * max_future_q
        q_values[self.last_action] = current_q + self.alpha * (target - current_q)

        # Update last_state for the next step
        self.last_state = next_state

    def update_q_values(self, reward: float):
        """
        Updates the Q-values based on the game outcome.

        Args:
            reward (float): The reward received at the end of the game.
        """
        # No longer needed since we update after each action
        pass

    def save_model(self):
        """
        Saves the trained model to a file.
        """
        if self.model_file:
            with open(self.model_file, 'wb') as f:
                pickle.dump(self.q_table, f)
        else:
            print("Model file path not specified. Model not saved.")

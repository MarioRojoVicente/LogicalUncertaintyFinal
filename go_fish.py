import random
import logging as l
from typing import Callable, TypeVar

from players.player import Player
from action import Action
from world import World, WorldK1

l.basicConfig(level=l.DEBUG, format="%(message)s") # Use l.DEBUG or l.INFO
l.disable()

T = TypeVar('T', bound=World)
Deck = list[int]

players = [0, 1]
opponent = [1, 0]

class GoFish:
    deck: Deck
    total_cards: int

    turn: int
    player_ais: list[Player]

    # We keep the player beliefs separate
    worlds: list[list[WorldK1]]
    # These are the real hands of the players. Each player knows their own hand
    hands: list[list[int]]

    def __init__(self, ranks: int, suit_size: int, initial_hand_size: int, player_ais: list[Player]) -> None:
        self.ranks = ranks
        self.suit_size = suit_size
        self.total_cards = ranks * suit_size
        self.hand_size = initial_hand_size
        self.turn = 0
        self.player_ais = player_ais

        # Initially both players know all cards are in the deck
        empty_hand = [0] * self.ranks

        self.worlds = [
            [WorldK1(1, tuple(empty_hand.copy()))],
            [WorldK1(1, tuple(empty_hand.copy()))]
        ]

        self.hands = [empty_hand.copy(), empty_hand.copy()]

        # Assign an initial hand of cards to both players
        self.deck = self.create_random_deck()
        for p in players:
            for _ in range(initial_hand_size):
                self.draw(p, opponent[p])

    def ask(self, rank: int, player_i: int, player_you: int) -> bool:
        # you learn that I have at least one of the given rank
        self.worlds[player_you] = self.remove_impossible_worlds(
            self.worlds[player_you], lambda w: w.think[rank] > 0
        )

        if self.hands[player_you][rank] > 0:
            # I learn that you have card of that rank in your hand
            self.worlds[player_i] = self.remove_impossible_worlds(
                self.worlds[player_i], lambda w: w.think[rank] > 0
            )
            return True
        else:
            # Go Fish
            self.worlds[player_i] = self.remove_impossible_worlds(
                self.worlds[player_i], lambda w: w.think[rank] == 0
            )
            return False
    
    # read as I give you cards
    def give_cards(self, rank: int, player_i: int, player_you: int):
        num_cards = self.hands[player_i][rank]

        # Player you learns that the only possible worlds are those where I has n cards
        # Player I already knows this fact
        self.worlds[player_you] = self.remove_impossible_worlds(
            self.worlds[player_you], lambda w: w.think[rank] == num_cards
        )

        # Player you learns that the other player no longer has any cards in any of those worlds
        for w in self.worlds[player_you]:
            think = list(w.think)
            think[rank] = 0
            w.think = tuple(think)

        # Player I learns that the other player now must have n more cards on his hand
        for w in self.worlds[player_i]:
            think = list(w.think)
            think[rank] += num_cards
            w.think = tuple(think)

        # update the real world
        self.hands[player_you][rank] += self.hands[player_i][rank]
        self.hands[player_i][rank] = 0
        
    # Should read as I draw a card
    def draw(self, player_i, player_you) -> None:
        previous_deck_card_count = len(self.deck)
        new_card = self.deck.pop()
        self.hands[player_i][new_card] += 1 # add 1 card to my hand

        # I learns that all of your worlds cannot have the number of cards that I have, in your hand
        self.worlds[player_i] = self.remove_impossible_worlds(
            self.worlds[player_i],
            lambda w: w.think[new_card] <= self.suit_size - self.hands[player_i][new_card]
        )

        # You learns that I have a new card in my hand (but we you don't know which one)
        new_worlds: dict[WorldK1, WorldK1] = {}
        for world in self.worlds[player_you]:
            # you imagines that I could have drawn any of the cards in the deck
            for c in range(self.ranks):
                # cards of rank in deck is stored implicitly, through the total number of cards with that rank 
                # - (the cards you think the opponent has in their hand in this world) 
                # - (the cards you know you have on your hand)
                cards_of_rank_in_deck = self.suit_size - world.think[c] - self.hands[player_you][c]
                
                probability_of_drawing_rank = cards_of_rank_in_deck / previous_deck_card_count
                if probability_of_drawing_rank > 0:
                    think = list(world.think)
                    think[c] += 1
                    w = WorldK1(probability_of_drawing_rank * world.p, tuple(think))
                    if w in new_worlds:
                        new_worlds[w].p += w.p
                    else:
                        new_worlds[w] = w

        self.worlds[player_you] = list(new_worlds.values())

    def probability_of_knowledge(
        self, worlds: list[T], condition: Callable[[T], bool]
    ) -> float: 
        return sum(world.p for world in worlds if condition(world))

    def probability_of_has_ranks(self, worlds: list[WorldK1]) -> list[float]:
        return [
            self.probability_of_knowledge(worlds, lambda w: w.think[c] > 0) 
            for c in range(self.ranks)
        ]

    # Go through all impossible worlds
    # remove all the worlds that do not satisfy the condition
    # and redistribute the probability to all other worlds
    def remove_impossible_worlds(
        self, worlds: list[T], condition: Callable[[T], bool]
    ) -> list[T]:
        total_probability = 0
        worlds_to_keep = []

        # Find all legal worlds
        for world in worlds:
            if condition(world):
                worlds_to_keep.append(world)
                total_probability += world.p

        # Redistribute the probability
        for world in worlds_to_keep:
            world.p = world.p / total_probability

        return worlds_to_keep

    def possible_actions(self, player_i) -> list[Action]:
        return [
            Action(c) 
            for c in range(self.ranks) 
            # You can ask about any card you have as long as neither player has all 4 of that card 
            # (it would be waste of an action to ask about books)
            if self.hands[player_i][c] not in {0, 4}
        ]

    def next_players_turn(self) -> None:
        self.turn = (self.turn + 1) % len(players)

    def fish_card(self, player_i: int, player_you: int) -> None:
        self.draw(player_i, player_you)
        self.next_players_turn()

    def play_turn(self) -> None:
        self.log_state()
        player_i = self.turn
        player_you = opponent[player_i]

        actions = self.possible_actions(player_i)
        if len(actions) == 0:
            l.debug("Go fish! (forced action)")
            self.fish_card(player_i, player_you)
            return
        
        action = self.player_ais[player_i].play(actions, self, player_i, player_you)

        they_should_give_cards = self.ask(action.rank, player_i, player_you)
        if they_should_give_cards:
            l.info(f"Player {player_i} guessed {action.rank} right and gets another turn")
            self.give_cards(action.rank, player_you, player_i)
        else:
            if len(self.deck) > 0:
                l.info("Go fish!")
                self.fish_card(player_i, player_you)
            else:
                # should be impossible with 2 players
                l.info("Go fish! (but there were no more cards)")

    def is_over(self) -> bool:
        return (len(self.deck) <= 0 and
                all([c in {0, 4} for hand in self.hands for c in hand]))

    def winner(self) -> int:
        return max(players, key= lambda p: sum(self.hands[p]))
    
    def create_random_deck(self) -> Deck:
        """Returns a shuffled deck"""
        deck = [i for i in range(self.ranks) for _ in range(self.suit_size)]
        random.shuffle(deck)
        return deck

    def log_state(self) -> None:

        player_text = [
            f"Player {p} has "
            + ", ".join(f"{c}: {self.hands[p][c]}" for c in range(self.ranks))
            for p in range(len(self.hands))
        ]
        player_text[self.turn] += " (current turn)"

        l.debug(f"There are {len(self.deck)} cards left")

        for p in players:
            l.debug(player_text[p])

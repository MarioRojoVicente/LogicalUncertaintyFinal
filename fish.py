from __future__ import annotations
from dataclasses import dataclass
import random
from typing import Callable

NUM_RANKS = 13
NUM_SUITS = 4
NUM_CARDS = NUM_RANKS * NUM_SUITS

# world constants
OTHER_PLAYER = 0 # index in 
WORLD_DECK = 1 #
Deck = list[int]

# Players
P0 = 0
P1 = 0
players = [0,1]
opponent = [1,0] # the opposite player for a player

@dataclass(slots=True)
class Action:
    rank:int

class Player:
    def play(actions: list[Action], fish: Fish, playerI:int, playerYou:int):
        raise "Not implemented(abstract class)"


class RandomPlayer(Player):
    def play(actions: list[Action], fish: Fish, playerI:int, playerYou:int):
        return random.choice(actions)

class ProbabilityPlayer(Player):
    def play(actions: list[Action], fish: Fish, playerI:int, playerYou:int):
        possibilities = fish.probability_of_has_ranks(fish.worlds[playerI])
        best_action = None
        best_probability = 0
        for action in actions:
            if possibilities[action.rank] >= best_probability:
                best_probability = possibilities[action.rank]
                best_action = action

        return best_action
    
def print_probabilities(probabilites):
    t = ""
    for c in range(NUM_RANKS):
        t += f"{c}: {round(probabilites[c], 3)}, "
    print(t)
class HumanPlayer(Player):

    def play(actions: list[Action], fish: Fish, playerI:int, playerYou:int):
        print(f"playeri {playerI} you {playerYou}")
        while True:
            text = "Please choose one of the ranks: "
            for action in actions:
                text += str(action.rank) + " "
            
            inp = input(text)
            if inp == "p":
                print("You think they have the ranks with these probabilities")
                print_probabilities(fish.probability_of_has_ranks(fish.worlds[playerI]))
                # print(fish.probability_of_has_ranks(fish.worlds[playerI]))
            
            if inp == "pi":
                print("They think you have these ranks with these probabilities")
                print_probabilities(fish.probability_of_has_ranks(fish.worlds[playerYou]))
                # print(fish.probability_of_has_ranks(fish.worlds[playerYou]))
            for action in actions:
                if str(action.rank) == inp:
                    return action


class Fish:
    # We keep the player beliefs seperate
    worlds: list[list[World]]

    deck: Deck
    playerAis :list[Player]
    turn: int

    # These are the real hands of the players. And the players know their hands
    hands: list[list[int]]
    def __init__(self, playerAis: list[Player]) -> None:
        self.turn = 0
        self.playerAis = playerAis
        everything_is_in_the_deck = [0 for _ in range(NUM_RANKS)] # TODO base this on NUM_RANKS
        # both players that with knowing that all cards are in the deck
        self.worlds = [
            [World(1, everything_is_in_the_deck)],
            [World(1, everything_is_in_the_deck)]
        ]
        self.hands = [
            list(everything_is_in_the_deck),
            list(everything_is_in_the_deck)
        ]


        self.deck = self.create_random_deck()
        for p in players:
            for i in range(5):
                self.draw(p, opponent[p])

    # should read as I draw a card
    def draw(self, playerI, playerYou):
        previous_deck_card_count = len(self.deck)
        new_card = self.deck.pop()
        self.hands[playerI][new_card] += 1 # add 1 card to my hand
        
        # I learns that all of your worlds cannot have the number of cards that I have, in your hand
        self.worlds[playerI] = self.remove_impossible_worlds(self.worlds[playerI],
            lambda w: w.think[new_card] <= NUM_SUITS - self.hands[playerI][new_card]
        )
        
        # You learns that I have a new card in my hand (but we you don't know which one)
        new_worlds :dict[World]= {}
        for world in self.worlds[playerYou]:
            # you imagines that I could have drawn any of the cards in the deck
            for c in range(NUM_RANKS):
                # cards of rank in deck is stored implicitly, through the total number of cards with that rank - (the cards you think the opponent has in their hand in this world) - (the cards you know you have on your hand)
                cards_of_rank_in_deck = NUM_SUITS - world.think[c] - self.hands[playerYou][c]
                probability_of_drawing_rank = cards_of_rank_in_deck / previous_deck_card_count
                if (probability_of_drawing_rank > 0):
                    think = list(world.think)
                    think[c] += 1
                    w = World(probability_of_drawing_rank * world.p, tuple(think))
                    if w in new_worlds:
                        new_worlds[w].p += w.p
                    else:
                        new_worlds[w] = w

        self.worlds[playerYou] = list(new_worlds.values())
    
    def propability_of_knowledge(self, worlds: list[World], condition: Callable[[World], bool]) -> float:
        total_propability = 0
        for world in worlds:
            if condition(world):
                total_propability += world.p
        return total_propability

    def probability_of_has_ranks(self, worlds: list[World]):
        ps = []
        for c in range(NUM_RANKS):
            ps.append(self.propability_of_knowledge(worlds, lambda w: w.think[c] > 0))
        return ps
    
    def askIfYouHaveRank(self, rank:int, playerI:int, playerYou:int) -> bool:
        # you learn that I have atleast one 
        self.worlds[playerYou] = self.remove_impossible_worlds(self.worlds[playerYou], lambda w: w.think[rank] > 0)
        
        if self.hands[playerYou][rank] > 0:
            # I learn that you have card of that rank in your hand
            self.worlds[playerI] = self.remove_impossible_worlds(self.worlds[playerI], lambda w: w.think[rank] > 0)
            return True
        else:
            self.worlds[playerI] = self.remove_impossible_worlds(self.worlds[playerI], lambda w: w.think[rank] == 0)
            return False

    # go through all impossible worlds 
    # remove all the worlds that do not satisfy the condition
    # and redistribute the probability to all other worlds
    def remove_impossible_worlds(self, worlds: list[World],condition: Callable[[World], bool]) -> list[World]:
        total_probability = 0
        new_worlds = []
        
        # find all legal worlds
        for world in worlds:
            if condition(world):
                new_worlds.append(world)
                total_probability += world.p

        # redistribute the probability
        for world in new_worlds:
            world.p = world.p / total_probability
             
        return new_worlds

    def create_random_deck(self) -> Deck:
        """Returns a shuffled deck"""
        cards = [[i,i,i,i] for i in range(NUM_RANKS)]
        deck = [item for sub_list in cards for item in sub_list] # convert 2d array to 1d array (wtf)
        random.shuffle(deck)
        return list(deck)
    
    def print_state(self):
        player_text = ["Player 0 has ", "Player 1 has "]
        for p in players:
            for c in range(NUM_RANKS):
                player_text[p] += f"{c}: {self.hands[p][c]}, "
        player_text[self.turn] += "(current turn)"
        print(f"there are {len(self.deck)} cards left")
        for p in players:
            print(player_text[p])


    def possible_actions(self, playerI):
        actions = []
        for c in range(NUM_RANKS):
            # you can ask about any card you have as long neither play has all 4 of that card(it would be waste of an action to ask about books)
            if (self.hands[playerI][c] != 0 and self.hands[playerI][c] != 4):
                actions.append(Action(c))
        return actions
    
    def next_players_turn(self):
        self.turn = (self.turn + 1) % len(players)

    # read as I give you cards
    def give_cards(self, rank:int, playerI:int, playerYou:int):
        n_cards = self.hands[playerI][rank]
        
        # player you learns that the only possible worlds are those where I has n cards
        self.remove_impossible_worlds(self.worlds[playerYou], lambda w: w.think[rank]==n_cards)
        # player you learns that the other player no longer has any cards in any of those worlds
        for w in self.worlds[playerYou]:
            think = list(w.think)
            think[rank] = 0
            w.think = tuple(think)

        # player I learns that the other player now must have n more cards on his hand
        for w in self.worlds[playerI]:
            think = list(w.think)
            think[rank] += n_cards
            w.think = tuple(think)
        
        # update the real world
        self.hands[playerYou][rank] += self.hands[playerI][rank]
        self.hands[playerI][rank] = 0
    
    def play_turn(self):
        self.print_state()
        playerI = self.turn
        playerYou = opponent[playerI]
        
        actions = self.possible_actions(playerI)
        if len(actions) == 0:
            print("Go fish! (forced action)")
            self.draw(playerI, playerYou)
            self.next_players_turn()
            return
        action = self.playerAis[playerI].play(actions, self, playerI, playerYou)
        
        they_should_give_cards = self.askIfYouHaveRank(action.rank, playerI, playerYou)
        if they_should_give_cards:
            print("you guessed right and get another turn")
            self.give_cards(action.rank, playerYou, playerI)
        else:
            if len(self.deck) > 0:
                print("Go fish!")
                self.draw(playerI, playerYou)
                self.next_players_turn()
            else:
                print("Go fish! (but there were no more cards)")# should be impossible with 2 players
    
    def is_game_over(self):
        if len(self.deck) > 0:
            return False
        for hand in self.hands:
            for c in hand:
                if c != 0 and c != 4:
                    return False
        return True
        
    def winner(self):
        player = 0
        most_cards = 0
        for p in players:
            if sum(self.hands[p]) > most_cards:
                player = p
                most_cards = sum(self.hands[p])
        return player
        
@dataclass(slots=True)
class World:
    # how likely is this world
    p:float
    
    # for memory reasons, we don't put the true state in the representation, since the players are not uncertain about their own cards
    # therefore we only put the other players cards in the representation
    
    # only represents belief about what cards the other player has in has hand
    think: tuple[int]
    
    def __hash__(self) -> int:
        return hash(self.think)
    
    def __eq__(self, value: object) -> bool:
        return self.think == value.think # I am assuming we never compare a world to anything other than a world
    
if __name__ == "__main__":
    # fish = Fish([HumanPlayer, HumanPlayer])
    wins = {0:0, 1:0}
    for i in range(10000):
        # fish = Fish([RandomPlayer, RandomPlayer])
        # fish = Fish([RandomPlayer, ProbabilityPlayer])
        fish = Fish([HumanPlayer, HumanPlayer])
        # print(fish.hands)
        # print(fish.probability_of_has_ranks(fish.worlds[P0]))
        while not fish.is_game_over():
            print(wins)
            fish.play_turn()
        print(f"{fish.winner()} won the game!")
        wins[fish.winner()] += 1
    print(wins)

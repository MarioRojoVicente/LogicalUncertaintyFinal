import random
from go_fish import GoFish



#This heuristics work only with the elements on the players hand
class GoForCloserPointHeuristic():

    def evaluate(self, fish:GoFish, actions, currentPlayer):
        max_rank = fish.hands[currentPlayer].index(0)
        for c in range(fish.ranks):
            if fish.hands[currentPlayer][c] != 4 and fish.hands[currentPlayer][c] > fish.hands[currentPlayer][max_rank]:
                max_rank = c
        for action in actions:
            if action.rank == max_rank:
                return action
        raise Exception("Probelem with the rank in GoForCloserPoint heuristic")
    
class RandomHeuristic():

    def evaluate(self, fish:GoFish, actions, currentPlayer):
        return random.choice(actions)


# This heuristics invilve first order knowlwdge
class HoardingHeuristic():
    #asks for the card that is more probable the nemey has therefore trying to hoard all cards
    
    def evaluate(self, fish:GoFish, actions, currentPlayer):
        possibilities = fish.probability_of_has_ranks(fish.worlds[currentPlayer])
        return max(actions, key=lambda action: possibilities[action.rank])
    
class ExplorationHeuristic():
    #asks for the card that is most uncertain if the enemy has or not therefore triying to reduce uncertainty
    
    def evaluate(self, fish:GoFish, actions, currentPlayer):
        possibilities = fish.probability_of_has_ranks(fish.worlds[currentPlayer])
        most_uncertain = possibilities[0]
        for possibilty in possibilities:
            if abs( 0.5 - possibilty) < abs(0.5 - most_uncertain):
                most_uncertain = possibilty
        return max(actions, key=lambda action: possibilities[action.rank]==most_uncertain)
    
class FinishFastHeuristic():
    #asks for the rank the enemy is most likely to have all the cards I am missing from
    
    def evaluate(self, fish:GoFish, actions, currentPlayer):
        possibilities = []
        for c in range(fish.ranks):
            missing = 4 - fish.hands[currentPlayer][c]
            p = fish.probability_of_ncards_of_ranks(fish.worlds[currentPlayer], c, missing)
            possibilities.append(p)
        return max(actions, key=lambda action: possibilities[action.rank])
    
class ExplotationExplorationHeuristic():
    #asks for the rank the enemy is most likely to have all the cards I am missing from whilw also minimizing uncertainty
    
    def __init__(self, boundry: float = 0.2):
        self.boundry = boundry #marks the lower bound probability for the exploitation mechanic, between 0 and 1

    def exploration(self, fish:GoFish, actions, currentPlayer):
        possibilities = fish.probability_of_has_ranks(fish.worlds[currentPlayer])
        most_uncertain = possibilities[0]
        for possibilty in possibilities:
            if abs( 0.5 - possibilty) < abs(0.5 - most_uncertain):
                most_uncertain = possibilty
        return [max(actions, key=lambda action: possibilities[action.rank]==most_uncertain)]
    
    def exploitation(self, fish:GoFish, actions, currentPlayer):
        possibilities = []
        for c in range(fish.ranks):
            missing = 4 - fish.hands[currentPlayer][c]
            p = fish.probability_of_ncards_of_ranks(fish.worlds[currentPlayer], c, missing)
            possibilities.append(p)
        best_action = max(actions, key=lambda action: possibilities[action.rank])
        return [best_action , possibilities[best_action.rank]]

    def evaluate(self, fish:GoFish, actions, currentPlayer):
        best_action = self.exploitation(fish, actions, currentPlayer)
        if best_action[1] < self.boundry:
            best_action = self.exploration(fish, actions, currentPlayer)
        return best_action[0]
    
#This heuristics involce second level knowledge

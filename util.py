import math
from itertools import combinations

def multi_choose(n: int, k: int) -> int:
    return math.comb(n + k - 1, k)

# For a multiset with finite multiplicities
# find the number of sub-multisets with cardinality k
def multi_choose_finite(multiset: list[int], k: int) -> int:
    n = len(multiset)
    return multi_choose(n, k) + _multi_choose_finite(multiset, n, k, 1)

# Using inclusion-exclusion principle
def _multi_choose_finite(multiplicities: list[int], n: int, k: int, i: int) -> int:
    if i > k:
        return 0

    sign = 1 if i % 2 == 0 else -1
    cur = sum(
        multi_choose(n, ki)
        for m in map(sum, combinations(multiplicities, i))
        if (ki := k - (m + i)) >= 0
    )
    return sign * cur + _multi_choose_finite(multiplicities, n, k, i + 1)

def distribute_dec(l: list[int], amount: int) -> list[int]:
    if amount > sum(l):
        raise ValueError("Amount to distribute exceeds the total sum")

    for i in range(amount):
        idx = i % len(l)
        if l[idx] > 0:
            l[idx] -= 1

    return l

def initial_world_count(cards: list[int], hand_size: int) -> int:
    hand1 = multi_choose_finite(cards, hand_size)
    distribute_dec(cards, hand_size) # worst case
    hand2 = multi_choose_finite(cards, hand_size)
    return hand1 * hand2 - hand1 // 2

# Number of initial worlds considered 
# when the agent knows their own hand (worst case)
def initial_K1_world_count(cards: list[int], hand_size: int) -> int:
    distribute_dec(cards, hand_size)
    return multi_choose_finite(cards, hand_size)

print(initial_world_count(13 * [4], 7))
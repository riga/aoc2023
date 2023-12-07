# coding: utf-8

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import cmp_to_key
from collections import Counter
from enum import IntEnum


this_dir: str = os.path.dirname(os.path.abspath(__file__))


# card scores for part 1
card_values1: dict[str, int] = {
    card: i
    for i, card in enumerate("23456789TJQKA", 2)
}

# card scores for part 2, joker moved to front
card_values2: dict[str, int] = {
    card: i
    for i, card in enumerate("J23456789TQKA", 2)
}


# special scores
class Score(IntEnum):
    NOTHING = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE = 3
    FULL_HOUSE = 4
    FOUR = 5
    FIVE = 6

    # decomposition into number of distinct cards and max count of any card
    __decomp__: dict[tuple[int, int], int] = {
        (1, 5): FIVE,
        (2, 4): FOUR,
        (2, 3): FULL_HOUSE,
        (3, 3): THREE,
        (3, 2): TWO_PAIR,
        (4, 2): ONE_PAIR,
    }

    @classmethod
    def get(cls, n_distinct: int, max_count: int) -> Score:
        return cls.__decomp__.get((n_distinct, max_count), cls.NOTHING)


@dataclass
class Hand:
    cards: str
    bid: int

    @property
    def score(self) -> int:
        return Score.get(len(set(self.cards)), max(Counter(self.cards).values()))

    def cast_joker(self) -> Hand:
        # helper to create a hand with jokers replaced by one other card
        cast = lambda other: Hand(self.cards.replace("J", other), self.bid)

        # other cards, sorted by decreasing value
        sorted_others = sorted(self.cards.replace("J", ""), key=lambda card: -card_values2[card])
        repeating_others = [card for card, count in Counter(sorted_others).items() if count > 1]

        # start casting
        n_jokers = self.cards.count("J")
        if n_jokers == 0:
            return Hand(self.cards, self.bid)
        elif n_jokers == 1:
            # if there was a four before, create a five
            if self.score == Score.FOUR:
                return cast(sorted_others[0])
            # if there was a two pair before, create a full house
            if self.score == Score.TWO_PAIR:
                return cast(sorted_others[0])
            # if there was a three before, create a four
            if self.score == Score.THREE:
                return cast(repeating_others[0])
            # if there was a pair before, create a three
            if self.score == Score.ONE_PAIR:
                return cast(repeating_others[0])
            # just create a pair
            return cast(sorted_others[0])
        elif n_jokers == 2:
            # if there was a full house before, we can create a five
            if self.score == Score.FULL_HOUSE:
                return cast(sorted_others[0])
            # if there was a two pair before, we can create a four
            if self.score == Score.TWO_PAIR:
                return cast(repeating_others[0])
            # there was a pair before (the jokers), we can create a three
            return cast(sorted_others[0])
        elif n_jokers == 3:
            # always form a four or a five with the highest other card
            return cast(sorted_others[0])
        elif n_jokers == 4:
            # always form a five with the other card
            return cast(sorted_others[0])
        else:  # n_jokers == 5
            # create highest five
            return Hand("AAAAA", self.bid)


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse hands
    hands: list[Hand] = [
        Hand(line.split()[0], int(line.split()[1]))
        for line in lines
    ]

    # helper to create a comparison function considering scores and card values
    def make_compare(
        get_score: callable[[Hand], int],
        card_values: dict[str, int],
    ) -> callable[[Hand, Hand], int]:
        def comp(hand1: Hand, hand2: Hand) -> int:
            # compare score
            if (score1 := get_score(hand1)) != (score2 := get_score(hand2)):
                return 1 if score1 > score2 else -1

            # compare cards one by one
            for card1, card2 in zip(hand1.cards, hand2.cards):
                if card1 != card2:
                    return 1 if card_values[card1] > card_values[card2] else -1

            raise Exception("tie should not happen")

        return cmp_to_key(comp)

    #
    # part 1
    #

    # sort and compute total winnings
    hands1: list[Hand] = sorted(hands, key=make_compare(lambda hand: hand.score, card_values1))
    total_winnings1: int = sum(rank * hand.bid for rank, hand in enumerate(hands1, 1))

    # results
    print(f"{total_winnings1=} (truth=246163188)")

    #
    # part 2
    #

    # sort and compute total winnings
    hands2: list[Hand] = sorted(hands, key=make_compare(lambda hand: hand.cast_joker().score, card_values2))
    total_winnings2: int = sum(rank * hand.bid for rank, hand in enumerate(hands2, 1))

    # results
    print(f"{total_winnings2=} (truth=245794069)")


if __name__ == "__main__":
    main()

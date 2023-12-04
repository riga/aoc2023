# coding: utf-8

from __future__ import annotations

import os
import re
from collections import defaultdict
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Card:
    id: int
    winning_nums: list[int]
    card_nums: list[int]
    n_matches: int


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse lines
    cards: list[Card] = []
    for line in lines:
        m = re.match(r"^Card\s+(\d+):\s+(.+)\s*\|\s*(.+)\s*$", line)
        card_id, winning_nums, card_nums = m.groups()
        winning_nums: list[id] = list(map(int, winning_nums.strip().split()))
        card_nums: list[id] = list(map(int, card_nums.strip().split()))
        cards.append(Card(
            id=int(card_id),
            winning_nums=winning_nums,
            card_nums=card_nums,
            n_matches=len(set(winning_nums) & set(card_nums)),
        ))

    # part 1
    sum_points: int = sum(
        2**(card.n_matches - 1) if card.n_matches else 0
        for card in cards
    )

    # part 2
    # let's skip F-style cycle detection for now as there shouldn't be one for this to work
    # iterate in reverse order and cache number of cards won to make this O(n)
    num_cards: dict[int, int] = defaultdict(int)
    for card in cards[::-1]:
        num_cards[card.id] = 1 + sum(num_cards[card.id + i] for i in range(1, card.n_matches + 1))
    sum_num_cards: int = sum(num_cards.values())

    # results
    print(f"{sum_points=} (truth=21105)")
    print(f"{sum_num_cards=} (truth=5329815)")


if __name__ == "__main__":
    main()

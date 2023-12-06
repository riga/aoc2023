# coding: utf-8

from __future__ import annotations

import os
import math
from functools import reduce
from operator import mul
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Game:
    duration: int
    distance: int


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse the games
    games: list[Game] = [
        Game(int(duration), int(distance))
        for duration, distance in zip(
            lines[0].split(":", 1)[1].strip().split(),
            lines[1].split(":", 1)[1].strip().split(),
        )
    ]

    #
    # part 1
    #

    # distance function
    get_distance = lambda t, t_wait: max(0, t * t_wait - t_wait ** 2)

    # number of winning options per game
    winning_options: list[list[int]] = []
    for game in games:
        winning_options.append([
            t_wait
            for t_wait in range(1, game.duration)
            if get_distance(game.duration, t_wait) > game.distance
        ])

    # results
    product_options: int = reduce(mul, map(len, winning_options))
    print(f"{product_options=} (truth=861300)")

    #
    # part 2
    #

    # combine numbers into a single game
    game2: Game = Game(
        int(lines[0].split(":", 1)[1].strip().replace(" ", "")),
        int(lines[1].split(":", 1)[1].strip().replace(" ", "")),
    )

    # brute force
    # n_options: int = 0
    # for t_wait in range(1, game2.duration):
    #     n_options += get_distance(game2.duration, t_wait) > game2.distance

    # functional via PQ
    pq = lambda sign: 0.5 * game2.duration + sign * math.sqrt(0.25 * game2.duration**2 - game2.distance)
    n_options: int = int(math.floor(pq(1))) - int(math.ceil(pq(-1))) + 1

    # results
    print(f"{n_options=} (truth=28101347)")


if __name__ == "__main__":
    main()

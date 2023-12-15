# coding: utf-8

from __future__ import annotations

import os
import re
import math
from functools import cache
from typing import TypeAlias


Rows: TypeAlias = tuple[str, ...]

this_dir: str = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    # read rows
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        rows: Rows = tuple(line for line in (line.strip() for line in f.readlines()) if line)

    # helper to rotate left
    def rotate_left(rows: Rows) -> Rows:
        n_rows, n_cols = len(rows), len(rows[0])
        return tuple(
            "".join(rows[j][n_cols - 1 - i] for j in range(n_rows))
            for i in range(n_cols)
        )

    # helper to rotate right
    def rotate_right(rows: Rows) -> Rows:
        n_rows, n_cols = len(rows), len(rows[0])
        return tuple(
            "".join(rows[n_cols - 1 - j][i] for j in range(n_rows))
            for i in range(n_cols)
        )

    # interprete north as left
    rows = rotate_left(rows)

    # helper to shift round rocks to the left
    cre = re.compile(r"(#([^#]+))")
    _shift_left = cache(lambda row: cre.sub(lambda m: "#" + "".join(reversed(sorted(m.group(2)))), "#" + row)[1:])
    shift_left = lambda rows: tuple(map(_shift_left, rows))

    # helper to count the north load
    _count_north_load = cache(lambda row: sum(i for i, stone in enumerate(reversed(row), 1) if stone == "O"))
    count_north_load = lambda rows: sum(map(_count_north_load, rows))

    #
    # part 1
    #

    # just shift to the left, then sum up
    north_load: int = count_north_load(shift_left(rows))

    # results
    print(f"{north_load=} (truth=109661)")

    #
    # part 2
    #

    # helper for perform a full cycle
    @cache
    def cycle(rows: Rows) -> Rows:
        # shift towards north
        rows = shift_left(rows)
        # adjust west to the left and shift
        rows = shift_left(rotate_right(rows))
        # adjust south to the left and shift
        rows = shift_left(rotate_right(rows))
        # adjust east to the left and shift
        rows = shift_left(rotate_right(rows))
        # adjust north to the left again and we're good
        return rotate_right(rows)

    # there must be a repeating pattern of north loads that stabilizes after a couple hundred cycles
    # otherwise the problem might not be solvable in finite time
    history: list[tuple[Rows, int]] = []
    for i in range(1, (test_cycles := 300) + 1):
        rows = cycle(rows)
        history.append((rows, count_north_load(rows)))

    # iteraatively find the length of the sequnce
    for seq_length in range(1, 101):
        if history[-seq_length:] == history[-2 * seq_length:-seq_length]:
            break
    else:
        raise Exception("no repeating pattern found with 100 cycles or less")

    # find the number of cycles that would correspond to the 100_000_000th cycle
    max_cycles: int = 100_000_000
    n_cycle: int = max_cycles - (int(math.ceil((max_cycles - test_cycles) / seq_length))) * seq_length

    # get the load
    north_load = history[n_cycle - 1][1]

    # results
    print(f"{north_load=} (truth=90176)")


if __name__ == "__main__":
    main()

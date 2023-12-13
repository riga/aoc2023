# coding: utf-8

from __future__ import annotations

import os
import re
from functools import cache
from typing import Generator


this_dir: str = os.path.dirname(os.path.abspath(__file__))


def main(*, part: int) -> None:
    assert part in (1, 2)

    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse and pad by one working spring on each side to avoid special cases
    springs: list[tuple[str, tuple[int, ...]]] = []
    scale: int = {1: 1, 2: 5}[part]
    for conditions, broken_counts in (line.split() for line in lines):
        springs.append((
            "." + "?".join([conditions] * scale) + ".",
            tuple(map(int, broken_counts.split(","))) * scale,
        ))

    # helper to get portions of conditions line, starting at the front, that could accomodate
    # n_broken consecutive springs
    def get_sub_conditions(conditions: str, n_broken: int) -> Generator[str, None, None]:
        # look for starting points of patterns "#|?", repeated n_broken times, followed by ".|?",
        # e.g. "##?#." or "##?#?" for n_broken=4
        for m in re.finditer(rf"(?=(((#|\?){{{n_broken}}})(\.|\?)))", conditions):
            start: int = m.span()[0]
            # no need to continue if there is a broken spring before the starting point
            if "#" in conditions[:start]:
                break
            # yield the conditions after the match
            yield conditions[start + n_broken + 1:]

    # helper to count the number of combinations
    # (for long condition lines, sub conditions are often repeated, so cache)
    @cache
    def count_combinations(conditions: str, broken_counts: tuple[int, ...]) -> int:
        # if no spring is broken at all, consider conditions that still have "#" as "no combination"
        if not broken_counts:
            return int("#" not in conditions)
        # recurse by counting combinations of all possible sub conditions
        return sum(
            count_combinations(sub_conditions, broken_counts[1:])
            for sub_conditions in get_sub_conditions(conditions, broken_counts[0])
        )

    # sum up possible combinations per line
    sum_combinations: int = sum(map(lambda args: count_combinations(*args), springs))

    # results
    print(f"{sum_combinations=} (truth={7025 if part == 1 else 11461095383315})")


if __name__ == "__main__":
    main(part=1)
    main(part=2)

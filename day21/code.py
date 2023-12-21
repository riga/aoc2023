# coding: utf-8

"""
Day 21 with dynamic programming, caching and "fiddling with the padding".
"""

from __future__ import annotations

import os
import functools
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Field:
    x: int
    y: int
    is_plot: bool

    def __hash__(self) -> int:
        return hash((self.x, self.y))


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # get dimensions and check for squareness plus symmetry
    dim: int = len(lines)
    assert dim == len(lines[0])
    assert dim % 2 == 1

    # parse fields
    fields: dict[tuple[int, int], Field] = {}
    start: tuple[int, int]
    for j, line in enumerate(lines):
        for i, c in enumerate(line):
            if c == "S":
                start = (i, j)
            fields[(i, j)] = Field(i, j, c != "#")

    # helper to get the set of next options given previous options
    @functools.cache
    def get_next_options(options: frozenset[Field]) -> set[Field]:
        next_options: set[Field] = set()
        for option in options:
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                x = option.x + dx
                y = option.y + dy
                if (x, y) in fields and fields[(x, y)].is_plot:
                    next_options.add(fields[(x, y)])
        return next_options

    # helper to count the number of plots reachable after n steps from a given start
    # assuming that after a large enough number of steps n_conv (height + width + some safety buffer),
    # the number will have converged and oscillates between two values
    @functools.cache
    def count_options(start: tuple[int, int], n_steps: int, n_conv: int = 2 * dim + 10) -> int:
        # when above n_conv, return count for n_conv if both even or odd, otherwise n_conv - 1
        if n_steps > n_conv:
            return count_options(start, n_conv - int((n_steps % 2) != (n_conv % 2)))
        # simulate steps
        options: set[Field] = {fields[start]}
        for _ in range(n_steps):
            options = get_next_options(frozenset(options))
        return len(options)

    #
    # part 1
    #

    # results
    n_options: int = count_options(start, 64)
    print(f"{n_options=} (truth=3677)")

    #
    # part 2
    #

    # helper to draw the options after n steps from a given start for debuggin
    def draw(start: tuple[int, int], n_steps: int) -> None:
        options: set[Field] = {fields[start]}
        for _ in range(n_steps):
            options = get_next_options(frozenset(options))
        with open(os.path.join(this_dir, f"reach__{start[0]}_{start[1]}__{n_steps}.txt"), "w") as f:
            for j, line in enumerate(lines):
                f.write("".join(
                    "O" if fields[(i, j)] in options else c.replace("S", ".")
                    for i, c in enumerate(line)
                ) + "\n")

    # after studying the input, there seem to be three patterns (thanks editor minimap):
    # 1. there is a diamond shaped border of plots that should even out unregular (diagonal) propagation effects
    # 2. there row and column crossing the starting point are free of stones, so neighbors patches are reached optimally
    # 3. the first and last rows and columns are all plots, so there should be no dependence between garden patches
    #    in the limit of infinite steps, so one can treat each patch individually, _but_ accounting for the "phase"
    #    w.r.t. the center since the patch dimension is uneven, so direct neighbor patches will oscillate out-of-sync,
    #    whereas diagonal neighbors will be in-sync (chess-board style)
    # with these observations, one just has to calculate how many garden patches are reachable, when they would be hit
    # the first time, and what the phase w.r.t. the center was
    # also, it looks like the number of steps is chosen such that in the outermost garden patches, those that are only
    # partially populated at the end, the propagation reaches
    # - the center of an edge, in case the propagation started in the center of the opposite edge,
    # - 1/4 of the patch, in case the propagation started in a corner _out-of-phase_, or
    # - 3/4 of the patch, in case the propagation started in a corner _in-phase_
    # confirm this
    n_steps: int = 26501365
    center: int = dim // 2
    assert start == (center, center)
    assert (n_steps - center) % dim == 0

    # thus there are 21 types of garden patches,
    # - 1 x center
    # - 4 x hit from center of edge, fully populated
    # - 4 x hit from center of edge, partially populated
    # - 4 x hit from corner, fully populated
    # - 4 x hit from corner, 1/4 populated
    # - 4 x hit from corner, 3/4 populated
    # and we only need to determine how many patches exist of each type for any direction
    n_edge_full: int = (n_steps - center) // dim - 1
    n_edge_part: int = 1
    n_corner_full_odd: int = sum(range(1, n_edge_full, 2))
    n_corner_full_even: int = sum(range(2, n_edge_full, 2))
    n_corner_34: int = n_edge_full
    n_corner_14: int = n_corner_34 + 1
    n_steps_corner_14: int = n_steps % (2 * dim)
    n_steps_corner_34: int = (n_steps - (dim + 1)) % (2 * dim)

    # count options
    n_options = 0
    # center patch
    n_options += count_options(start, n_steps)
    # patches hit from edge
    for x, y in [(center, 0), (center, dim - 1), (0, center), (dim - 1, center)]:
        # fully populated, odd distance to center (+1 because not in sync, -1 for offset when crossing patches)
        n_options += ((n_edge_full + 1) // 2) * count_options((x, y), n_steps + 0)
        # fully populated, even distance to center (-1 for offset when crossing patches)
        n_options += (n_edge_full // 2) * count_options((x, y), n_steps - 1)
        # partially populated (-1 for offset when crossing patches)
        n_options += n_edge_part * count_options((x, y), dim - 1)
    # patches hit from corner
    for x, y in [(0, 0), (0, dim - 1), (dim - 1, 0), (dim - 1, dim - 1)]:
        # fully populated (as above +0 for odd, and +1 for even)
        n_options += n_corner_full_odd * count_options((x, y), n_steps + 0)
        n_options += n_corner_full_even * count_options((x, y), n_steps + 1)
        # 1/4 populated (-1 for offset when crossing patches)
        n_options += n_corner_14 * count_options((x, y), n_steps_corner_14 - 1)
        # 3/4 populated
        n_options += n_corner_34 * count_options((x, y), n_steps_corner_34)

    # results
    print(f"{n_options=} (truth=609585229256084)")


if __name__ == "__main__":
    main()

# coding: utf-8

from __future__ import annotations

import os
import heapq
from collections import namedtuple
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Node:
    x: int
    y: int
    cost: int


# type alias for a path (not using a dataclass because sorting with multiple keys is a pain):
Path = namedtuple("Path", ["cost", "x", "y", "direction", "n_straight"])


def main(*, part: int) -> None:
    assert part in (1, 2)

    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # get dimensions
    n_rows: int = len(lines)
    n_cols: int = len(lines[0])

    # parse into nodes
    nodes: dict[tuple[int, int], Node] = {}
    for y, line in enumerate(lines, 1):
        for x, c in enumerate(line, 1):
            nodes[(x, y)] = Node(x, y, int(c))

    # start with the top left node with zero cost and no previous direction
    paths: list[Path] = [Path(0, 1, 1, "", 0)]
    seen = set()
    while True:
        # get the next path with the lowest cost
        assert paths
        path = heapq.heappop(paths)

        # found the target?
        if (path.x, path.y) == (n_cols, n_rows):
            break

        # did we get to this node before from the same direction?
        # (caching by both the last direction AND the number of straight steps is key here!)
        key = path[1:]  # use all but the cost to hash
        if key in seen:
            continue
        seen.add(key)

        # check next steps
        for direction in ["u", "d", "l", "r"]:
            # don't go back
            if (path.direction, direction) in [("u", "d"), ("d", "u"), ("l", "r"), ("r", "l")]:
                continue

            # check bounds
            x = path.x + {"l": -1, "r": 1}.get(direction, 0)
            y = path.y + {"u": -1, "d": 1}.get(direction, 0)
            if not (1 <= x <= n_cols) or not (1 <= y <= n_rows):
                continue

            # count straight steps
            n_straight = 1 if direction != path.direction else (path.n_straight + 1)

            # check if the move is valid
            if part == 1:
                if n_straight > 3:
                    continue
            else:
                if (
                    n_straight > 10 or
                    # changed direction but did not complete four straight steps yet
                    (path.direction != direction and path.n_straight < 4 and path.n_straight)
                ):
                    continue

            # add next path
            heapq.heappush(
                paths,
                Path(path.cost + nodes[(x, y)].cost, x, y, direction, n_straight),
            )

    # results
    print(f"{path.cost=} (truth={674 if part == 1 else 773})")


if __name__ == "__main__":
    main(part=1)
    main(part=2)

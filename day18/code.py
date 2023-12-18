# coding: utf-8

from __future__ import annotations

import os
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Instruction:
    d: str
    n: int


@dataclass
class Point:
    x: int
    y: int


def main(*, part: int) -> None:
    assert part in (1, 2)

    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse the instructions
    instructions: list[Instruction] = []
    for line in lines:
        d, n, col = line.split()
        instructions.append(Instruction(
            d if part == 1 else "RDLU"[int(col[-2])],
            int(n) if part == 1 else int(col[2:-2], 16),
        ))

    # get corner points and count the number of edge points
    corners: list[Point] = [Point(1, 1)]
    n_edge_points: int = 0
    for inst in instructions:
        corners.append(Point(
            corners[-1].x + inst.n * {"L": -1, "R": 1}.get(inst.d, 0),
            corners[-1].y + inst.n * {"U": -1, "D": 1}.get(inst.d, 0),
        ))
        n_edge_points += inst.n

    # the corners form a polygon, so use shoelacing to get the area (c.f. day 10)
    # (instead of multiplying with 0.5, integer division is ok since the area will be an integer)
    n_corners = len(corners)
    area: int = abs(sum(
        corners[i].x * (corners[(i + 1) % n_corners].y - corners[(i - 1) % n_corners].y)
        for i in range(n_corners)
    )) // 2

    # include the edge, assuming that the area calculation already takes half of it into account
    # (again, the number of edge points is always even by construction, so integer division is ok)
    n_inside: int = area + n_edge_points // 2 + 1

    # results
    print(f"{n_inside} (truth={44436 if part == 1 else 106941819907437})")


if __name__ == "__main__":
    main(part=1)
    main(part=2)

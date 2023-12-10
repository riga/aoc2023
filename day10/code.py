# coding: utf-8

from __future__ import annotations

import os
import itertools
import functools
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class LoopPoint:
    # coordinates
    x: int
    y: int

    # value
    v: str

    # neighbors
    t: LoopPoint | None = None
    r: LoopPoint | None = None
    b: LoopPoint | None = None
    l: LoopPoint | None = None

    def __hash__(self) -> int:
        return hash(self.coord)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y}, v={self.v})"

    @property
    def coord(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def neighbors(self) -> dict[str, LoopPoint]:
        return dict([(d, n) for d in "trbl" if (n := getattr(self, d))])


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse points that make up the maze, remember the start
    maze: dict[tuple[int, int], LoopPoint] = {}
    start: LoopPoint | None = None
    for y, line in enumerate(lines):
        for x, v in enumerate(line):
            maze[(x, y)] = LoopPoint(x, y, v)
            if v == "S":
                start = maze[(x, y)]

    # fill neighbors
    prod = functools.cache(lambda *args: set(itertools.product(*args)))
    for point in maze.values():
        if (p := maze.get((point.x, point.y - 1))) and (point.v, p.v) in prod("S|JL", "S|7F"):
            point.t = p
        if (p := maze.get((point.x, point.y + 1))) and (point.v, p.v) in prod("S|7F", "S|JL"):
            point.b = p
        if (p := maze.get((point.x - 1, point.y))) and (point.v, p.v) in prod("S-J7", "S-LF"):
            point.l = p
        if (p := maze.get((point.x + 1, point.y))) and (point.v, p.v) in prod("S-LF", "S-J7"):
            point.r = p

    # replace the correct starting field
    start.v = {"tl": "J", "tb": "|", "bl": "7", "rl": "-", "rb": "F"}["".join(start.neighbors)]

    #
    # part 1
    #

    # find points on the loop
    loop: set[LoopPoint] = set()
    cur: LoopPoint = start
    while True:
        loop.add(cur)
        if not (next_d := [d for d, n in cur.neighbors.items() if n not in loop]):
            break
        cur = getattr(cur, next_d[0])

    # get the distance as half the loop length (floored)
    max_dist: int = len(loop) >> 1

    # results
    print(f"{max_dist=} (truth=6757)")

    #
    # part 2
    #

    # get the bounding box containing the loop within the maze
    x_min = min(p.x for p in loop)
    x_max = max(p.x for p in loop)
    y_min = min(p.y for p in loop)
    y_max = max(p.y for p in loop)

    # for each line, scan from left to right and count the number of real crossings over the loop
    # then, count a normal field if the number of crossings is odd
    n_inside: int = 0
    for y in range(y_min, y_max + 1):
        n_crossings: int = 0
        loop_start: LoopPoint | None = None
        for x in range(x_min, x_max + 1):
            p: LoopPoint = maze.get((x, y))
            if p in loop:
                if loop_start is None:
                    if p.v in ("F", "L"):
                        # start running on the loop
                        loop_start = p
                    else:
                        # entering perpendicularly
                        n_crossings += 1
                elif p.v == "-":
                    # continuing walking on it
                    pass
                elif (loop_start.v, p.v) in (("F", "7"), ("L", "J")):
                    # leaving without ever having entered
                    loop_start = None
                else:
                    # entered
                    n_crossings += 1
                    loop_start = None
            elif n_crossings % 2 == 1:
                # normal field, _inside_ the loop
                n_inside += 1

    # results
    print(f"{n_inside=} (truth=523)")


if __name__ == "__main__":
    main()

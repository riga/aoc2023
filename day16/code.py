# coding: utf-8

from __future__ import annotations

import os
from dataclasses import dataclass, field


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Tile:
    x: int
    y: int
    symbol: str
    reached_from: set[str] = field(default_factory=set)

    @property
    def energized(self) -> bool:
        return len(self.reached_from) > 0

    def reset(self) -> None:
        self.reached_from.clear()


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse tiles
    tiles: dict[tuple[int, int], Tile] = {}
    for y, line in enumerate(lines, 1):
        for x, symbol in enumerate(line, 1):
            tiles[(x, y)] = Tile(x, y, symbol)

    # the field is a square, so get the side length
    n_side: int = len(lines)

    # helper to calculate the next coordinate given a direction
    def next_coord(x: int, y: int, direction: str) -> tuple[int, int]:
        return (x + {"r": 1, "l": -1}.get(direction, 0), y + {"d": 1, "u": -1}.get(direction, 0))

    # helper to propagate a beam given a starting point and direction
    def propagate_beam(x: int, y: int, direction: str) -> None:
        # reset tiles
        tile: Tile | None
        for tile in tiles.values():
            tile.reset()

        # start propagation
        beams: list[tuple[tuple[int, int], str]] = [((x, y), direction)]
        while beams:
            coord, direction = beams.pop()

            # out of bounds?
            if not (tile := tiles.get(coord)):
                continue

            # has this tile already been reached from this side?
            if direction in tile.reached_from:
                continue

            # energize it
            tile.reached_from.add(direction)

            # propagate
            if tile.symbol == ".":
                # continue propagating
                beams.append((next_coord(*coord, direction), direction))
            elif tile.symbol == "|":
                if direction in "rl":
                    # add new beams
                    beams.append((next_coord(*coord, "u"), "u"))
                    beams.append((next_coord(*coord, "d"), "d"))
                else:
                    # just propagate
                    beams.append((next_coord(*coord, direction), direction))
            elif tile.symbol == "-":
                if direction in "ud":
                    # add new beams
                    beams.append((next_coord(*coord, "r"), "r"))
                    beams.append((next_coord(*coord, "l"), "l"))
                else:
                    # just propagate
                    beams.append((next_coord(*coord, direction), direction))
            elif tile.symbol == "/":
                # reflect
                new_direction = {"r": "u", "l": "d", "d": "l", "u": "r"}[direction]
                beams.append((next_coord(*coord, new_direction), new_direction))
            elif tile.symbol == "\\":
                # reflect
                new_direction = {"r": "d", "l": "u", "d": "r", "u": "l"}[direction]
                beams.append((next_coord(*coord, new_direction), new_direction))
            else:
                assert False

    # helper to get the number of currently energized tiles
    def count_energized() -> int:
        return sum(1 for tile in tiles.values() if tile.energized)

    #
    # part 1
    #

    # propagate and count
    propagate_beam(1, 1, "r")
    n_energized: int = count_energized()

    # results
    print(f"{n_energized=} (truth=7111)")

    #
    # part 2
    #

    # propagate from each edge tile
    n_energized = 0
    for i in range(1, n_side + 1):
        # top edge
        propagate_beam(i, 1, "d")
        n_energized = max(n_energized, count_energized())
        # bottom edge
        propagate_beam(i, n_side, "u")
        n_energized = max(n_energized, count_energized())
        # left edge
        propagate_beam(1, i, "r")
        n_energized = max(n_energized, count_energized())
        # right edge
        propagate_beam(n_side, i, "l")
        n_energized = max(n_energized, count_energized())

    print(f"{n_energized=} (truth=7831)")


if __name__ == "__main__":
    main()

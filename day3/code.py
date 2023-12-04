# coding: utf-8

from __future__ import annotations

import os
import re
from operator import mul
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Part:
    num: str
    i: int
    j: int

    def __hash__(self: Part) -> int:
        return hash((self.num, self.i, self.j))


@dataclass
class Symbol:
    c: str
    i: int
    j: int

    def __hash__(self: Symbol) -> int:
        return hash((self.c, self.i, self.j))


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse potential parts and symbols using the same re.search mechanism
    part: list[Part] = []
    symbols: list[Symbol] = []
    for objs, cls, expr in [(part, Part, r"\d+"), (symbols, Symbol, r"[^\.\d]")]:
        for i, line in enumerate(lines):
            offset: int = 0
            while m := re.search(expr, line):
                objs.append(cls(m.group(0), i, offset + m.start()))
                offset += (shift := m.start() + len(m.group(0)))
                line = line[shift:]

    # keep a hashmap of all coordinates that point to a potential part
    coords_to_parts: dict[tuple[int, int], Part] = {}
    for part in part:
        for d in range(len(part.num)):
            coords_to_parts[(part.i, part.j + d)] = part

    # iterate over symbols and look around for actual parts
    parts: set[Part] = set()  # overwrites
    sum_gear_ratio: int = 0
    for sym in symbols:
        # build neighbor coordinates, no need to check bounds since we do explicit hashmap lookups
        neighbors = [
            (sym.i - 1, sym.j - 1), (sym.i - 1, sym.j + 0), (sym.i - 1, sym.j + 1),
            (sym.i + 0, sym.j - 1),                         (sym.i + 0, sym.j + 1),  # noqa
            (sym.i + 1, sym.j - 1), (sym.i + 1, sym.j + 0), (sym.i + 1, sym.j + 1),
        ]
        # check adjacent parts, keeping track of those found for gear ratio
        symbol_parts: set[Part] = set()
        for coord in neighbors:
            if (part := coords_to_parts.get(coord)):
                parts.add(part)
                symbol_parts.add(part)
        # update gear ratio sum iteratively
        if len(symbol_parts) == 2 and sym.c == "*":
            sum_gear_ratio += mul(*(int(part.num) for part in symbol_parts))

    # get sum of parts
    sum_part_ids: int = sum(int(part.num) for part in parts)

    # results
    print(f"{sum_part_ids=} (truth=553079)")
    print(f"{sum_gear_ratio=} (truth=84363105)")


if __name__ == "__main__":
    main()

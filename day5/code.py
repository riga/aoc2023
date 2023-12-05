# coding: utf-8

from __future__ import annotations

import os
import re
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Mapping:
    src_start: int
    dst_start: int
    n: int

    @property
    def src_end(self) -> int:
        return self.src_start + self.n

    def has_src(self, src: int) -> bool:
        return self.src_start <= src < self.src_end

    def get_dst(self, src: int) -> int:
        return self.dst_start + (src - self.src_start)


@dataclass
class Range:
    start: int
    n: int

    def copy(self) -> Range:
        return Range(self.start, self.n)

    @property
    def end(self) -> int:
        return self.start + self.n

    def shift_start(self, offset: int) -> None:
        assert offset <= self.n
        self.start += offset
        self.n -= offset


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse seeds
    seeds: list[int] = list(map(int, [int(s.strip()) for s in lines.pop(0).split(":", 1)[1].strip().split()]))

    # parse ranges into mappings
    mappings: dict[str, list[Mapping]] = {}
    name = None
    for line in lines:
        if ":" in line:
            # new mapping
            name = "{}_{}".format(*re.match(r"^(\w+)-to-(\w+)\smap.+$", line).groups())
            mappings[name] = []
            continue
        # add to last mapping
        dst_start, src_start, n = map(int, line.split())
        mappings[name].append(Mapping(src_start, dst_start, n))

    # sort mappings by src start
    for _mappings in mappings.values():
        _mappings.sort(key=lambda m: m.src_start)

    #
    # part 1
    #

    # helper to find the location for a seed
    def get_location(seed: int) -> int:
        val = seed
        for _mappings in mappings.values():
            for m in _mappings:
                if m.has_src(val):
                    val = m.get_dst(val)
                    break
        return val

    # results
    min_location: int = min(map(get_location, seeds))
    print(f"part 1: {min_location=} (truth=457535844)")

    #
    # part 2
    #

    # parse seed ranges
    seed_ranges: list[Range] = []
    for i in range(len(seeds) // 2):
        seed_ranges.append(Range(seeds[i * 2], seeds[i * 2 + 1]))

    # helper to find the ranges of the next mapping layer for a range
    def get_next_ranges(r: Range, mappings: list[Mapping]) -> list[Range]:
        r = r.copy()
        next_ranges: list[Range] = []
        for m in mappings:
            start, end = m.src_start, m.src_end
            if end <= r.start:
                continue
            if start >= r.end:
                break
            start = max(start, r.start)
            end = min(end, r.end)
            # uncovered range before mapping
            if start > r.start:
                # no mapping covers the range, so keep same values
                next_ranges.append(Range(r.start, offset := start - r.start))
                r.shift_start(offset)
            # add the mapped range
            next_ranges.append(Range(m.get_dst(start), end - start))
            r.shift_start(end - start)
        # handle trailing, uncovered range
        if r.n:
            next_ranges.append(r)
        return next_ranges

    # find all ranges mapped iteratively to all seeds
    ranges = seed_ranges
    for _mappings in mappings.values():
        ranges = sum((get_next_ranges(r, _mappings) for r in ranges), [])

    # results
    min_location: int = min(ranges, key=lambda r: r.start).start
    print(f"part 2: {min_location=} (truth=41222968)")


if __name__ == "__main__":
    main()

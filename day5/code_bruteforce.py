# coding: utf-8

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from multiprocessing import Pool
from multiprocessing.pool import AsyncResult
import time


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Mapping:
    src_start: int
    dst_start: int
    n: int

    def __hash__(self):
        return hash((self.src_start, self.dst_start, self.n))

    def has_src(self, src: int) -> bool:
        return self.src_start <= src < self.src_start + self.n

    def get_src(self, dst: int) -> int:
        return self.src_start + (dst - self.dst_start)

    def has_dst(self, dst: int) -> bool:
        return self.dst_start <= dst < self.dst_start + self.n

    def get_dst(self, src: int) -> int:
        return self.dst_start + (src - self.src_start)


@dataclass
class SeedRange:
    start: int
    n: int

    def __hash__(self):
        return hash((self.start, self.n))

    def has(self, seed: int) -> bool:
        return self.start <= seed < self.start + self.n


# helper to find a seed for a location range defined by i and n, given mappings and seed ranges
def get_seed_for_location_range(i, n, mappings, seed_ranges):
    for location in range(i * n, (i + 1) * n):
        src = location
        for name, _mappings in reversed(mappings.items()):
            for m in _mappings:
                if m.has_dst(src):
                    src = m.get_src(src)
                    break
        if any(sr.has(src) for sr in seed_ranges):
            return location
    return None


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse seeds
    seeds = list(map(int, [int(s.strip()) for s in lines.pop(0).split(":", 1)[1].strip().split()]))

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

    #
    # part 1
    #

    # sort mappings by src start
    mappings1 = {name: sorted(ms, key=lambda m: m.src_start) for name, ms in mappings.items()}

    # helper to find the location for a seed
    def get_location(seed: int) -> int:
        val = seed
        for _mappings in mappings1.values():
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

    # sort mappings by dst start
    mappings2 = {name: sorted(ms, key=lambda m: m.dst_start) for name, ms in mappings.items()}

    # parse seed ranges
    seed_ranges = []
    for i in range(len(seeds) // 2):
        seed_ranges.append(SeedRange(seeds[i * 2], seeds[i * 2 + 1]))

    # go parallel :)
    with Pool(pool_size := 8) as pool:
        results: dict[int, int | AsyncResult | None] = {}
        hit: int | None = None
        while True:
            # check done results
            for s, r in list(results.items()):
                if isinstance(r, AsyncResult) and r.ready():
                    results[s] = r.get()
                    if results[s] is not None:
                        hit = s
                        break

            # stop early if a seed was found
            if hit is not None:
                break

            # fill pool
            n_running: int = sum([1 for r in results.values() if isinstance(r, AsyncResult)])
            if (n_fill := pool_size - n_running) > 0:
                for _ in range(n_fill):
                    i = len(results)
                    args = (i, 100_000, mappings2, seed_ranges)
                    results[i] = (pool.apply_async(get_seed_for_location_range, args))

        # helper to wait for an async result and return its value
        def get_location(r: AsyncResult | int) -> int:
            if isinstance(r, AsyncResult):
                while not r.ready():
                    time.sleep(0.01)
                return r.get()
            return r

        # get all locations up to the hit
        min_location: int = min(
            location
            for location in (
                get_location(r)
                for s, r in results.items()
                if s <= hit
            )
            if location is not None
        )

    # kill left-over processes
    pool.terminate()

    # results
    print(f"part 2: {min_location=} (truth=41222968)")


if __name__ == "__main__":
    main()

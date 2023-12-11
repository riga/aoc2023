# coding: utf-8

from __future__ import annotations

import os
import itertools

import numpy as np


this_dir: str = os.path.dirname(os.path.abspath(__file__))


def main(expansion_factor: int, truth: int) -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # read in the universe as a numpy array
    universe: np.ndarray = np.array([[c == "#" for c in line] for line in lines], dtype=np.int8)

    # get expanding rows and columns
    expand_rows: set[int] = {i for i in range(universe.shape[0]) if not np.any(universe[i, :])}
    expand_cols: set[int] = {j for j in range(universe.shape[1]) if not np.any(universe[:, j])}

    # get galaxy coordinates
    coords: list[tuple[int, int]] = list(zip(*np.where(universe == 1)))

    # distance between two galaxies
    def get_distance(x1: int, y1: int, x2: int, y2: int) -> int:
        # normal distance
        x_min, x_diff = min(x1, x2), abs(x2 - x1)
        y_min, y_diff = min(y1, y2), abs(y2 - y1)
        dist = x_diff + y_diff

        # account for expanded rows and columns in between
        dist += len(set(range(x_min, x_min + x_diff)) & expand_cols) * (expansion_factor - 1)
        dist += len(set(range(y_min, y_min + y_diff)) & expand_rows) * (expansion_factor - 1)

        return dist

    # get sum of distances
    sum_dist: int = sum(
        get_distance(x1, y1, x2, y2)
        for (y1, x1), (y2, x2) in itertools.combinations(coords, 2)
    )

    # results
    print(f"{sum_dist=} ({truth=})")


if __name__ == "__main__":
    main(expansion_factor=2, truth=9686930)
    main(expansion_factor=1_000_000, truth=630728425490)

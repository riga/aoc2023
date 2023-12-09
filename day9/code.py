# coding: utf-8

from __future__ import annotations

import os


this_dir: str = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse sequences
    sequences: list[list[int]] = []
    for line in lines:
        sequences.append(list(map(int, line.split())))

    # helper to get pair-wise differences
    get_diffs = lambda seq: [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]

    #
    # part 1
    #

    # recursive prediction
    def get_next1(seq: list[int]) -> int:
        return seq[0] if len(seq) == 1 else seq[-1] + get_next1(get_diffs(seq))

    # results
    sum_preds1: int = sum(map(get_next1, sequences))
    print(f"{sum_preds1=} (truth=1930746032)")

    #
    # part 2
    #

    # recursive prediction
    def get_next2(seq: list[int]) -> int:
        return seq[0] if len(seq) == 1 else seq[0] - get_next2(get_diffs(seq))

    # results
    sum_preds2: int = sum(map(get_next2, sequences))
    print(f"{sum_preds2=} (truth=1154)")


if __name__ == "__main__":
    main()

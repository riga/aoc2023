# coding: utf-8

from __future__ import annotations

import os
import re


this_dir: str = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse steps
    steps: list[str] = lines[0].split(",")

    def create_hash(s: str) -> int:
        h = 0
        for c in s:
            h = (h + ord(c)) * 17 % 256
        return h

    #
    # part 1
    #

    # sum of hashes
    sum_hashes: int = sum(map(create_hash, steps))

    # results
    print(f"{sum_hashes=} (truth=513172)")

    #
    # part 2
    #

    # setup boxes
    boxes: dict[int, dict[str, int]] = {i: {} for i in range(1, 256 + 1)}

    # apply steps
    for step in steps:
        m = re.match(r"^(.+)(-|=(\d+))$", step)
        assert m is not None
        label = m.group(1)
        box_num = create_hash(label) + 1
        if m.group(2) == "-":
            # remove
            boxes[box_num].pop(label, None)
        else:
            # add
            boxes[box_num][label] = int(m.group(3))

    # sum of powers
    sum_powers: int = sum(
        sum(
            box_num * i * flength
            for i, flength in enumerate(box.values(), 1)
        )
        for box_num, box in boxes.items()
    )

    # results
    print(f"{sum_powers=} (truth=237806)")


if __name__ == "__main__":
    main()

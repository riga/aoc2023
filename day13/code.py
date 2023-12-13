# coding: utf-8

from __future__ import annotations

import os
from functools import cached_property
from dataclasses import dataclass, field


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Pattern:
    lines: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"Pattern(n_rows={self.n_rows}, n_cols={self.n_cols})"

    @cached_property
    def n_rows(self) -> int:
        return len(self.lines)

    @cached_property
    def n_cols(self) -> int:
        return len(self.lines[0])

    @property
    def rows(self) -> list[str]:
        return self.lines

    @cached_property
    def cols(self) -> list[str]:
        return ["".join(row[i] for row in self.lines) for i in range(self.n_cols)]


def main(*, part: int) -> None:
    assert part in (1, 2)

    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line.strip() for line in f.readlines()]

    # parse into patterns
    patterns: list[Pattern] = [Pattern()]
    for line in lines:
        if line:
            patterns[-1].lines.append(line)
        else:
            patterns.append(Pattern())

    # helper to determine number of differing sequence elements
    n_diff = lambda seq1, seq2: sum(1 for i in range(len(seq1)) if seq1[i] != seq2[i])

    # check for vertical symmetry
    sum_left_cols: int = 0
    for pattern in patterns:
        for i in range(1, pattern.n_cols):
            # width of covered area
            w: int = min(i, pattern.n_cols - i)
            if sum(
                n_diff(row[i - w:i], row[i:i + w][::-1])
                for row in pattern.rows
            ) == (0 if part == 1 else 1):
                sum_left_cols += i
                break

    # check for horizontal symmetry
    sum_top_rows: int = 0
    for pattern in patterns:
        for i in range(1, pattern.n_rows):
            # height of covered area
            h: int = min(i, pattern.n_rows - i)
            if sum(
                n_diff(col[i - h:i], col[i:i + h][::-1])
                for col in pattern.cols
            ) == (0 if part == 1 else 1):
                sum_top_rows += i
                break

    # results
    print(f"{sum_left_cols + 100 * sum_top_rows=} (truth={42974 if part == 1 else 27587})")


if __name__ == "__main__":
    main(part=1)
    main(part=2)

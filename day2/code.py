# coding: utf-8

import os


this_dir: str = os.path.dirname(os.path.abspath(__file__))
colors: list[str] = ["red", "green", "blue"]


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # loop through games
    sum_ids: int = 0
    sum_powers: int = 0
    for line in lines:
        # get the game id, the uggly way
        game_id: int = int(line.split(":", 1)[0].split(" ", 1)[1])

        # get the draws for this game
        draws: list[tuple[int, int, int]] = []
        for part in line.split(":", 1)[1].split(";"):
            draw: list[int] = [0, 0, 0]  # r, g, b
            for s in part.strip().split(","):
                n, col = s.strip().split(" ", 1)
                draw[colors.index(col)] = int(n)
            draws.append(tuple(draw))

        # check if possible
        if (
            all(r <= 12 for r, _, _ in draws) and
            all(g <= 13 for _, g, _ in draws) and
            all(b <= 14 for _, _, b in draws)
        ):
            sum_ids += game_id

        # add power
        sum_powers += (
            max(r for r, _, _ in draws) *
            max(g for _, g, _ in draws) *
            max(b for _, _, b in draws)
        )

    # results
    print(f"{sum_ids=} (truth=2545)")
    print(f"{sum_powers=} (truth=78111)")


if __name__ == "__main__":
    main()

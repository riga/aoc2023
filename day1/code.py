# coding: utf-8

import os
import re


this_dir: str = os.path.dirname(os.path.abspath(__file__))

string_nums: dict[str, str] = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


def main(part_two: bool = False) -> None:
    # read the file
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # sum values
    sum_nums: int = 0
    for line in lines:
        if not part_two:
            nums = re.findall(r"(?=(\d))", line)
        else:
            nums = [
                string_nums.get(num, num)
                for num in re.findall(rf"(?=(\d|{'|'.join(string_nums)}))", line)
            ]
        num = f"{nums[0]}{nums[-1]}"
        sum_nums += int(num)

    # print
    print(f"{sum_nums=} (truth={53868 if part_two else 54953})")


if __name__ == "__main__":
    main(part_two=False)
    main(part_two=True)

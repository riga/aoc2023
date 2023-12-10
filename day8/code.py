# coding: utf-8

from __future__ import annotations

import os
import re
import math
from dataclasses import dataclass


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Node:
    name: str
    left: Node | None = None
    right: Node | None = None

    def next(self, instruction: str) -> Node:
        return self.left if instruction == "L" else self.right


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse instructions
    instructions = lines[0].strip().upper()
    assert set(instructions) == {"L", "R"}
    n_instructions = len(instructions)

    # parse map nodes
    nodes: dict[str, Node] = {
        name: Node(name)
        for name in (line.split("=")[0].strip() for line in lines[1:])
    }
    # add left and right references
    for line in lines[1:]:
        name, left, right = re.match(r"(\w{3})\s*\=\s*\((\w{3}),\s*(\w{3})\)", line).groups()
        nodes[name].left = nodes[left]
        nodes[name].right = nodes[right]

    #
    # part 1
    #

    # start traversing
    steps1: int = 0
    node: Node = nodes["AAA"]
    while node.name != "ZZZ":
        node = node.next(instructions[steps1 % n_instructions])
        steps1 += 1

    # results
    print(f"{steps1=} (truth=19637)")

    #
    # part 2
    #

    # get a nodes
    a_nodes: list[Node] = [node for node in nodes.values() if node.name.endswith("A")]

    # helper to get the first z node and steps needed to go there
    def get_z_node(node: Node) -> tuple[Node, int]:
        steps: int = 0
        while not node.name.endswith("Z"):
            node = node.next(instructions[steps % n_instructions])
            steps += 1
        return node, steps

    # ... for a fully generic map, only a brute force method should be possible (maybe with some
    # partial caching, but still), so this cannot be the case here; instead do a check:
    # does every a node end up in only one z node and then cycle back?
    first_z_nodes: list[tuple[Node, int]] = list(map(get_z_node, a_nodes))
    for a_node, (z_node, steps) in zip(a_nodes, first_z_nodes):
        # steps must be a multiple of the number of instructions
        assert steps % n_instructions == 0
        # the node after the z node must be the one behind the a node after the first instruction
        assert (z_node.next((steps + 1) % n_instructions) == a_node.next(instructions[0]))

    # in this special case, the number of total steps is just the least common multiple
    steps2: int = math.lcm(*(steps for _, steps in first_z_nodes))

    # results
    print(f"{steps2=} (truth=8811050362409)")


if __name__ == "__main__":
    main()

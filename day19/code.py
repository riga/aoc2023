# coding: utf-8

from __future__ import annotations

import os
import re
import functools
from operator import lt, gt, mul
from dataclasses import dataclass, field
from typing import Callable, TypeAlias


this_dir: str = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Part:
    ratings: dict[str, int]

    @property
    def sum_ratings(self) -> int:
        return sum(self.ratings.values())


@dataclass
class Condition:
    attr: str
    op: Callable[[int, int], bool]
    threshold: int
    target: Rule | bool
    test_reverse: bool = False

    def __repr__(self):
        rev_str = "!" if self.test_reverse else ""
        return f"Condition({self.attr} {rev_str}{self.op.__name__} {self.threshold})"

    def _test(self, val: int) -> bool:
        return self.op(val, self.threshold) is not self.test_reverse

    def test(self, part: Part) -> bool:
        return self._test(part.ratings[self.attr])

    def reversed(self) -> Condition:
        return Condition(self.attr, self.op, self.threshold, self.target, not self.test_reverse)


@dataclass
class Rule:
    name: str
    condition_line: str
    conditions: list[Condition] = field(default_factory=list)
    decision: bool | Rule = False

    def __repr__(self):
        return f"Rule({self.name})"

    def __hash__(self):
        return hash(self.name)


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse into rules and parts
    rules: dict[str, Rule] = {}
    parts: list[Part] = []
    for line in lines:
        if (m_rule := re.match(r"^(.+)\{(.+)\}", line)):
            rules[m_rule.group(1)] = Rule(m_rule.group(1), m_rule.group(2))
        elif (m_part := re.match(r"^\{x=(\d+),m=(\d+),a=(\d+),s=(\d+)\}", line)):
            parts.append(Part(dict(zip("xmas", map(int, m_part.groups())))))

    # expand rule conditions and set final decisions
    for name, rule in rules.items():
        for cond_str in rule.condition_line.split(","):
            if (m_cond := re.match(r"^(x|m|a|s)(<|>)(\d+):(.+)$", cond_str)):
                rule.conditions.append(Condition(
                    m_cond.group(1),
                    lt if m_cond.group(2) == "<" else gt,
                    int(m_cond.group(3)),
                    m_cond.group(4) == "A" if m_cond.group(4) in "AR" else rules[m_cond.group(4)],
                ))
            elif cond_str in "AR":
                rule.decision = cond_str == "A"
            else:
                rule.decision = rules[cond_str]

    #
    # part 1
    #

    # helper to check if a part is accepted
    def is_accepted(part: Part) -> bool:
        rule = rules["in"]
        while rule is not None:
            # check conditions in order
            for cond in rule.conditions:
                if cond.test(part):
                    if isinstance(cond.target, bool):
                        return cond.target
                    rule = cond.target
                    break
            else:
                # no condition matched, check the final decision
                if isinstance(rule.decision, bool):
                    return rule.decision
                rule = rule.decision

    # check parts and sum ratings
    sum_ratings = sum(part.sum_ratings for part in parts if is_accepted(part))

    # results
    print(f"{sum_ratings=} (truth=456651)")

    #
    # part 2
    #

    NestedConditions: TypeAlias = list[list[Condition]]
    leaf_conditions: dict[Rule, NestedConditions] = {}

    def get_leaf_conds(rule: Rule) -> NestedConditions:
        # get from cache
        if rule in leaf_conditions:
            return leaf_conditions[rule]

        conds: NestedConditions = []

        # handle rule conditions
        reversed_conds: list[Condition] = []
        for cond in rule.conditions:
            if isinstance(cond.target, bool):
                if cond.target:
                    conds.append(list(reversed_conds) + [cond])
            else:
                conds += [reversed_conds + [cond] + _conds for _conds in get_leaf_conds(cond.target)]
            reversed_conds.append(cond.reversed())

        # handle final rule decision
        if isinstance(rule.decision, bool):
            if rule.decision:
                conds.append(reversed_conds)
        else:
            conds += [reversed_conds + _conds for _conds in get_leaf_conds(rule.decision)]

        # cache and return
        leaf_conditions[rule] = conds
        return conds

    # sum up conditions
    n_combinations: int = 0
    for conds in get_leaf_conds(rules["in"]):
        # per attribute, check how many values pass all conditions
        n_vals = [
            sum(1 for v in range(1, 4001) if all(c._test(v) for c in conds if c.attr == attr))
            for attr in "xmas"
        ]
        n_combinations += functools.reduce(mul, n_vals)

    # results
    print(f"{n_combinations=} (truth=131899818301477)")


if __name__ == "__main__":
    main()

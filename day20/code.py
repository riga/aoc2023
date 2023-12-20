# coding: utf-8

"""
Day 20, solved with fulll over-engineered OOP and event queues :)
"""

from __future__ import annotations

import os
import math
from functools import partial
from collections import deque
from dataclasses import dataclass, field
from typing import TypeAlias, Callable


this_dir: str = os.path.dirname(os.path.abspath(__file__))

Queue: TypeAlias = deque[Callable[[], None]]


@dataclass
class Counter:
    n_low: int = 0
    n_high: int = 0

    def reset(self) -> None:
        self.n_high = 0
        self.n_low = 0

    def add(self, state: bool) -> None:
        if state:
            self.n_high += 1
        else:
            self.n_low += 1


@dataclass
class Module:
    name: str


@dataclass
class HasInputs(Module):
    inputs: dict[str, Module] = field(default_factory=dict)
    in_counter: Counter = field(default_factory=Counter)

    def receive(self, in_name: str, signal: bool, queue: Queue, global_out_counter: Counter | None = None) -> None:
        raise NotImplementedError

    def reset_in_counter(self) -> None:
        self.in_counter.reset()


@dataclass
class HasOutputs(Module):
    outputs: dict[str, Module] = field(default_factory=dict)
    out_counter: Counter = field(default_factory=Counter)

    def emit(self, signal: bool, queue: Queue, global_out_counter: Counter | None = None) -> None:
        for out_mod in self.outputs.values():
            self.out_counter.add(signal)
            if global_out_counter:
                global_out_counter.add(signal)
            queue.append(partial(out_mod.receive, self.name, signal, queue, global_out_counter))

    def reset_out_counter(self) -> None:
        self.out_counter.reset()


class HasState:

    def is_default_state(self) -> bool:
        raise NotImplementedError

    def reset_state(self) -> None:
        raise NotImplementedError


class Broadcaster(HasOutputs):
    pass


@dataclass
class Output(HasInputs):

    def receive(self, in_name: str, signal: bool, queue: Queue, global_out_counter: Counter | None = None) -> None:
        # just update counter
        self.in_counter.add(signal)


@dataclass
class FlipFlop(HasInputs, HasOutputs, HasState):
    state: bool = False

    def receive(self, in_name: str, signal: bool, queue: Queue, global_out_counter: Counter | None = None) -> None:
        self.in_counter.add(signal)
        # do nothing on HI
        if signal:
            return
        # flip state on LO
        self.state = not self.state
        # send new state to outputs
        self.emit(self.state, queue, global_out_counter)

    def is_default_state(self) -> bool:
        return not self.state

    def reset_state(self) -> None:
        self.state = False


@dataclass
class Conjunction(HasInputs, HasOutputs, HasState):
    states: dict[str, bool] = field(default_factory=dict)

    def receive(self, in_name: str, signal: bool, queue: list, global_out_counter: Counter | None = None) -> None:
        self.in_counter.add(signal)
        # update state
        self.states[in_name] = signal
        # determine the signal to send
        out_signal = not all(self.states.values())
        # dispatch to outputs
        self.emit(out_signal, queue, global_out_counter)

    def is_default_state(self) -> bool:
        return not any(self.states.values())

    def reset_state(self) -> None:
        self.states.clear()
        self.states.update({in_name: False for in_name in self.inputs})


def main() -> None:
    # read lines
    with open(os.path.join(this_dir, "data.txt"), "r") as f:
        lines: list[str] = [line for line in (line.strip() for line in f.readlines()) if line]

    # parse modules
    modules: dict[str, Module] = {}
    for line in lines:
        front = line.replace(" ", "").split("->", 1)[0]
        name = front[1:] if front.startswith(("%", "&")) else front
        cls = {"%": FlipFlop, "&": Conjunction, "b": Broadcaster}[front[0]]
        modules[name] = cls(name=name)

    # connect them, determine which one is the output module
    found_output: bool = False
    for line in lines:
        front, back = line.replace(" ", "").split("->", 1)
        name = front[1:] if front.startswith(("%", "&")) else front
        for out_name in back.split(","):
            # create the output module if it doesn't exist yet
            if out_name not in modules:
                assert not found_output
                out_name = "output"
                modules[out_name] = Output(name=out_name)
                found_output = True
            # connect
            modules[name].outputs[out_name] = modules[out_name]
            modules[out_name].inputs[name] = modules[name]

    # helper to reset states
    def reset_states() -> None:
        for mod in modules.values():
            if isinstance(mod, HasState):
                mod.reset_state()

    # helper to reset input counters
    def reset_counters() -> None:
        for mod in modules.values():
            if isinstance(mod, HasInputs):
                mod.reset_in_counter()
            if isinstance(mod, HasOutputs):
                mod.reset_out_counter()

    #
    # part 1
    #

    # setup counter and queue, reset states
    counter: Counter = Counter()
    queue: Queue = deque()
    reset_states()

    # run several times
    for _ in range(1000):
        # reset input counters
        reset_counters()
        # start with button push
        counter.add(False)
        queue.append(partial(modules["broadcaster"].emit, False, queue, counter))
        # run the event queue
        while queue:
            queue.popleft()()

    # results
    prod: int = counter.n_low * counter.n_high
    print(f"{prod=} (truth=794930686)")

    #
    # part 2
    #

    # reset things
    queue.clear()
    reset_states()
    reset_counters()

    # after some testing, it's clear that pushing the button n times takes too much time, and it
    # seems that the input is connected to a conjunction (X) that is itself connected to several
    # conjunctions (A, B, C, D) this means that for X to send LO to the output, it has to receive
    # only HI's from A - D; so just as for the tree cycles of day 8, assume that they all send HI
    # on specific cycles and hope that the least common multiple of their lengths is the answer

    # get the second-to-last conjunctions
    conjs: list[Conjunction] = [modules[name] for name in modules[list(modules["output"].inputs)[0]].inputs]

    # press the button several times and remember how long it took per conjunction
    n_pressed: dict[str, int] = {}
    n: int = 0
    while len(n_pressed) < len(conjs):
        # push button
        queue.append(partial(modules["broadcaster"].emit, False, queue))
        n += 1
        # run the event queue
        while queue:
            queue.popleft()()
        # check if the conjunctions are HI
        for conj in conjs:
            if conj.name not in n_pressed and conj.out_counter.n_high == 1:
                n_pressed[conj.name] = n

    # results
    n_total: int = math.lcm(*n_pressed.values())
    print(f"{n_total=} (truth=244465191362269)")


if __name__ == "__main__":
    main()

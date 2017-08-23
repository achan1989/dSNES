# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import collections

import dsnes


class Analyser:
    def __init__(self, project):
        self.project = project
        self.state = None
        self.disassembly = None
        # List of (target, from) tuples.
        self.calls = None
        self.visited = None
        self.reset()

    def reset(self):
        self.state = dsnes.State()
        self.disassembly = []
        self.calls = []
        self.visited = set()

    def analyse_function(self, address):
        self.reset()
        orig_addr = address
        bus = self.project.bus
        db = self.project.database
        queue = collections.deque()
        queue.append(orig_addr)
        # By default we don't know what state the CPU is in.
        calculated_state = dsnes.State()

        while queue:
            address = queue.pop()

            while True:
                if address in self.visited:
                    break

                # If the user claims to know the state for this instruction,
                # use it.
                declared_state = db.get_state(address)
                if declared_state is not None:
                    self.state = declared_state
                # Otherwise use the state that was calculated by executing the
                # previous instruction.
                else:
                    self.state = calculated_state

                disassembly = dsnes.disassemble(address, bus, self.state)
                self.disassembly.append(disassembly)
                calculated_state = disassembly.new_state

                do_next = disassembly.next_addr
                action, data = do_next[0], do_next[1:]

                if action in (dsnes.NextAction.step, dsnes.NextAction.jump):
                    # Temporarily treat jump like a step.
                    next_addr = data[0]
                elif action is dsnes.NextAction.call:
                    target, after_return = data
                    self.calls.append((target, address))
                    next_addr = after_return
                elif action is dsnes.NextAction.branch:
                    taken_addr, not_taken_addr = data
                    next_addr = taken_addr
                    queue.append(not_taken_addr)
                else:
                    raise NotImplementedError(
                        "Analyser can't handle {}".format(action))

                self.visited.add(address)
                address = next_addr

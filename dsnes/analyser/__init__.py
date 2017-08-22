# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes


class Analyser:
    def __init__(self, project):
        self.project = project
        self.state = None
        self.disassembly = None
        # List of (target, from) tuples.
        self.calls = None
        self.reset()

    def reset(self):
        self.state = dsnes.State()
        self.disassembly = []
        self.calls = []

    def analyse_function(self, address):
        self.reset()
        bus = self.project.bus
        db = self.project.database
        orig_addr = address
        # By default we don't know what state the CPU is in.
        calculated_state = dsnes.State()

        while True:
            # If the user claims to know the state for this instruction, use it.
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
                address = data[0]
            elif action is dsnes.NextAction.call:
                target, after_return = data
                self.calls.append((target, address))
                address = after_return
            else:
                raise NotImplementedError(
                    "Analyser can't handle {}".format(action))

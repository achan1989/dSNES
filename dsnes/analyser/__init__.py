# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes


class Analyser:
    def __init__(self, project):
        self.project = project
        self.state = None
        self.disassembly = []

    def reset(self):
        self.state = dsnes.State()
        self.disassembly = []

    def analyse_function(self, address):
        self.reset()
        bus = self.project.bus
        db = self.project.database
        orig_addr = address
        # By default we don't know what state the CPU is in.
        calculated_state = (None, None, None)

        while True:
            # If the user claims to know the state for this instruction, use it.
            declared_state = db.get_state(address)
            if declared_state is not None:
                self.state = declared_state
                s = self.state
            # Otherwise use the state that was calculated by executing the
            # previous instruction.
            else:
                s = self.state
                s.e, s.m, s.x = calculated_state

            disassembly = dsnes.disassemble(address, bus, s.e, s.m, s.x)
            self.disassembly.append(disassembly)
            address = disassembly.next_addr
            calculated_state = disassembly.new_state

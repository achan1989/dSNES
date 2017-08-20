# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes


class State:
    def __init__(self):
        self.e = None
        self.m = None
        self.x = None


class Analyser:
    def __init__(self, project):
        self.project = project
        self.state = None
        self.disassembly = []

    def reset(self):
        self.state = State()
        self.disassembly = []

    def analyse_function(self, address):
        self.reset()
        bus = self.project.bus
        orig_addr = address

        while True:
            s = self.state
            disassembly = dsnes.disassemble(address, bus, s.e, s.m, s.x)
            self.disassembly.append(disassembly)
            address = disassembly.next_addr

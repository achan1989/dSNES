# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes
from . import database


class State:
    def __init__(self, e=None, m=None, x=None):
        self.e = None
        if e is not None:
            self.e = bool(e)

        self.m = None
        if m is not None:
            self.m = bool(m)

        self.x = None
        if x is not None:
            self.x = bool(x)

    def clone(self):
        cls = self.__class__
        return cls(e=self.e, m=self.m, x=self.x)

    def encode(self):
        s = ""
        for flag in ("e", "m", "x"):
            value = getattr(self, flag)
            if value is not None:
                value = bool(value)
                s += flag.upper() if value else flag
        return s or None

    @classmethod
    def parse(cls, s):
        lookup = {
            "e": {"e": False},
            "E": {"e": True},
            "m": {"m": False},
            "M": {"m": True},
            "x": {"x": False},
            "X": {"x": True}
        }
        kwargs = {}
        try:
            for letter in s:
                kwargs.update(lookup[letter])
        except LookupError:
            raise ValueError("'{}' is not a valid State encoding".format(s))
        if kwargs:
            return cls(**kwargs)
        else:
            return None

    def __repr__(self):
        return "<{cls} e={e} m={m} x={x}>".format(
            cls=self.__class__.__name__,
            e=self.e, m=self.m, x=self.x)


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

    @staticmethod
    def parse_state(s):
        return State.parse(s)

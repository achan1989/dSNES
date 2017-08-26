# Copyright 2017 Adrian Chan
# Licensed under GPLv3

from dsnes import project
from dsnes.analyser import Analyser, database
from dsnes.bus import Bus
from dsnes.cartridge import Cartridge
from dsnes.disassembler import disassemble, NextAction
from dsnes.cpustate import State
from dsnes.memory import Rom, cpureg, dmareg

class UnmappedMemoryAccess(ValueError):
    pass

class AmbiguousDisassembly(Exception):
    def __init__(self, mnemonic, requires):
        super().__init__(mnemonic, requires)
        self.mnemonic = mnemonic
        self.requires = requires

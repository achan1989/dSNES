# Copyright 2017 Adrian Chan
# Licensed under GPLv3

from dsnes import project
from dsnes import interactive
from dsnes import ui
from dsnes.analyser import Analyser, database
from dsnes.bus import Bus
from dsnes.cartridge import Cartridge
from dsnes.disassembler import disassemble, NextAction
from dsnes.cpustate import State, StateDelta
from dsnes.memory import Rom, apureg, cpureg, dmareg, ppureg, superfxreg

class UnmappedMemoryAccess(ValueError):
    pass

class AmbiguousDisassembly(Exception):
    def __init__(self, mnemonic, requires):
        super().__init__(mnemonic, requires)
        self.mnemonic = mnemonic
        self.requires = requires

class InvalidDisassembly(Exception):
    pass

class BusReadImpossible(Exception):
    pass

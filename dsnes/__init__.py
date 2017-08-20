# Copyright 2017 Adrian Chan
# Licensed under GPLv3

from dsnes import project

class UnmappedMemoryAccess(ValueError):
    pass

class AmbiguousDisassembly(Exception):
    def __init__(self, mnemonic, requires):
        super().__init__(mnemonic, requires)
        self.mnemonic = mnemonic
        self.requires = requires

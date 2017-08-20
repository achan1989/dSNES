from dsnes import project

class AmbiguousDisassembly(Exception):
    def __init__(self, mnemonic, requires):
        super().__init__(mnemonic, requires)
        self.mnemonic = mnemonic
        self.requires = requires

class Instruction():
    def __init__(self, address, instr_desc, operands):
        self.address = address
        self.instr_desc = instr_desc
        self.operands = operands

    @property
    def assembly_string(self):
        mnemonic = self.instr_desc.mnemonic
        operands = "todo..."
        #operands = self.instr_desc.handler_class(self.operands).operands_string
        return " ".join((mnemonic, operands))

    @property
    def size(self):
        return self.instr_desc.size

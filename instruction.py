class BaseInstruction():
    # The following class variables will be available (will be set by child
    # classes, access as self._Blah):
    # _Opcode
    # _Mnemonic
    # _Kind
    # _Operand_size

    def __init__(self, mem, address):
        self._address = address
        self._operands = self._get_operands(mem)

    def _get_operands(self, mem):
        """ Get the operands for this instruction. """
        address = self._address
        num_operands = self._Operand_size
        operands = tuple()

        while num_operands > 0:
            address += 1
            operands += (mem[address],)
            num_operands -= 1
        return operands

    @property
    def assembly_string(self):
        operands = "[{} operand bytes todo]".format(self._Operand_size)
        return " ".join((self._Mnemonic, operands))

    @property
    def size(self):
        return 1 + self._Operand_size

    @property
    def operands(self):
        return self._operands

    @property
    def address(self):
        return self._address

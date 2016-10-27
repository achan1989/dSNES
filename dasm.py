import opcodes
from instruction import Instruction


def disassemble_instruction(mem, address):
    opcode = mem[address]
    instr_desc = opcodes.opcode_table[opcode]
    operands = get_operands(mem, address, instr_desc)

    instruction = Instruction(address, instr_desc, operands)
    return instruction

def get_operands(mem, address, instr_desc):
    """ Get the operands for the instruction at the given address. """
    num_operands = instr_desc.size - 1
    assert num_operands >= 0

    operands = []
    while num_operands > 0:
        address += 1
        operands.append(mem[address])
        num_operands -= 1
    return operands

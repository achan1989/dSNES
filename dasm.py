import opcodes


def disassemble_instruction(mem, address):
    opcode = mem[address]
    instruction = opcodes.opcode_table[opcode](mem, address)
    return instruction

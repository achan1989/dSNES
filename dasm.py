import opcodes
import dasm_objects


def disassemble_instruction(mem, address):
    opcode = mem[address]
    instruction = opcodes.opcode_table[opcode](mem, address)
    return instruction

def disassemble_program(program):
    find_and_label_entry_points(program)
    program.print_entry_points()

def find_and_label_entry_points(program):
    vectors = (
        ("NMI", 0xFFFA),
        ("RESET", 0xFFFC),
        ("IRQ", 0xFFFE))
    for label, v in vectors:
        address = read_dword(program.mem, v)
        program.entry_points.add(address)
        program.labels[address] = label

def read_dword(mem, address):
    """ Read a 2-byte dword, little-endian, at the given address. """
    lsb = mem[address]
    msb = mem[address+1]
    return (msb << 8) | lsb

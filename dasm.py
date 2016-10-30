import opcodes
import dasm_objects
from util import dw_to_uint, tc_to_int


def disassemble_instruction(mem, address):
    try:
        opcode = mem[address]
    except IndexError:
        import pdb; pdb.set_trace()
    instruction = opcodes.opcode_table[opcode](mem, address)
    return instruction

def disassemble_program(program):
    find_and_label_entry_points(program)
    program.print_entry_points()

    for ep in program.entry_points:
        disassemble_chunk(program, ep)

def disassemble_chunk(program, start_address):
    chunk = dasm_objects.Chunk(start_address)

    address = start_address
    while True:
        instruction = disassemble_instruction(program.mem, address)
        if instruction.category == opcodes.category.Illegal:
            chunk.print_instructions()
            import pdb; pdb.set_trace()
            raise Exception("Tried to disassemble illegal instruction {}".format(instruction))
        chunk.add_instruction(instruction)
        address += instruction.size

        if instruction.is_conditional_jump or instruction.is_function_call:
            chunk.add_and_label_exit_point(
                instruction.address,
                get_jump_target(instruction),
                program.labels)
        if instruction.is_unconditional_jump or instruction.is_function_return:
            chunk.add_and_label_exit_point(
                instruction.address,
                get_jump_target(instruction),
                program.labels)
            break

    program.chunks.add(chunk)

def find_and_label_entry_points(program):
    vectors = (
        ("NMI", 0xFFFA),
        ("RESET", 0xFFFC),
        # ("IRQ", 0xFFFE) The IRQ vector is unused (and points to data not code).
        )
    for label, v in vectors:
        address = read_dword(program.mem, v)
        program.entry_points.add(address)
        program.labels.add(address, label)

def read_dword(mem, address):
    """ Read a 2-byte dword, little-endian, at the given address. """
    lsb = mem[address]
    msb = mem[address+1]
    return dw_to_uint((lsb, msb))

def get_jump_target(instruction):
    if instruction.is_conditional_jump:
        # All conditional jumps are relative.
        assert len(instruction.operands) == 1
        operand = instruction.operands[0]
        # They are relative to the end of the instruction, not the start.
        return instruction.address + 2 + tc_to_int(operand)

    if instruction.is_unconditional_jump or instruction.is_function_call:
        if instruction.category == opcodes.category.JmpAbsolute:
            return dw_to_uint(instruction.operands)
        if instruction.category == opcodes.category.JmpAbsoluteIndirect:
            assert len(instruction.operands) == 2
            return dasm_objects.UNKNOWN_JUMP_TARGET

    if instruction.is_function_return:
        assert len(instruction.operands) == 0
        return dasm_objects.RETURN_TO_CALLER

    raise Exception("Instruction {} is not a jump".format(instruction))

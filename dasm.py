import collections

import opcodes
import dasm_objects
from util import dw_to_uint, tc_to_int
import memory
import symbolset


def disassemble_instruction(mem, address):
    try:
        opcode = mem[address]
    except IndexError:
        import pdb; pdb.set_trace()
    instruction = opcodes.opcode_table[opcode](mem, address)
    return instruction

def disassemble_program(program):
    find_and_label_entry_points(program)
    # program.print_entry_points()

    queue = collections.deque(program.entry_points)
    chunk_count = 0

    while True:
        try:
            target = queue.popleft()
        except IndexError:
            break

        # Only disassemble chunks at locations that we haven't disassembled
        # already.
        existing_chunk = program.get_chunk_containing(target)
        if not existing_chunk:
            print("Disassembling chunk {} at 0x{:04X}".format(
                chunk_count, target))
            chunk = disassemble_chunk(program, target)
            for address, target in chunk.exit_points:
                if target not in dasm_objects.SPECIAL_TARGETS:
                    queue.append(target)
            chunk_count += 1

    print("\nDisassembling finished.")

def disassemble_chunk(program, start_address):
    chunk = dasm_objects.Chunk(start_address)

    address = start_address
    end_of_chunk = False
    while not end_of_chunk:
        is_exit_point = False
        ram_ref = None

        instruction = disassemble_instruction(program.mem, address)
        if instruction.category == opcodes.category.Illegal:
            print("\nError disassembling chunk.")
            chunk.print_instructions(program.symbols, program.config)
            import pdb; pdb.set_trace()
            raise Exception("Tried to disassemble illegal "
                "instruction {}".format(instruction))
        chunk.add_instruction(instruction)
        address += instruction.size

        if instruction.is_conditional_jump or instruction.is_function_call:
            is_exit_point = True
        elif instruction.is_unconditional_jump or instruction.is_function_return:
            is_exit_point = True
            end_of_chunk = True
        else:
            ram_ref = get_ram_reference(instruction)

        if is_exit_point:
            target = get_jump_target(instruction)
            chunk.add_and_label_exit_point(
                instruction.address,
                target,
                program.symbols)

            if target == dasm_objects.UNKNOWN_JUMP_TARGET:
                # We don't know where the jump will go (indirect jump) but we
                # should try to name the indirection variable.
                ram_ref = get_ram_reference(instruction)

        if ram_ref is not None:
            try:
                if ram_ref <= memory.MAX_ZERO_PAGE:
                    program.symbols.add_zp_variable(ram_ref)
                else:
                    program.symbols.add_generic_variable(ram_ref)
            except symbolset.TargetRelabelException:
                # If the variable already has a name that's ok.
                pass

            # TODO: program.symbols.record_variable_access(
            #         chunk, ram_ref, todo_access_kind)

        if instruction.address in program.config.forced_chunk_ends:
            print("Forced the end of this chunk disassembly after "
                "0x{:04X}".format(instruction.address))
            end_of_chunk = True

    chunk.clean_exit_points()
    program.chunks.append(chunk)
    return chunk

def find_and_label_entry_points(program):
    vectors = (
        ("NMI", 0xFFFA),
        ("RESET", 0xFFFC),
        # ("IRQ", 0xFFFE) The IRQ vector is unused (points to data not code).
        )
    for label, v in vectors:
        address = read_dword(program.mem, v)
        program.entry_points.add(address)
        try:
            program.symbols.add_label(address, label)
        except symbolset.TargetRelabelException:
            # If the variable already has a name that's ok.
            pass

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
        return instruction.address + instruction.size + tc_to_int(operand)

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

def get_ram_reference(instruction):
    """
    Try to get a reference to a location in RAM from an instruction's
    operand.  May return None.
    """
    address = None

    if instruction.category in (
            opcodes.category.Absolute,
            opcodes.category.AbsoluteX,
            opcodes.category.AbsoluteY,
            opcodes.category.JmpAbsoluteIndirect):
        address = dw_to_uint(instruction.operands)

    elif instruction.category in (
            opcodes.category.ZeroPage,
            opcodes.category.ZeroPageX,
            opcodes.category.ZeroPageY,
            opcodes.category.ZeroPageIndirectY,
            opcodes.category.ZeroPageXIndirect):
        address = instruction.operands[0]

    if address is not None and memory.RAM.contains(address):
        return address

    return None

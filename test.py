import sys

import loader
import extract
import memory
import dasm
import dasm_objects


def basic_test(address):
    prog = extract.extract("smb.nes")
    mem = memory.Memory()
    mem.map_prog_rom(prog)
    del prog

    for _ in range(0, 50):
        instruction = dasm.disassemble_instruction(mem, address)
        assert instruction.address == address
        address += instruction.size

        print("0x{addr:04X}: {asm}".format(
            addr=instruction.address,
            asm=instruction.assembly_string))


def disassemble_program(program):
    dasm.disassemble_program(program)
    return program


def test_print(prog):
    chunk = prog.chunks[0]

    # print("\nBasic print:")
    # chunk.print_instructions()

    print("\nPrint with symbols resolved:")
    chunk.print_instructions(prog.symbols, prog.config)

    print("\nExit points:")
    for address, target in chunk.exit_points:
        if type(target) is str:
            print("0x{:04X} --> {}".format(address, target))
        else:
            print("0x{:04X} --> 0x{:04X}".format(address, target))


def parse_args(args):
    address = None
    label = None

    if len(args) == 1:
        label = "RESET"
    else:
        label = args[1]
        try:
            address = int(args[1], base=0)
        except ValueError:
            pass
    return address, label


if __name__ == "__main__":
    address, label = parse_args(sys.argv)

    # basic_test(address)
    p = loader.load("smb.nes", "smb.config")
    disassemble_program(p)
    # test_print(p)

    # Find the chunk at the given address or label.
    # Try address first, as that's harder.
    c = p.get_chunk_starting(address)
    if not c:
        c = p.get_chunk_starting(label)

    if c:
        c.print_instructions(p.symbols, p.config)
    else:
        print("No chunk found at {} or {}".format(address, label))

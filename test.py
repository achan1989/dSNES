import sys

import extract
import memory
import dasm


def main(address):
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


if __name__ == "__main__":
    if len(sys.argv) == 1:
        address = 0x8000
    else:
        address = int(sys.argv[1], base=0)

    main(address)

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


def metatest():
    import opcodes
    handler_class = opcodes.opcode_table[0].handler_class
    handler = handler_class()

    print()
    print(handler)
    print("type is " + str(type(handler)))
    print(dir(handler))
    print(handler.operand_size)
    print(handler.operands_string)
    handler.operand_size = 5
    print(handler.operands_string)

    print()
    print(handler_class)
    print("type is " + str(type(handler_class)))
    print(dir(handler_class))
    #print(handler_class.size)

    #print()
    #print(handler_class.size is handler.size)
    #handler_class.size = "potato"
    #print(handler.size)


def optest():
    import opcodes
    for opdesc in opcodes.opcode_table:
        assert opdesc.size == opdesc.handler_class().size
    print("\noptest() pass")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        address = 0x8000
    else:
        address = int(sys.argv[1], base=0)

    main(address)
    metatest()
    optest()

import extract
import memory
import dasm_objects


def load(rom_path, config_path=None):
    prog_rom = extract.extract(rom_path)
    mem = memory.Memory()
    mem.map_prog_rom(prog_rom)
    del prog_rom

    program = dasm_objects.Program(mem)
    program.symbols.load(config_path)
    return program

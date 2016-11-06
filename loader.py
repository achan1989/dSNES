import configparser

import extract
import memory
import dasm_objects


def load(rom_path, config_path=None):
    prog_rom = extract.extract(rom_path)
    mem = memory.Memory()
    mem.map_prog_rom(prog_rom)
    del prog_rom

    program = dasm_objects.Program(mem)
    load_config(config_path, program.symbols)
    return program

def load_config(config_path, symbols):
    if not config_path:
        return
    print("Loading config from {}".format(config_path))

    config = configparser.ConfigParser()
    config.read(config_path)

    if "LABELS" in config:
        count = 0
        for address, label in config.items("LABELS"):
            address = int(address, base=0)
            symbols.add_label(address, label)
            count += 1
        print("Loaded {} labels.".format(count))

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
    load_config(config_path, program.symbols, program.config)
    return program

def load_config(config_path, symbols, config):
    if not config_path:
        return
    print("Loading config from {}".format(config_path))

    parsed = configparser.ConfigParser(allow_no_value=True)
    parsed.read(config_path)

    if "LABELS" in parsed:
        count = 0
        for address, label in parsed.items("LABELS"):
            address = int(address, base=0)
            symbols.add_label(address, label)
            count += 1
        print("Loaded {} labels.".format(count))

    if "FORCE END CHUNK" in parsed:
        count = 0
        for address, _ in parsed.items("FORCE END CHUNK"):
            address = int(address, base=0)
            config.forced_chunk_ends.append(address)
            count += 1
        print("Loaded {} forced chunk ends.".format(count))

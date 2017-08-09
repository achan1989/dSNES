# Copyright 2017 Adrian Chan
# Licensed under GPLv3

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

    count = 0
    if "LABELS" in parsed:
        for address, label in parsed.items("LABELS"):
            address = int(address, base=0)
            symbols.add_label(address, label)
            count += 1
    print("Loaded {} labels.".format(count))

    count = 0
    if "FORCE END CHUNK" in parsed:
        for address, comment in parsed.items("FORCE END CHUNK"):
            address = int(address, base=0)
            config.forced_chunk_ends.append(address)
            config.add_post_comment(address, comment)
            count += 1
    print("Loaded {} forced chunk ends.".format(count))

    count = 0
    if "PRE COMMENTS" in parsed:
        for address, comment in parsed.items("PRE COMMENTS"):
            address = int(address, base=0)
            config.add_pre_comment(address, comment)
            count += 1

    if "INLINE COMMENTS" in parsed:
        for address, comment in parsed.items("INLINE COMMENTS"):
            address = int(address, base=0)
            config.add_inline_comment(address, comment)
            count += 1

    if "POST COMMENTS" in parsed:
        for address, comment in parsed.items("POST COMMENTS"):
            address = int(address, base=0)
            config.add_post_comment(address, comment)
            count += 1
    print("Loaded {} comments.".format(count))

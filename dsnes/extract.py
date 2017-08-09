"""
Extract the SMB program rom from the .nes file.
"""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

def extract(filename):
    nesfile = open(filename, 'rb')

    header = get_header(nesfile)
    assert is_nrom_mapper(header)
    program_rom = get_program_rom(header, nesfile)
    return program_rom


def get_header(nesfile):
    header = nesfile.read(16)
    check_header(header)
    return header


def check_header(header):
    assert header[0:4] == b"NES\x1A"


def is_nrom_mapper(header):
    nibble_mask = 0b11110000
    low = (header[6] & nibble_mask) >> 4
    high = header[7] & nibble_mask
    return (high | low) == 0


def get_program_rom(header, nesfile):
    prg_blocks = header[4]
    nbytes = prg_blocks * 16384
    return nesfile.read(nbytes)


if __name__ == "__main__":
    extract("smb.nes")

"""
Represents all of NES memory for SMB.
"""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import collections
import types


MAX_ZERO_PAGE = 0xFF


class Section():
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

    @property
    def size(self):
        return 1 + self.end - self.start

    def contains(self, address):
        return self.start <= address <= self.end

class Mirror():
    def __init__(self, section, start, end):
        self.section = section
        self.start = start
        self.end = end

    def contains(self, address):
        return self.start <= address <= self.end

    def normalise(self, address):
        assert self.contains(address)
        offset = address % self.section.size
        return self.section.start + offset


# The following 4 are always correct.
RAM = Section("RAM", 0x00, 0x07FF)
PPU = Section("PPU", 0x2000, 0x2007)
APU_IO = Section("APU/IO", 0x4000, 0x4017)
Test = Section("test", 0x4018, 0x401F)
# Program ROM mapping is a function of the cartridge, so changes depending on
# the game.
# TODO: make a cartridge/mapper object to handle this properly.
PROM = Section("program ROM", 0x8000, 0xFFFF)

sections = [RAM, PPU, APU_IO, Test, PROM]
mirrors = [
    Mirror(RAM, 0x0800, 0x1FFF),
    Mirror(PPU, 0x2008, 0x3FFF)
]

def normalise(address):
    for section in sections:
        if section.contains(address):
            return address

    for mirror in mirrors:
        if mirror.contains(address):
            norm_address = mirror.normalise(address)
            if norm_address != address:
                print("WARNING: address {:#04X} is a mirror of {:#04X}.".format(
                    address, norm_address))
            return norm_address

    # Not in a section we know about.  Meh.
    return address

class Memory:
    Max_index = 0xFFFF
    Size = Max_index + 1

    def __init__(self):
        self._int_ram = bytearray(RAM.size)
        self._prog_rom = bytearray(PROM.size)

    def map_prog_rom(self, prog_rom):
        assert len(prog_rom) == len(self._prog_rom)
        self._prog_rom[:] = prog_rom

    @property
    def internal_ram_view(self):
        return memoryview(self._int_ram)

    @property
    def program_rom_view(self):
        return memoryview(self._prog_rom)

    def __len__(self):
        return Memory.size

    def __getitem__(self, key):
        """ Get a register description or value in memory for a given
            address. Does not support slicing. """
        if type(key) == slice:
            raise TypeError("Cannot use slices")

        if key < 0 or key > Memory.Max_index:
            raise IndexError()

        address = normalise(key)

        if address <= RAM.end:
            return self._int_ram[address]

        if address <= PPU.end:
            return "PPU reg at 0x{0:X}".format(address)

        if address <= APU_IO.end:
            return "APU/IO reg at 0x{0:X}".format(address)

        if address <= Test.end:
            return "Test reg at 0x{0:X}".format(address)

        # Up to this point all addresses have been mapped to something.
        # This is not true within the cartridge space.

        if PROM.contains(address):
            return self._prog_rom[address - PROM.start]

        # Unmapped memory is just None for the moment.
        return None


access = types.SimpleNamespace(
    read="read",
    write="write",
    readwrite="readwrite",
    none="none"
    )

"""
Represents all of NES memory for SMB.
"""

class Memory:
    int_ram_start = 0x00
    int_ram_end = 0x07FF
    int_ram_size = 0x0800
    int_ram_mirror_end = 0x01FFF

    ppu_start = 0x2000
    ppu_end = 0x2007
    ppu_size = 0x08
    ppu_mirror_end = 0x3FFF

    apu_io_start = 0x4000
    apu_io_end = 0x4017
    apu_io_size = 0x18

    test_start = 0x4018
    test_end = 0x401F
    test_size = 0x08

    prog_start = 0x8000
    prog_end =0xFFFF
    prog_size = 0x8000

    max_index = 0xFFFF
    size = max_index + 1


    def __init__(self):
        self._int_ram = bytearray(0x0800)
        self._prog_rom = bytearray(0x8000)

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

        if key < 0 or key > Memory.max_index:
            raise IndexError()

        if key <= Memory.int_ram_mirror_end:
            i = key % Memory.int_ram_size
            return self._int_ram[i]

        if key <= Memory.ppu_mirror_end:
            i = key % Memory.ppu_size
            return "PPU reg at 0x{0:X}".format(Memory.ppu_start + i)

        if key <= Memory.apu_io_end:
            return "APU/IO reg at 0x{0:X}".format(key)

        # Up to this point all addresses have been mapped to something.
        # This is not true within the cartridge space.

        if key >= Memory.prog_start and key <= Memory.prog_end:
            return self._prog_rom[key - Memory.prog_start]

        # Unmapped memory is just None for the moment.
        return None

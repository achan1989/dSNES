"""Bus concept and code adapted from the higan emulator.
See https://gitlab.com/higan/higan/tree/master

Original code copyright byuu, and licensed under GPLv3 (see
https://byuu.org/emulation/higan/licensing).
"""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes

class Bus:
    """Provides the CPU with access to memory devices.

    Responsible for mapping a CPU address bus value to a memory address in
    the correct memory device.
    """

    def __init__(self):
        # Maps CPU address bus values to reader/writer ids.
        self.lookup = {}
        # Maps CPU address bus values to device memory addresses.
        self.target = {}
        self.map_count = 0
        # Maps ids to read and write functions.
        self.reader = {}
        self.writer = {}

    def map(self, bank_lo, bank_hi, addr_lo, addr_hi, size=0, base=0,
            mask=0, read_fn=None, write_fn=None):
        assert read_fn is not None
        assert write_fn is not None
        idx = self.map_count + 1
        # Not strictly necessary, but I want to know if I accidentally make a
        # stupid number of mappings.
        assert idx < 256, "Too many mappings"

        for bank in range(bank_lo, bank_hi+1):
            for addr in range(addr_lo, addr_hi+1):
                target_addr = (bank << 16 | addr)
                assert not self.lookup.get(target_addr, None), (
                    "Target address {} has already been mapped".format(
                        target_addr))

                offset = self.reduce(target_addr, mask)
                if size:
                    offset = base + self.mirror(offset, size - base)
                self.lookup[target_addr] = idx
                self.target[target_addr] = offset

        self.reader[idx] = read_fn
        self.writer[idx] = write_fn
        self.map_count = idx

    def read(self, addr):
        try:
            map_id = self.lookup[addr]
            reader = self.reader[map_id]
            dev_addr = self.target[addr]
        except LookupError as ex:
            raise dsnes.UnmappedMemoryAccess(addr) from ex
        return reader(dev_addr)

    def write(self, addr, data):
        try:
            map_id = self.lookup[addr]
            writer = self.writer[map_id]
            dev_addr = self.target[addr]
        except LookupError as ex:
            raise dsnes.UnmappedMemoryAccess(addr) from ex
        writer(dev_addr, data)

    @staticmethod
    def reduce(addr, mask):
        """Get the effective memory device address.

        Memory devices don't always connect all address lines to the CPU
        address bus; this is denoted by the relevant bit being set in the mask.
        This function calculates the effective address seen by the memory
        device based on the given CPU address and the device mask.
        """
        while mask:
            bits = (mask & -mask) - 1
            addr = ((addr >> 1) & ~bits) | (addr & bits)
            mask = (mask & (mask - 1)) >> 1
        return addr

    @staticmethod
    def mirror(addr, size):
        """Presumably accounting for the way that some memory devices are
        mirrored in the the memory map.  I don't really know how this works...
        """
        assert size > 0
        base = 0
        mask = 1 << 23
        while addr >= size:
            while not (addr & mask):
                mask = mask >> 1

            addr -= mask
            if size > mask:
                size -= mask
                base += mask
            mask = mask >> 1

        return base + addr

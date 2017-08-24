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

        reduce_fn = self.make_reduce_fn(mask)

        for bank in range(bank_lo, bank_hi+1):
            pbr = bank << 16
            for target_addr in range((pbr | addr_lo), (pbr | addr_hi)+1):
                assert target_addr not in self.lookup, (
                    "Target address {} has already been mapped".format(
                        target_addr))

                offset = reduce_fn(target_addr, mask)
                if size:
                    offset = base + self.mirror(offset, size - base)
                self.lookup[target_addr] = idx
                self.target[target_addr] = offset

        self.reader[idx] = read_fn
        self.writer[idx] = write_fn
        self.map_count = idx

    def read(self, addr):
        addr = int(addr)
        try:
            map_id = self.lookup[addr]
            reader = self.reader[map_id]
            dev_addr = self.target[addr]
        except LookupError as ex:
            raise dsnes.UnmappedMemoryAccess(addr) from ex
        return reader(dev_addr)

    def write(self, addr, data):
        addr = int(addr)
        try:
            map_id = self.lookup[addr]
            writer = self.writer[map_id]
            dev_addr = self.target[addr]
        except LookupError as ex:
            raise dsnes.UnmappedMemoryAccess(addr) from ex
        writer(dev_addr, data)

    @staticmethod
    def make_reduce_fn(mask):
        """Make a function that computes the effective memory device address.

        Memory devices don't always connect their address lines to the CPU
        address bus one-to-one, but can skip CPU address lines; this is denoted
        by the relevant bit being set in the mask.
        Return a function that calculates the effective address seen by the
        memory device based on a given CPU address and device mask.
        """
        if mask == 0:
            def reduce_fn(addr, mask):
                return addr

        elif mask == 0x8000:
            def reduce_fn(addr, mask):
                return (addr & 0x7FFF) + ((addr >> 1) & 0xFFFF8000)

        else:
            def reduce_fn(addr, mask):
                while mask:
                    bits = (mask & -mask) - 1
                    print("bits: {:x}".format(bits))
                    addr = ((addr >> 1) & ~bits) | (addr & bits)
                    mask = (mask & (mask - 1)) >> 1
                return addr

        return reduce_fn

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

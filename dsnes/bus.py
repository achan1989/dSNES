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
        # Maps CPU address bus values to access ids.
        self.lookup = {}
        # Maps CPU address bus values to device memory addresses.
        self.target = {}
        self.map_count = 0
        # Maps ids to access functions.
        self.reader = {}
        self.labeller = {}

    def map(self, bank_lo, bank_hi, addr_lo, addr_hi, size=0, base=0,
            mask=0, read_fn=None, label_fn=None):
        if read_fn is None:
            read_fn = default_read_fn
        if label_fn is None:
            label_fn = default_label_fn
        idx = self.map_count + 1
        # Not strictly necessary, but I want to know if I accidentally make a
        # stupid number of mappings.
        assert idx < 256, "Too many mappings"

        reduce_fn = make_reduce_fn(mask)
        if size:
            mirror_fn = make_mirror_fn(size - base)

        for bank in range(bank_lo, bank_hi+1):
            pbr = bank << 16
            for target_addr in range((pbr | addr_lo), (pbr | addr_hi)+1):
                assert target_addr not in self.lookup, (
                    "Target address {} has already been mapped".format(
                        target_addr))

                offset = reduce_fn(target_addr, mask)
                if size:
                    offset = base + mirror_fn(offset)
                self.lookup[target_addr] = idx
                self.target[target_addr] = offset

        self.reader[idx] = read_fn
        self.labeller[idx] = label_fn
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

    def get_label(self, addr):
        addr = int(addr)
        try:
            map_id = self.lookup[addr]
            labeller = self.labeller[map_id]
            dev_addr = self.target[addr]
        except LookupError as ex:
            raise dsnes.UnmappedMemoryAccess(addr) from ex
        return labeller(dev_addr)


def make_reduce_fn(mask):
    """Make a function that computes the effective memory device address.

    Memory devices don't always connect their address lines to the CPU
    address bus one-to-one, but can skip CPU address lines; this is denoted
    by the relevant bit being set in the mask.
    Return a function that calculates the effective address seen by the
    memory device based on a given CPU address and device mask.
    """
    # Have validated that these optimized versions are equivalent to the
    # slower generic version.
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
                addr = ((addr >> 1) & ~bits) | (addr & bits)
                mask = (mask & (mask - 1)) >> 1
            return addr

    return reduce_fn

def make_mirror_fn(size):
    """Make a function that resolves a device address (handles mirroring).

    If the given device address is larger than the actual size of the device
    then the address "wraps" until it falls into a valid range?
    I think this is just modulo for some cases, but I'm not sure in exactly
    what circumstances it becomes more complicated.
    """
    assert size > 0

    # Have validated that these optimized versions are equivalent to the
    # slower generic version.
    simple_modulo = (0x2000, 0x8000, 0x20000, 0x100000)
    if size in simple_modulo:
        def mirror_fn(addr):
            return addr % size

    else:
        size_capture = size
        def mirror_fn(addr):
            size = size_capture
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

    return mirror_fn

def default_read_fn(addr):
    raise TypeError("No read function for memory at 0x{:x}".format(addr))

def default_label_fn(addr):
    return None

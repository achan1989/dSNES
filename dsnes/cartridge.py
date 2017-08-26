"""Represents the hardware within a cartridge."""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import os

import dsnes


class Cartridge:
    def __init__(self):
        self.rom = None
        self.ram = None
        self.cpu = None

    def load(self, project):
        assert os.path.isdir(project.path), "{} is not a directory".format(path)
        self._load_apu(project)
        self._load_cpu(project)
        self._load_dma(project)
        self._load_ppu(project)
        self._load_wram(project)
        self.rom = self._load_rom(project)
        self.ram = self._load_ram(project)

    @staticmethod
    def _load_rom(project):
        config = project.config["rom"]
        if config:
            filename = config["filename"]
            try:
                size = int(config["size"], 0)
            except LookupError:
                size = 0
            path = os.path.join(project.path, filename)
            maps = config["map"]
            assert len(maps) > 0, "Must map ROM somewhere"

            rom = dsnes.Rom()
            rom.allocate(open(path, 'rb'), size=size)
            for m in maps:
                bank_lo = int(m["bank_low"], 0)
                bank_hi = int(m["bank_high"], 0)
                addr_lo = int(m["address_low"], 0)
                addr_hi = int(m["address_high"], 0)
                try:
                    size = int(m["size"], 0)
                except LookupError:
                    size = 0
                try:
                    base = int(m["base"], 0)
                except LookupError:
                    base = 0
                try:
                    mask = int(m["mask"], 0)
                except LookupError:
                    mask = 0
                project.bus.map(
                    bank_lo, bank_hi, addr_lo, addr_hi,
                    size, base, mask, read_fn=rom.read)

            return rom

    @staticmethod
    def _load_ram(project):
        # TODO
        return None

    @staticmethod
    def _load_apu(project):
        for bank_lo, bank_hi in dsnes.apureg.map_to_banks:
            for addr_lo, addr_hi in dsnes.apureg.map_to_addresses:
                project.bus.map(
                    bank_lo=bank_lo, bank_hi=bank_hi,
                    addr_lo=addr_lo, addr_hi=addr_hi,
                    label_fn=dsnes.apureg.get_label)

    @staticmethod
    def _load_cpu(project):
        for bank_lo, bank_hi in dsnes.cpureg.map_to_banks:
            for addr_lo, addr_hi in dsnes.cpureg.map_to_addresses:
                project.bus.map(
                    bank_lo=bank_lo, bank_hi=bank_hi,
                    addr_lo=addr_lo, addr_hi=addr_hi,
                    label_fn=dsnes.cpureg.get_label)

    @staticmethod
    def _load_dma(project):
        for bank_lo, bank_hi in dsnes.dmareg.map_to_banks:
            for addr_lo, addr_hi in dsnes.dmareg.map_to_addresses:
                project.bus.map(
                    bank_lo=bank_lo, bank_hi=bank_hi,
                    addr_lo=addr_lo, addr_hi=addr_hi,
                    label_fn=dsnes.dmareg.get_label)

    @staticmethod
    def _load_ppu(project):
        for bank_lo, bank_hi in dsnes.ppureg.map_to_banks:
            for addr_lo, addr_hi in dsnes.ppureg.map_to_addresses:
                project.bus.map(
                    bank_lo=bank_lo, bank_hi=bank_hi,
                    addr_lo=addr_lo, addr_hi=addr_hi,
                    label_fn=dsnes.ppureg.get_label)

    @staticmethod
    def _load_wram(project):
        wram_size = 0x20000
        small_map = 0x2000
        large_map = wram_size
        def wram_label(addr):
            if addr >= 0 and addr <= wram_size:
                return "wram_{:05x}".format(addr)
            else:
                return "INVALID_WRAM"
        mappings = (
            (0x00, 0x3f, 0, 0x1fff, small_map),
            (0x80, 0xbf, 0, 0x1fff, small_map),
            (0x7e, 0x7f, 0, 0xffff, large_map)
        )
        for bank_lo, bank_hi, addr_lo, addr_hi, size in mappings:
            project.bus.map(
                bank_lo=bank_lo, bank_hi=bank_hi,
                addr_lo=addr_lo, addr_hi=addr_hi,
                size=size,
                label_fn=wram_label)

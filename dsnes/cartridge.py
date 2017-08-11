"""Represents the hardware within a cartridge."""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import os

from dsnes import memory


class Cartridge:
    def __init__(self):
        self.rom = None
        self.ram = None

    def load(self, project):
        assert os.path.isdir(project.path), "{} is not a directory".format(path)
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

            rom = memory.Memory()
            rom.allocate(open(path, 'rb'), size=size)
            # TODO mapping etc.
            return rom

    @staticmethod
    def _load_ram(project):
        # TODO
        return None

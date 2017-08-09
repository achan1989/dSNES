"""Represents the hardware within a cartridge."""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import os


class Cartridge:
    def __init__(self):
        self.rom = None
        self.ram = None

    def load(project):
        assert os.path.isdir(project.path), "{} is not a directory".format(path)
        self._load_rom(project)
        self._load_ram(project)

    def _load_rom(project):
        config = project.get("rom", {})
        if config:
            filename = config["filename"]
            path = os.path.join(project.path, filename)
            maps = config["map"]
            assert len(maps) > 0, "Must map ROM somewhere"

            # TODO

    def _load_ram(project):
        # TODO
        pass

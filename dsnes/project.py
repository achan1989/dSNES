"""Represents a disassembly project."""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import os

from dsnes import contoml_fix as contoml
from dsnes import bus, cartridge


def load(path):
    project = Project()
    project.load(path)
    return project

class Project:
    def __init__(self):
        self.path = None
        self.config = None
        self.bus = None

    def load(self, path):
        assert os.path.isdir(path), "{} is not a directory".format(path)
        self.path = path
        self.config = self.load_config(os.path.join(path, "config.toml"))
        self.bus = bus.Bus()
        self.cartridge = cartridge.Cartridge()
        self.cartridge.load(self)

    @staticmethod
    def load_config(path):
        assert os.path.isfile(path), "{} is not a file".format(path)
        config = contoml.load(path)
        return config

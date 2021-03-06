"""Represents a disassembly project."""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import os

import toml

import dsnes


def load(path):
    project = Project()
    project.load(path)
    return project

class Project:
    def __init__(self):
        self.path = None
        self.config = None
        self.database = None
        self.bus = None

    def load(self, path):
        assert os.path.isdir(path), "{} is not a directory".format(path)
        self.path = path
        self.config = self.load_config(os.path.join(path, "config.toml"))
        self.database = self.load_database(os.path.join(path, "database.toml"))
        self.bus = dsnes.Bus()
        self.cartridge = dsnes.Cartridge()
        self.cartridge.load(self)

    def save(self):
        assert self.database
        self.database.save()

    @staticmethod
    def load_config(path):
        assert os.path.isfile(path), "{} is not a file".format(path)
        config = toml.load(path)
        return config

    @staticmethod
    def load_database(path):
        assert os.path.isfile(path), "{} is not a file".format(path)
        return dsnes.database.load(path)

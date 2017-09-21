# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes


class Session:
    def __init__(self):
        self.project = None
        self.to_load = None

    def load_project(self, path=None):
        if self.project is not None:
            raise RuntimeError("Project already loaded")
        if not path and not self.to_load:
            raise RuntimeError("Must set to_load or provide a path")
        self.project = dsnes.project.load(path or self.to_load)
        self.to_load = None

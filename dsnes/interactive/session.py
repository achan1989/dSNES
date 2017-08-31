# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes


class Session:
    def __init__(self):
        self.project = None

    def load_project(self, path):
        if self.project is not None:
            raise RuntimeError("Project already loaded")
        self.project = dsnes.project.load(path)

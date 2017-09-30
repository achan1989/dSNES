# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import collections

import dsnes


class NoOperation(Exception):
    pass


class Session:
    def __init__(self):
        self.project = None
        self.analysis_stack = collections.deque()
        self.current_analysis = None
        self.line_number = None

    @property
    def line_number(self):
        return self._line_number

    @line_number.setter
    def line_number(self, value):
        if value is None:
            self._line_number = None
        elif self.current_analysis:
            # Raises IndexError if not a valid line.
            self.current_analysis.get_disassembly_line(value)
            self._line_number = value
        else:
            raise RuntimeError("No analysis is open")

    @property
    def analysis_line_range(self):
        """Get the range of line numbers in the disassembly.

        Returns (min, max), or None if there is no disassembly.
        """
        if not self.current_analysis:
            return None
        disassembly = self.current_analysis.disassembly
        num_items = len(disassembly)
        if num_items == 0:
            return None
        else:
            return (0, num_items-1)

    @property
    def analysis_lines(self):
        if not self.current_analysis:
            raise RuntimeError("No analysis is open")
        return self.current_analysis.get_disassembly_lines()

    def load_project(self, path):
        if self.project is not None:
            raise RuntimeError("Project already loaded")
        if not path:
            raise RuntimeError("Must provide a path")
        self.project = dsnes.project.load(path)
        self.analysis_stack.clear()

    def new_analysis(self, address):
        analyser = dsnes.Analyser(self.project)
        analyser.analyse_function(address)
        self.analysis_stack.clear()
        self.current_analysis = analyser
        self.line_number = 0

    def get_calls_from_line(self, line_number=None):
        analyser = self.current_analysis
        if not analyser:
            raise RuntimeError("No analysis is open")
        return analyser.get_calls_from(line_number or self.line_number)

    def follow_call(self, target, state):
        analyser = self.current_analysis
        if not analyser:
            raise RuntimeError("No analysis is open")
        valid = False
        for t, s in analyser.get_calls_from(self.line_number):
            if target == t and s == s:
                valid = True
                break
        if not valid:
            raise NoOperation("Not a valid call")

        follow_analyser = dsnes.Analyser(self.project)
        follow_analyser.analyse_function(target, state)
        self.line_number = 0

        self.analysis_stack.append((analyser, self.line_number))
        self.current_analysis = follow_analyser

    def jump_back(self):
        try:
            analyser, line_number = self.analysis_stack.pop()
        except LookupError:
            raise NoOperation("Nowhere to jump back to")
        else:
            self.current_analysis = analyser
            self.line_number = line_number

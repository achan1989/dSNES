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
    def has_unsaved_changes(self):
        return self.project is not None and self.project.database.is_dirty

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

    def save_project(self):
        if self.project is None:
            raise RuntimeError("No project is loaded")
        self.project.save()

    def new_analysis(self, address):
        analyser = dsnes.Analyser(self.project)
        analyser.analyse_function(address)
        self.analysis_stack.clear()
        self.current_analysis = analyser
        self.line_number = 0

    def refresh_analysis(self):
        address = self.current_analysis.start_address
        assert address is not None
        state = self.current_analysis.start_state

        new_analysis = dsnes.Analyser(self.project)
        new_analysis.analyse_function(address, state)
        self.current_analysis = new_analysis

        max_line = len(new_analysis.disassembly) - 1
        if self.line_number > max_line:
            self.line_number = max_line

    def get_calls_from_line(self, line_number=None):
        analyser = self.current_analysis
        if not analyser:
            raise RuntimeError("No analysis is open")
        return analyser.get_calls_from(line_number or self.line_number)

    def follow_call(self, target, state):
        current_analyser = self.current_analysis
        current_line = self.line_number
        if not current_analyser:
            raise RuntimeError("No analysis is open")
        valid = False
        for t, s in current_analyser.get_calls_from(self.line_number):
            if target == t and s == s:
                valid = True
                break
        if not valid:
            raise NoOperation("Not a valid call")

        follow_analyser = dsnes.Analyser(self.project)
        follow_analyser.analyse_function(target, state)
        self.line_number = 0

        self.analysis_stack.append((current_analyser, current_line))
        self.current_analysis = follow_analyser

    def can_jump_back(self):
        return len(self.analysis_stack) > 0

    def jump_back(self):
        try:
            analyser, line_number = self.analysis_stack.pop()
        except LookupError:
            raise NoOperation("Nowhere to jump back to")
        else:
            self.current_analysis = analyser
            self.line_number = line_number

    def can_create_new_label(self, text):
        """Check if a given label can be created."""
        if not text:
            return False, "Label cannot be empty"

        fail_msg = None
        valid = text not in self.project.database.get_all_labels()
        if not valid:
            fail_msg = "That label is already used somewhere else"
        return valid, fail_msg

    def apply_new_label(self, addr, text):
        """Apply a label to an address."""
        if addr < 0 or addr > 0xFFFFFF:
            raise ValueError("Address 0x{:06x} is out of range".format(addr))
        self.project.database.add_label(addr, text)

    def remove_label(self, addr, text):
        """Remove the label from an address."""
        if addr < 0 or addr > 0xFFFFFF:
            raise ValueError("Address 0x{:06x} is out of range".format(addr))
        self.project.database.remove_label(addr, text)

    def is_valid_state(self, text):
        """Check if something is a valid state string."""
        try:
            dsnes.State.parse(text)
            valid = True
            fail_msg = None
        except Exception as ex:
            valid = False
            fail_msg = str(ex)
        return valid, fail_msg

    def set_state(self, addr, text):
        """Set the state at an address."""
        if addr < 0 or addr > 0xFFFFFF:
            raise ValueError("Address 0x{:06x} is out of range".format(addr))
        state = dsnes.State.parse(text)
        self.project.database.set_state(addr, state)

    def remove_state(self, addr):
        """Remove the state from an address."""
        if addr < 0 or addr > 0xFFFFFF:
            raise ValueError("Address 0x{:06x} is out of range".format(addr))
        self.project.database.remove_state(addr)

    def is_valid_state_delta(self, text):
        """Check is something is a valid state delta string."""
        try:
            dsnes.StateDelta.parse(text)
            valid = True
            fail_msg = None
        except Exception as ex:
            valid = False
            fail_msg = str(ex)
        return valid, fail_msg

    def set_state_delta(self, addr, text):
        """Set the state delta at an address."""
        if addr < 0 or addr > 0xFFFFFF:
            raise ValueError("Address 0x{:06x} is out of range".format(addr))
        delta = dsnes.StateDelta.parse(text)
        self.project.database.set_state_delta(addr, delta)

    def remove_state_delta(self, addr):
        """Remove the state delta from an address."""
        if addr < 0 or addr > 0xFFFFFF:
            raise ValueError("Address 0x{:06x} is out of range".format(addr))
        self.project.database.remove_state_delta(addr)

    def get_hardware_label(self, addr):
        """Get a hardware label for the given address.

        Horrible hack that duplicates functionality in
        analyser.get_labels_for().
        May return None.
        """
        try:
            hw_label = self.project.bus.get_label(addr)
        except dsnes.UnmappedMemoryAccess:
            hw_label = "UNMAPPED_{:06x}".format(addr)
        return hw_label

    def get_address_of_interrupt_handler(self, emulation, kind):
        emulation_vectors = {
            "IRQ": 0xfffe,
            "Reset": 0xfffc,
            "NMI": 0xfffa,
            "Abort": 0xfff8,
            "COP": 0xfff4
        }
        native_vectors = {
            "IRQ": 0xffee,
            "NMI": 0xffea,
            "Abort": 0xffe8,
            "BRK": 0xffe6,
            "COP": 0xffe4
        }

        if emulation:
            vector = emulation_vectors[kind]
        else:
            vector = native_vectors[kind]
        lo = self.project.bus.read(vector)
        hi = self.project.bus.read(vector+1)
        handler = (hi << 8) + lo
        return handler

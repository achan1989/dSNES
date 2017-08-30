# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes
from dsnes import contoml_fix as contoml


def load(path):
    db = Database()
    db.load(path)
    return db

def encode_address_key(addr):
    assert addr > 0
    assert addr <= 0xFFFFFF
    pbr = (addr & 0xFF0000) >> 16
    pc = addr & 0x00FFFF
    return "{:02x}:{:04x}".format(pbr, pc)

def parse_address_key(key):
    pbr, pc = key.split(":", maxsplit=1)
    pbr = int(pbr, base=16)
    pc = int(pc, base=16)
    assert pbr >= 0
    assert pbr <= 0xFF
    assert pc >= 0
    assert pc <= 0xFFFF
    return (pbr << 16) + pc


class Database:
    def __init__(self):
        self.path = None
        self.data = contoml.TOMLFile([])
        self.state_cache = {}
        self.state_delta_cache = {}

    def get_state(self, addr):
        state = self.state_cache.get(addr, None)
        if state is not None:
            return state.clone()
        else:
            return None

    def set_state(self, addr, state):
        key = encode_address_key(addr)
        s = state.encode()
        if s is None and addr in self.state_cache:
            # State is set to all unknown, so delete the entry.
            del self.state_cache[addr]
            del self.data["states"][key]
        else:
            self.state_cache[addr] = state.clone()
            self.data["states"][key] = s

    def get_state_delta(self, addr):
        delta = self.state_delta_cache.get(addr, None)
        return delta

    def set_state_delta(self, addr, delta):
        key = encode_address_key(addr)
        s = delta.encode()
        self.state_delta_cache[addr] = delta
        self.data["state_deltas"][key] = s

    def get_label(self, addr):
        """Get the first label for a given address."""
        key = encode_address_key(addr)
        labels = self.data["labels"].get(key, [])
        if labels:
            return labels[0]
        else:
            return None

    def get_labels(self, addr):
        """Get all labels for a given address."""
        key = encode_address_key(addr)
        labels = self.data["labels"].get(key, [])
        return labels

    def get_pre_comment(self, addr):
        """Get the pre-instruction comment for an address."""
        key = encode_address_key(addr)
        return self.data["pre_comments"].get(key, None)

    def get_inline_comment(self, addr):
        """Get the inline comment for an address."""
        key = encode_address_key(addr)
        return self.data["inline_comments"].get(key, None)

    def load(self, path):
        self.path = path
        self.data = contoml.load(path)

        self.state_cache = state_cache = {}
        for key, value in self.data["states"].items():
            addr = parse_address_key(key)
            state = dsnes.State.parse(value)
            assert state is not None
            if addr in state_cache:
                raise ValueError(
                    "State for {} has already been declared".format(key))
            state_cache[addr] = state

        self.state_delta_cache = delta_cache = {}
        for key, value in self.data["state_deltas"].items():
            addr = parse_address_key(key)
            delta = dsnes.StateDelta.parse(value)
            assert delta is not None
            if addr in delta_cache:
                raise ValueError(
                    "State delta for {} has already been declared".format(key))
            delta_cache[addr] = delta

    def save(self):
        path = self.path
        contoml.dump(self.data, path)

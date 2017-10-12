# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import toml

import dsnes


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
        self.is_dirty = False
        self.data = {}
        self.state_cache = {}
        self.state_delta_cache = {}
        self.labels_of_address = {}
        self.address_of_label = {}

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
        self.is_dirty = True

    def get_state_delta(self, addr):
        delta = self.state_delta_cache.get(addr, None)
        return delta

    def set_state_delta(self, addr, delta):
        key = encode_address_key(addr)
        s = delta.encode()
        self.state_delta_cache[addr] = delta
        self.data["state_deltas"][key] = s
        self.is_dirty = True

    def get_label(self, addr):
        """Get the first label for a given address."""
        labels = self.labels_of_address.get(addr, [])
        if labels:
            return labels[0]
        else:
            return None

    def get_labels(self, addr):
        """Get all labels for a given address."""
        labels = self.labels_of_address.get(addr, [])
        return labels

    def get_all_labels(self):
        """Get all labels in use."""
        labels = [x for x in self.address_of_label.keys()]
        return labels

    def get_address_with_label(self, label):
        """Get the address that the label applies to."""
        return self.address_of_label.get(label, None)

    def add_label(self, addr, label):
        """Add a label to an address."""
        if label in self.get_all_labels():
            raise ValueError("Label {!r} is already in use".format(label))
        TODO

    def remove_label(self, addr, label):
        """Remove a label from an address."""
        stored_address = self.address_of_label.get(label, None)
        if stored_address is None:
            assert label not in self.address_of_label
            raise ValueError("Label {!r} does not exist".format(label))
        if stored_address != addr:
            raise ValueError(
                "Label {!r} is not applied to the address {}".format(
                    label, addr))
        key = encode_address_key(addr)

        label_list = self.data["labels"][key]
        label_list.remove(label)
        if len(label_list) == 0:
            del self.data["labels"][key]
        del self.address_of_label[label]
        label_list = self.labels_of_address[addr]
        label_list.remove(label)
        if len(label_list) == 0:
            del self.labels_of_address[addr]

        self.is_dirty = True

    def get_pre_comment(self, addr):
        """Get the pre-instruction comment for an address."""
        key = encode_address_key(addr)
        return self.data["pre_comments"].get(key, None)

    def set_pre_comment(self, addr, comment):
        assert comment is not None
        key = encode_address_key(addr)
        self.data["pre_comments"][key] = comment
        self.is_dirty = True

    def delete_pre_comment(self, addr):
        key = encode_address_key(addr)
        del self.data["pre_comments"][key]
        self.is_dirty = True

    def get_inline_comment(self, addr):
        """Get the inline comment for an address."""
        key = encode_address_key(addr)
        return self.data["inline_comments"].get(key, None)

    def set_inline_comment(self, addr, comment):
        assert comment is not None
        key = encode_address_key(addr)
        self.data["inline_comments"][key] = comment
        self.is_dirty = True

    def delete_inline_comment(self, addr):
        key = encode_address_key(addr)
        del self.data["inline_comments"][key]
        self.is_dirty = True

    def load(self, path):
        self.path = path
        self.data = toml.load(path)
        self.is_dirty = False

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

        self.labels_of_address = {}
        self.address_of_label = {}
        for key, labels in self.data["labels"].items():
            addr = parse_address_key(key)
            for label in labels:
                if label in self.address_of_label:
                    raise ValueError(
                        "Label {!r} has already been used for 0x{:06x}".format(
                            label, self.address_of_label[label]))
                self.address_of_label[label] = addr

                if addr not in self.labels_of_address:
                    self.labels_of_address[addr] = [label]
                else:
                    lst = self.labels_of_address[addr]
                    lst.append(label)

    def save(self):
        path = self.path
        with open(path, 'w') as outfile:
            toml.dump(self.data, outfile)
        self.is_dirty = False

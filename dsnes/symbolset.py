import memory


class SymbolSet():
    def __init__(self):
        self._address_labels = dict()
        self._label_addresses = dict()
        self._generic_id = 0
        self._var_accesses = dict()

    def add_label(self, address, label):
        address = memory.normalise(address)
        if address in self._address_labels:
            raise TargetRelabelException("{:#04X} has already been given the "
                "label {}".format(address, self._address_labels[address]))
        if label in self._label_addresses:
            raise LabelReuseException('The label "{}" is already used '
                'at {:#04X}'.format(label, address))

        self._address_labels[address] = label
        self._label_addresses[label] = address

    def add_generic_label(self, address):
        address = memory.normalise(address)
        label = "label{:04}".format(self._generic_id)
        self.add_label(address, label)
        self._generic_id += 1

    def add_generic_variable(self, address):
        address = memory.normalise(address)
        assert memory.RAM.contains(address)
        if address > memory.MAX_ZERO_PAGE:
            label = "var{:04}".format(self._generic_id)
        else:
            label = "zpv{:04}".format(self._generic_id)
        self.add_label(address, label)
        self._generic_id += 1

    def add_base_variable(self, address):
        address = memory.normalise(address)
        assert memory.RAM.contains(address)
        if address > memory.MAX_ZERO_PAGE:
            label = "vb{:04}".format(self._generic_id)
        else:
            label = "zb{:04}".format(self._generic_id)
        self.add_label(address, label)
        self._generic_id += 1

    def add_indirect_variable(self, address):
        address = memory.normalise(address)
        assert memory.RAM.contains(address)
        if address > memory.MAX_ZERO_PAGE:
            label = "vi{:04}".format(self._generic_id)
            self.add_label(address, label)
            self._generic_id += 1
        else:
            # Indirection target is read from the provided ZP address and
            # the ZP address immediately after it.  Wrapping is possible,
            # but easier not to support it unless absolutely necessary.
            assert address <= memory.MAX_ZERO_PAGE - 1
            label = "zi{:04}".format(self._generic_id)
            self.add_label(address, label)
            self._generic_id += 1
            self.add_label(address+1, label)
            self._generic_id += 1

    def get_label(self, address):
        address = memory.normalise(address)
        return self._address_labels.get(address, None)

    def get_address(self, label):
        return self._label_addresses.get(label, None)

    def record_variable_access(self, chunk, address, access_kind):
        """
        Record read/write/readwrite access of a variable from a particular
        address.
        """
        address = int(address)
        assert access_kind in (
            memory.access.read, memory.access.write, memory.access.readwrite)

        try:
            record = self._var_accesses[address]
        except KeyError:
            record = {
                memory.access.read: [],
                memory.access.write: [],
                memory.access.readwrite: []
            }
            self._var_accesses[address] = record

        record[access_kind].append((chunk, address))


class NullSymbols():
    def get_label(self, address):
        return None

    def get_address(self, label):
        return None


class TargetRelabelException(Exception):
    pass

class LabelReuseException(Exception):
    pass

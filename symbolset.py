import memory


class SymbolSet():
    def __init__(self):
        self._address_labels = dict()
        self._label_addresses = dict()
        self._generic_id = 0

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
        label = "var{:04}".format(self._generic_id)
        self.add_label(address, label)
        self._generic_id += 1

    def get_label(self, address):
        address = memory.normalise(address)
        return self._address_labels.get(address, None)

    def get_address(self, label):
        return self._label_addresses.get(label, None)


class TargetRelabelException(Exception):
    pass

class LabelReuseException(Exception):
    pass

class LabelSet():
    def __init__(self):
        self._address_labels = dict()
        self._label_addresses = dict()
        self._generic_id = 0

    def add(self, address, label):
        if address in self._address_labels:
            raise Exception("{:#04X} already has the label {}".format(
                address, self._address_labels[address]))
        if label in self._label_addresses:
            raise Exception('The label "{}" is being used at {:#04X}'.format(
                label, address))

        self._address_labels[address] = label
        self._label_addresses[label] = address

    def add_generic(self, address):
        label = "label{:04}".format(self._generic_id)
        self._generic_id += 1
        self.add_label(address, label)

    def get_label(self, address):
        return self._address_labels.get(address, None)

    def get_address(self, label):
        return self._label_addresses.get(label, None)

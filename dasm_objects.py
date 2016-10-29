class Program():
    def __init__(self, memory):
        self.mem = memory
        self.entry_points = set()
        self.labels = dict()
        self.chunks = set()

    def print_entry_points(self):
        addresses = [
            "{label} 0x{address:04X}".format(
                label=self.labels[addr], address=addr)
            for addr in self.entry_points]
        print("Entry points are:\n{}".format("\n".join(addresses)))


class Chunk():
    def __init__(self, start_address):
        self.start_address = start_address
        self.entry_points = set((start_address,))
        self.exit_points = set()

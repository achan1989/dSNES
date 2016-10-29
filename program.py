class Program():
    def __init__(self, memory):
        self.mem = memory
        self.entry_points = set()
        self.labels = dict()

    def print_entry_points(self):
        addresses = [
            "{label} 0x{address:04X}".format(
                label=self.labels[addr], address=addr)
            for addr in self.entry_points]
        print("Entry points are:\n{}".format("\n".join(addresses)))

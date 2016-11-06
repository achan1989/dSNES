import symbolset


UNKNOWN_JUMP_TARGET = "UNKNOWN_JUMP_TARGET"
RETURN_TO_CALLER = "RETURN_TO_CALLER"


class Program():
    def __init__(self, memory):
        self.mem = memory
        self.entry_points = set()
        self.symbols = symbolset.SymbolSet()
        self.chunks = set()

    def print_entry_points(self):
        addresses = [
            "{label} {address:#04X}".format(
                label=self.symbols.get_label(addr), address=addr)
            for addr in self.entry_points]
        print("Entry points are:\n{}".format("\n".join(addresses)))


class Chunk():
    def __init__(self, start_address):
        self.start_address = start_address
        self.entry_points = set((start_address,))
        self.exit_points = set()
        self.instructions = []

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def add_and_label_exit_point(self, address, target, symbols):
        self.exit_points.add((address, target))

        if target not in (UNKNOWN_JUMP_TARGET, RETURN_TO_CALLER):
            try:
                symbols.add_generic_label(target)
            except symbolset.TargetRelabelException:
                # If the target already has a label that's ok.
                pass

    def print_instructions(self, symbols=None):
        print("Chunk at 0x{addr:04X}:".format(addr=self.start_address))
        for inst in self.instructions:
            if symbols:
                label = symbols.get_label(inst.address)
                if label:
                    print("{}:".format(label))

            print("0x{addr:04X}    {asm}".format(
                addr=inst.address,
                asm=inst.assembly_string(symbols)))

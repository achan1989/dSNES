import symbolset
import config


UNKNOWN_JUMP_TARGET = "UNKNOWN_JUMP_TARGET"
RETURN_TO_CALLER = "RETURN_TO_CALLER"

SPECIAL_TARGETS = (UNKNOWN_JUMP_TARGET, RETURN_TO_CALLER)


class Program():
    def __init__(self, memory):
        self.mem = memory
        self.entry_points = set()
        self.symbols = symbolset.SymbolSet()
        self.config = config.Config()
        self.chunks = []

    def print_entry_points(self):
        addresses = [
            "{label} {address:#04X}".format(
                label=self.symbols.get_label(addr), address=addr)
            for addr in self.entry_points]
        print("Entry points are:\n{}".format("\n".join(addresses)))

    def get_chunk(self, address):
        """ Try to find a chunk that contains the given address.  May return
        None.
        """
        for chunk in self.chunks:
            if chunk.start_address <= address <= chunk.end_address:
                return chunk
        return None

    def print_callers_of(self, target):
        callers = self.get_callers_of(target)
        print("Callers of 0x{:04X}:".format(target))
        if len(callers) == 0:
            print("None")
        else:
            for chunk, ep in callers:
                address, _ = ep
                print("{} at address 0x{:04X}".format(chunk, address))

    def get_callers_of(self, target):
        callers = []
        for chunk in self.chunks:
            ep = chunk.get_exit_point_with_target(target)
            if ep:
                callers.append((chunk, ep))
        return callers


class Chunk():
    def __init__(self, start_address):
        self.start_address = start_address
        self.end_address = start_address
        self.entry_points = set((start_address,))
        self.exit_points = set()
        self.instructions = []

    def __str__(self):
        return "<chunk from 0x{:04X} to 0x{:04X}>".format(
            self.start_address, self.end_address)

    def add_instruction(self, instruction):
        self.instructions.append(instruction)
        addr = instruction.address
        if addr > self.end_address:
            self.end_address = addr

    def add_and_label_exit_point(self, address, target, symbols):
        self.exit_points.add((address, target))

        if target not in SPECIAL_TARGETS:
            try:
                symbols.add_generic_label(target)
            except symbolset.TargetRelabelException:
                # If the target already has a label that's ok.
                pass

    def clean_exit_points(self):
        """
        Remove "exit" points that are really just jumps within this chunk.
        """
        def is_valid(ep):
            address, target = ep
            if target in SPECIAL_TARGETS:
                return True
            return not (self.start_address <= target <= self.end_address)
        self.exit_points = set([ep for ep in self.exit_points if is_valid(ep)])

    def get_exit_point_with_target(self, target):
        for ep in self.exit_points:
            _, ep_target = ep
            if target == ep_target:
                return ep
        return None

    def print_instructions(self, symbols=None):
        print("Chunk from 0x{start:04X} to 0x{end:04X}:".format(
            start=self.start_address,
            end=self.end_address))
        for inst in self.instructions:
            if symbols:
                label = symbols.get_label(inst.address)
                if label:
                    print("{}:".format(label))

            print("0x{addr:04X}    {asm}".format(
                addr=inst.address,
                asm=inst.assembly_string(symbols)))

# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import collections

import dsnes


class Analyser:
    def __init__(self, project):
        self.project = project
        self.state = None
        self.disassembly = None
        # List of (target, from) tuples.
        self.calls = None
        self.visited = None
        self.reset()

    def reset(self):
        self.state = dsnes.State()
        self.disassembly = []
        self.calls = []
        self.visited = set()

    def analyse_function(self, address, state_str=None):
        self.reset()
        orig_addr = address
        bus = self.project.bus
        db = self.project.database
        queue = collections.deque()
        queue.append(orig_addr)
        # By default we don't know what state the CPU is in, though the caller
        # can provide a starting state.
        if state_str is not None:
            calculated_state = dsnes.State.parse(str(state_str))
        else:
            calculated_state = dsnes.State()

        while queue:
            address = queue.pop()

            while True:
                if address in self.visited:
                    break

                # If the user claims to know the state for this instruction,
                # use it.
                declared_state = db.get_state(address)
                if declared_state is not None:
                    self.state = declared_state
                # Otherwise use the state that was calculated by executing the
                # previous instruction.
                else:
                    self.state = calculated_state

                disassembly = dsnes.disassemble(address, bus, self.state)
                self.disassembly.append(disassembly)
                calculated_state = disassembly.new_state

                do_next = disassembly.next_addr
                action, data = do_next[0], do_next[1:]

                if action in (dsnes.NextAction.step, dsnes.NextAction.jump):
                    # Temporarily treat jump like a step.
                    next_addr = data[0]
                elif action is dsnes.NextAction.call:
                    target, after_return = data
                    self.calls.append((target, address))
                    next_addr = after_return
                elif action is dsnes.NextAction.branch:
                    taken_addr, not_taken_addr = data
                    next_addr = taken_addr
                    queue.append(not_taken_addr)
                else:
                    raise NotImplementedError(
                        "Analyser can't handle {}".format(action))

                self.visited.add(address)
                address = next_addr

    def display(self):
        # disassembly = sorted(self.disassembly, key=lambda x: x.addr)
        disassembly = self.disassembly
        for item in disassembly:

            # Try to replace an address with a label.
            target_info = item.target_info
            target_addr, str_fn = target_info
            label = None
            if target_addr:
                label = self.get_label_for(target_addr)
            tgt_str = str_fn(label)

            s = "{pbr:02x}:{pc:04x}:{raw:<11}  {asm:<15s}   {target:<18s}   {state}".format(
                pbr=(item.addr & 0xFF0000) >> 16,
                pc=item.addr & 0xFFFF,
                raw=" ".join([format(n, "02x") for n in item.raw]),
                asm=item.asm_str,
                target=tgt_str,
                state=item.state.encode())
            print(s)

    def get_label_for(self, addr):
        return "potato"

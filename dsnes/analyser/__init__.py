# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import collections

import dsnes


class Analyser:
    def __init__(self, project):
        self.project = project
        self.state = None
        self.operations = None
        # List of (target, from) tuples.
        self.calls = None
        self.visited = None
        self.reset()

    def reset(self):
        self.state = dsnes.State()
        self.operations = []
        self.calls = []
        self.visited = set()

    def analyse_function(self, address, state_str=None, stop_before=None):
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

                # If the user claims to know the exact state for this
                # instruction, use it.
                declared_state = db.get_state(address)
                if declared_state is not None:
                    self.state = declared_state
                # Otherwise use the state that was calculated by executing the
                # previous instruction.
                else:
                    self.state = calculated_state
                    # We can also modify this calculated state based on some
                    # partial state information provided by the user.
                    delta = db.get_state_delta(address)
                    if delta:
                        self.state = delta.apply(self.state)

                disassembly = dsnes.disassemble(address, bus, self.state)
                self.operations.append(disassembly)
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
                    next_addr = not_taken_addr
                    if taken_addr == stop_before:
                        print_address(address)
                        import pdb
                        pdb.set_trace()
                    queue.append(taken_addr)
                else:
                    raise NotImplementedError(
                        "Analyser can't handle {}".format(action))

                self.visited.add(address)
                if next_addr == stop_before:
                    print_address(address)
                    import pdb
                    pdb.set_trace()
                address = next_addr

    def display(self):
        for operation in self.operations:
            # Print label(s) and comments for this instruction.
            for label in self.get_labels_for(operation.addr):
                print(label)
            pre_comment = self.get_pre_comment_for(operation.addr)
            if pre_comment:
                lines = pre_comment.splitlines()
                for line in lines:
                    print(" ; {}".format(line))

            # Try to replace an address with a label.
            target_info = operation.target_info
            target_addr, str_fn = target_info
            label = None
            if target_addr:
                labels = self.get_labels_for(target_addr)
                if len(labels) == 0:
                    pass
                elif len(labels) == 1:
                    label = labels[0]
                else:
                    label = labels[0] + "..."
            tgt_str = str_fn(label)

            comment = self.get_inline_comment_for(operation)
            if comment:
                comment = "; {}".format(comment)

            s = " {pbr:02x}:{pc:04x}:{raw:<11}  {asm:<15s}   {target:<18s}  {comment:<35s}   {state}".format(
                pbr=(operation.addr & 0xFF0000) >> 16,
                pc=operation.addr & 0xFFFF,
                raw=" ".join([format(n, "02x") for n in operation.raw]),
                asm=operation.asm_str,
                target=tgt_str,
                comment=comment,
                state=operation.state.encode())
            print(s)

    def get_label_for(self, addr):
        try:
            hw_label = self.project.bus.get_label(addr)
        except dsnes.UnmappedMemoryAccess:
            hw_label = "UNMAPPED_{:06x}".format(addr)

        # User labels can override the default hardware label.
        user_label = self.project.database.get_label(addr)
        if user_label:
            return user_label
        else:
            return hw_label

    def get_labels_for(self, addr):
        try:
            hw_label = self.project.bus.get_label(addr)
        except dsnes.UnmappedMemoryAccess:
            hw_label = "UNMAPPED_{:06x}".format(addr)

        # Is always at least an empty list.
        user_labels = self.project.database.get_labels(addr)
        if hw_label:
            user_labels.append(hw_label)
        return user_labels

    def get_pre_comment_for(self, addr):
        return self.project.database.get_pre_comment(addr)

    def get_inline_comment_for(self, operation):
        user = self.project.database.get_inline_comment(operation.addr)
        default = operation.default_comment
        return user or default or ""


def print_address(addr):
    print("At {:02x}:{:04x}".format(
        (address & 0xff0000) >> 16, address & 0xFFFF))

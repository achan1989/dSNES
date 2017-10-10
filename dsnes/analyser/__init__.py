# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import collections

import dsnes


class AnalyserError:
    def __init__(self, address, state, msg):
        self.kind = "error"
        self.addr = address
        self.state = state
        self.msg = msg


class Label:
    def __init__(self, operation, text):
        self.kind = "label"
        # The operation that this is associated with.
        self.operation = operation
        self.text = text


class PreComment:
    def __init__(self, operation, text):
        self.kind = "pre-comment"
        # The operation that this is associated with.
        self.operation = operation
        self.text = text


class Disassembly:
    def __init__(self, operation, target_str, comment):
        self.kind = "disassembly"
        self.operation = operation
        self.target_str = target_str
        self.comment = comment


class Analyser:
    def __init__(self, project):
        self.project = project
        self.start_address = None
        self.start_state = None
        self.state = None
        self.operations = None
        self.disassembly = None
        # Dict of from_address:[(to, state)].
        self.calls_from = None
        self.visited = None
        self.reset()

    def reset(self):
        self.start_address = None
        self.start_state = None
        self.state = dsnes.State()
        self.operations = []
        self.disassembly = []
        self.calls_from = collections.defaultdict(list)
        self.visited = set()

    def analyse_function(self, address, state=None, stop_before=None):
        self.reset()
        self.start_address = address
        self.start_state = state
        self._analyse_operations(address, state, stop_before)
        self._collate_disassembly()

    def _analyse_operations(self, address, state, stop_before):
        bus = self.project.bus
        db = self.project.database
        queue = collections.deque()
        queue.append(address)
        # By default we don't know what state the CPU is in, though the caller
        # can provide a starting state.
        if isinstance(state, dsnes.State):
            calculated_state = state
        elif state is not None:
            calculated_state = dsnes.State.parse(state)
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

                try:
                    self.visited.add(address)
                    disassembly = dsnes.disassemble(address, bus, self.state)
                except dsnes.AmbiguousDisassembly as ex:
                    error = AnalyserError(
                        address, self.state,
                        "Ambiguous {mnemonic} depends on {thing}".format(
                            mnemonic=ex.mnemonic, thing=ex.requires))
                    self.operations.append(error)
                    break
                else:
                    self.operations.append(disassembly)
                    calculated_state = disassembly.new_state

                    do_next = disassembly.next_addr
                    action, data = do_next[0], do_next[1:]

                    if action in (dsnes.NextAction.step, dsnes.NextAction.jump):
                        # Temporarily treat jump like a step.
                        next_addr = data[0]
                    elif action is dsnes.NextAction.call:
                        target, after_return = data
                        call_list = self.calls_from[address]
                        call_list.append((target, self.state))
                        next_addr = after_return
                    elif action is dsnes.NextAction.branch:
                        taken_addr, not_taken_addr = data
                        next_addr = not_taken_addr
                        if taken_addr == stop_before:
                            print_address(address)
                            import pdb
                            pdb.set_trace()
                        queue.append(taken_addr)
                    elif action is dsnes.NextAction.ret:
                        break
                    else:
                        raise NotImplementedError(
                            "Analyser can't handle {}".format(action))

                    if next_addr == stop_before:
                        print_address(address)
                        import pdb
                        pdb.set_trace()
                    address = next_addr

    def _collate_disassembly(self):
        disassembly = self.disassembly

        for operation in self.operations:
            for text in self.get_labels_for(operation.addr):
                item = Label(operation, text)
                disassembly.append(item)

            text = self.get_pre_comment_for(operation.addr)
            if text:
                item = PreComment(operation, text)
                disassembly.append(item)

            if isinstance(operation, AnalyserError):
                disassembly.append(operation)
            else:
                # Special manipulations for a line of disassembly.
                # Try to replace an operation's target address with a label.
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
                target_str = str_fn(label)

                comment = self.get_inline_comment_for(operation)

                disassembly.append(Disassembly(operation, target_str, comment))

    def get_disassembly_line(self, line_number):
        return self.disassembly[line_number]

    def get_disassembly_lines(self):
        return self.disassembly

    def get_calls_from(self, line_number):
        """Get calls made from the given disassembly line number.

        Returns a list of (call_target, state_before_call).
        """
        item = self.disassembly[line_number]
        if not isinstance(item, Disassembly):
            return []
        address = item.operation.addr
        # Use get() so the defaultdict doesn't add the empty list to itself.
        return self.calls_from.get(address, [])

    def display(self):
        """Print the disassembly."""
        for item in self.disassembly:
            if isinstance(item, Label):
                print(item.text)

            elif isinstance(item, PreComment):
                lines = item.text.splitlines()
                for line in lines:
                    print(" {}".format(line))

            elif isinstance(item, AnalyserError):
                self._display_error(item)

            else:
                self._display_operation(item)

    def _display_operation(self, operation):
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

        s = " {pbr:02x}:{pc:04x}:{raw:<11}  {asm:<15s}   {target:<18s}  {comment:<35s}   {state}".format(
            pbr=(operation.addr & 0xFF0000) >> 16,
            pc=operation.addr & 0xFFFF,
            raw=" ".join([format(n, "02x") for n in operation.raw]),
            asm=operation.asm_str,
            target=tgt_str,
            comment=comment or "",
            state=operation.state.encode())
        print(s)

    def _display_error(self, error):
        error_msg = "!!!{}!!!".format(error.msg)
        s = " {pbr:02x}:{pc:04x}{pad:<12}  {msg:^73}   {state}".format(
            pbr=(error.addr & 0xFF0000) >> 16,
            pc=error.addr & 0xFFFF,
            pad="",
            msg=error_msg,
            state=error.state.encode())
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
        return user or default or None


def print_address(addr):
    print("At {:02x}:{:04x}".format(
        (address & 0xff0000) >> 16, address & 0xFFFF))

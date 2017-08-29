"""Code adapted from the higan emulator.
See https://gitlab.com/higan/higan/tree/master/processor/wdc65816

Original code copyright byuu, and licensed under GPLv3 (see
https://byuu.org/emulation/higan/licensing).
"""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import collections
from enum import Enum

import dsnes
from dsnes import util


Disassembly = collections.namedtuple(
    "Disassembly",
    ["addr", "raw", "asm_str", "target_info", "state", "next_addr",
     "new_state", "default_comment"])

TargetInfo = collections.namedtuple(
    "TargetInfo",
    ["addr", "str_fn"])

NULL_TARGET_INFO = TargetInfo(addr=None, str_fn=lambda l: "")


class NextAction(Enum):
    step = 1
    jump = 2
    call = 3
    ret = 4
    branch = 5


class InstructionType:
    nbytes = None

    def __init__(self, mnemonic, default_comment=None):
        self.mnemonic = mnemonic
        self.default_comment = default_comment

    def disassemble(self, addr, state, opcode, op0, op1, op2):
        return Disassembly(
            addr=addr,
            raw=self.get_raw_bytes(addr, state, opcode, op0, op1, op2),
            asm_str=self.asm_str(addr, state, op0, op1, op2),
            target_info=self.target_info(addr, state, op0, op1, op2),
            state=state,
            next_addr=self.next_instruction_addr(addr, state, op0, op1, op2),
            new_state=self.new_state(addr, state.clone(), op0, op1, op2),
            default_comment=self.get_default_comment(addr, state, op0, op1, op2)
        )

    def get_raw_bytes(self, addr, state, opcode, op0, op1, op2):
        if self.nbytes is None:
            raise NotImplementedError(
                "get_raw_bytes() for {}".format(self.__class__.__name__))
        b = (opcode, op0, op1, op2)
        return b[:self.nbytes]

    def asm_str(self, addr, state, op0, op1, op2):
        raise NotImplementedError(
            "Not implemented for {}".format(self.__class__.__name__))

    def target_info(self, addr, state, op0, op1, op2):
        raise NotImplementedError(
            "Not implemented for {}".format(self.__class__.__name__))

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Most instructions can't cross bank boundaries. If the PC increments
        # past 0xFFFF it rolls over to 0x0000 without changing PBR.
        if self.nbytes is None:
            raise NotImplementedError(
                "next_instruction_addr() for {}".format(
                    self.__class__.__name__))
        pbr = addr & 0xFF0000
        a = addr & 0xFFFF
        a = (a + self.nbytes) & 0xFFFF
        return (NextAction.step, pbr + a)

    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        # Most instructions leave most things unchanged.
        # Most instructions change c in ways we can't predict and don't care
        # about.
        state.c = None
        return state

    def get_default_comment(self, addr, state, op0, op1, op2):
        """Get the default comment for this instruction.

        Return the default_comment keyword argument if it was given, else None.
        """
        return self.default_comment

# Basic addressing modes.

class Immediate8(InstructionType):
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        return "{} #${:02x}".format(self.mnemonic, op8)

    def target_info(self, addr, state, op0, op1, op2):
        return NULL_TARGET_INFO

class ImmediateAmbiguous(InstructionType):
    def __init__(self, mnemonic, selector, default_comment=None):
        assert selector in ("a8", "x8")
        super().__init__(mnemonic, default_comment)
        self.selector = selector

    def get_raw_bytes(self, addr, state, opcode, op0, op1, op2):
        b = (opcode, op0, op1, op2)
        a8 = state.e or state.m
        x8 = state.e or state.x

        if self.selector == "a8":
            if a8 is None:
                raise dsnes.AmbiguousDisassembly(self.mnemonic, "e or m flags")
            if a8:
                return b[:2]
            else:
                return b[:3]

        else:
            if x8 is None:
                raise dsnes.AmbiguousDisassembly(self.mnemonic, "e or x flags")
            if x8:
                return b[:2]
            else:
                return b[:3]

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        op16 = op0 | (op1 << 8)
        a8 = state.e or state.m
        x8 = state.e or state.x

        if self.selector == "a8":
            if a8 is None:
                raise dsnes.AmbiguousDisassembly(self.mnemonic, "e or m flags")
            if a8:
                return "{} #${:02x}".format(self.mnemonic, op8)
            else:
                return "{} #${:04x}".format(self.mnemonic, op16)

        else:
            if x8 is None:
                raise dsnes.AmbiguousDisassembly(self.mnemonic, "e or x flags")
            if x8:
                return "{} #${:02x}".format(self.mnemonic, op8)
            else:
                return "{} #${:04x}".format(self.mnemonic, op16)

    def target_info(self, addr, state, op0, op1, op2):
        return NULL_TARGET_INFO

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # The instruction length depends on the processor flags e/m/x.
        # This instruction also can't cross bank boundaries. If the PC
        # increments past 0xFFFF it rolls over to 0x0000 without changing PBR.
        a8 = state.e or state.m
        x8 = state.e or state.x

        if self.selector == "a8":
            if a8 is None:
                raise dsnes.AmbiguousDisassembly(self.mnemonic, "e or m flags")
            if a8:
                nbytes = 2
            else:
                nbytes = 3

        else:
            if x8 is None:
                raise dsnes.AmbiguousDisassembly(self.mnemonic, "e or x flags")
            if x8:
                nbytes = 2
            else:
                nbytes = 3

        pbr = addr & 0xFF0000
        a = addr & 0xFFFF
        a = (a + nbytes) & 0xFFFF
        return (NextAction.step, pbr + a)

class Absolute(InstructionType):
    nbytes = 3

    def asm_str(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} ${:04x}".format(self.mnemonic, op16)

    def target_info(self, addr, state, op0, op1, op2):
        pc = op0 | (op1 << 8)
        if state.dbr is None:
            tgt_addr = None
            addr_str = "DBR:{:04x}".format(pc)
        else:
            tgt_addr = (state.dbr << 16) | pc
            addr_str = "{:06x}".format(tgt_addr)

        def str_fn(label=None):
            if label is None:
                label = addr_str
            return "[{}]".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

class AbsLong(InstructionType):
    nbytes = 4

    def asm_str(self, addr, state, op0, op1, op2):
        op24 = op0 | (op1 << 8) | (op2 << 16)
        if state.e is not False:
            raise ValueError(
                "AbsLong address mode only available in native mode")
        return "{} ${:06x}".format(self.mnemonic, op24)

    def target_info(self, addr, state, op0, op1, op2):
        tgt_addr = op0 | (op1 << 8) | (op2 << 16)

        def str_fn(label=None):
            if label is None:
                label = "{:06x}".format(tgt_addr)
            return "[{}]".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

class AbsLongX(InstructionType):
    """Absolute long, indexed by X."""
    nbytes = 4

    def asm_str(self, addr, state, op0, op1, op2):
        op24 = op0 | (op1 << 8) | (op2 << 16)
        if state.e is not False:
            raise ValueError(
                "AbsLongX address mode only available in native mode")
        return "{} ${:06x},x".format(self.mnemonic, op24)

    def target_info(self, addr, state, op0, op1, op2):
        tgt_addr = op0 | (op1 << 8) | (op2 << 16)

        def str_fn(label=None):
            if label is None:
                label = "{:06x}".format(tgt_addr)
            return "[{}],x".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

class AbsoluteX(InstructionType):
    """Absolute, indexed by X."""
    nbytes = 3

    def asm_str(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} ${:04x},x".format(self.mnemonic, op16)

    def target_info(self, addr, state, op0, op1, op2):
        pc = op0 | (op1 << 8)
        if state.dbr is None:
            tgt_addr = None
            addr_str = "DBR:{:04x}".format(pc)
        else:
            tgt_addr = (state.dbr << 16) | pc
            addr_str = "{:06x}".format(tgt_addr)

        def str_fn(label=None):
            if label is None:
                label = addr_str
            return "[{}]+x".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

    def get_default_comment(self, *args):
        comment = "Can cross banks."
        dc = self.default_comment
        if dc:
            comment += " {}".format(dc)
        return comment

class AbsoluteY(InstructionType):
    """Absolute, indexed by Y."""
    nbytes = 3

    def asm_str(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} ${:04x},y".format(self.mnemonic, op16, op16)

    def target_info(self, addr, state, op0, op1, op2):
        pc = op0 | (op1 << 8)
        if state.dbr is None:
            tgt_addr = None
            addr_str = "DBR:{:04x}".format(pc)
        else:
            tgt_addr = (state.dbr << 16) | pc
            addr_str = "{:06x}".format(tgt_addr)

        def str_fn(label=None):
            if label is None:
                label = addr_str
            return "[{}]+y".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

    def get_default_comment(self, *args):
        comment = "Can cross banks."
        dc = self.default_comment
        if dc:
            comment += " {}".format(dc)
        return comment

class AbsXInd(InstructionType):
    """(Absolute, indexed by X) indirect.

    Only used for jump/call."""
    nbytes = 3

    def asm_str(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} (${:04x},x)".format(self.mnemonic, op16)

    def target_info(self, addr, state, op0, op1, op2):
        pbr = addr & 0xFF0000
        pbr_str = "{:02x}".format(pbr >> 16)
        ind_pc = op0 | (op1 << 8)
        indirect_addr = pbr | ind_pc
        indirect_str = "{:06x}".format(indirect_addr)

        def str_fn(label=None):
            if label is None:
                label = indirect_str
            return "[{pbr}:({label}+x)]".format(
                pbr=pbr_str, label=label)

        ti = TargetInfo(addr=indirect_addr, str_fn=str_fn)
        return ti

class DirectPage(InstructionType):
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        return "{} ${:02x}".format(
            self.mnemonic, op8, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0

        def str_fn(label=None):
            assert label is None
            return "[00:DP+{:02x}]".format(offset)

        ti = TargetInfo(addr=None, str_fn=str_fn)
        return ti

class DirectPageX(InstructionType):
    """Direct Page, indexed by X."""
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        return "{} ${:02x},x".format(self.mnemonic, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0

        def str_fn(label=None):
            assert label is None
            return "[00:DP+{:02x}]+x".format(offset)

        ti = TargetInfo(addr=None, str_fn=str_fn)
        return ti

    def get_default_comment(self, addr, state, op0, op1, op2):
        if state.e is False and state.x is False:
            comment = "Target is masked 0xFFFF."
        else:
            comment = "Wrapping rules p102."
        if self.default_comment:
            comment += " {}".format(self.default_comment)
        return comment

class DirectPageY(InstructionType):
    """Direct Page, indexed by Y."""
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        return "{} ${:02x},y      [00:DP+{:02x}]+y".format(
            self.mnemonic, op8, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0

        def str_fn(label=None):
            assert label is None
            return "[00:DP+{:02x}]+y".format(offset)

        ti = TargetInfo(addr=None, str_fn=str_fn)
        return ti

    def get_default_comment(self, addr, state, op0, op1, op2):
        if state.e is False and state.x is False:
            comment = "Target is masked 0xFFFF."
        else:
            comment = "Wrapping rules p102."
        if self.default_comment:
            comment += " {}".format(self.default_comment)
        return comment

class DPInd(InstructionType):
    """Direct Page indirect."""
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        if state.e is not False:
            raise ValueError("DPInd address mode only available in native mode")
        return "{} (${:02x})".format(self.mnemonic, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0
        if state.dbr is None:
            dbr_str = "DBR"
        else:
            dbr_str = "{:02x}".format(state.dbr)

        def str_fn(label=None):
            assert label is None
            return "[{dbr_str}:(00:DP+{offset:02x})]".format(
                dbr_str=dbr_str, offset=offset)

        ti = TargetInfo(addr=None, str_fn=str_fn)
        return ti

class DPIndLong(InstructionType):
    """Direct Page indirect, long."""
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        if state.e is not False:
            raise ValueError(
                "DPIndLong address mode only available in native mode")
        return "{} [${:02x}]".format(self.mnemonic, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0

        def str_fn(label=None):
            assert label is None
            return "[(00:DP+{:02x})]".format(offset)

        ti = TargetInfo(addr=None, str_fn=str_fn)
        return ti

class DPIndY(InstructionType):
    """(Direct Page indirect), indexed by Y.

    Indexing can cause the address to roll into the next bank.
    """
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        return "{} (${:02x}),y".format(
            self.mnemonic, op8, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0
        if state.dbr is None:
            dbr_str = "DBR"
        else:
            dbr_str = "{:02x}".format(state.dbr)

        def str_fn(label=None):
            assert label is None
            return "[{dbr}:(00:DP+{offset:02x})]+y".format(
                dbr=dbr_str, offset=offset)

        ti = TargetInfo(addr=None, str_fn=str_fn)
        return ti

class DPIndLongY(InstructionType):
    """(Direct Page indirect) long, indexed by Y."""
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        if state.e is not False:
            raise ValueError(
                "DPIndLongY address mode only available in native mode")
        return "{} [${:02x}],y".format(
            self.mnemonic, op8, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0

        def str_fn(label=None):
            assert label is None
            return "[(00:DP+{offset:02x})]+y".format(offset=offset)

        ti = TargetInfo(addr=None, str_fn=str_fn)
        return ti

class DPXInd(InstructionType):
    """(Direct Page, indexed by X) indirect."""
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        return "{} (${:02x},x)".format(self.mnemonic, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0
        if state.dbr is None:
            dbr_str = "DBR"
        else:
            dbr_str = "{:02x}".format(state.dbr)

        def str_fn(label=None):
            assert label is None
            return "[{dbr}:(00:DP+{offset:02x}+x)]".format(
                dbr=dbr_str, offset=offset)

        ti = TargetInfo(addr=None, str_fn=str_fn)
        return ti

    def get_default_comment(self, addr, state, op0, op1, op2):
        comment = "Wrapping rules p163."
        if self.default_comment:
            comment += " {}".format(self.default_comment)
        return comment

class BlockMove(InstructionType):
    """Move a block of memory."""
    nbytes = 3

    def asm_str(self, addr, state, op0, op1, op2):
        if state.e is not False:
            raise ValueError(
                "BlockMove address mode only available in native mode")
        return "{} ${:02x},${:02x}".format(self.mnemonic, op1, op0)
        # TODO: could put additional info into this dasm.

class Implied(InstructionType):
    nbytes = 1

    def asm_str(self, addr, state, op0, op1, op2):
        return self.mnemonic

    def target_info(self, addr, state, op0, op1, op2):
        return NULL_TARGET_INFO

class Accumulator(Implied):
    """Currently as Implied, may need to do special case later."""
    pass

class Stack(Implied):
    """Currently as Implied, may need to do special case later."""
    pass

class StackRelative(InstructionType):
    """Stack pointer + offset."""
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        if state.e is not False:
            raise ValueError(
                "StackRelative address mode only available in native mode")
        return "{} ${:02x},s".format(
            self.mnemonic, op8, op8)

    def target_info(self, addr, state, op0, op1, op2):
        op8 = op0
        def str_fn(label=None):
            assert label is None
            return "[00:SP+{:02x}]".format(op8)

        return TargetInfo(addr=None, str_fn=str_fn)

class StackRelativeIndY(InstructionType):
    """(Stack pointer + offset) indirect, indexed by Y."""
    nbytes = 2

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        if state.e is not False:
            raise ValueError(
                "StackRelativeIndY address mode only available in native mode")
        return "{} (${:02x},s),y".format(self.mnemonic, op8)

    def target_info(self, addr, state, op0, op1, op2):
        offset = op0
        if state.dbr is not None:
            dbr_str = "{:02x}".format(state.dbr)
        else:
            dbr_str = "DBR"

        def str_fn(label=None):
            assert label is None
            return "[{dbr}:(SP+{offset:02x})]+y".format(
                dbr=dbr_str, offset=offset)

        return TargetInfo(addr=None, str_fn=str_fn)

class PushEffectiveAbs(Absolute):
    """Push 16b of data to stack."""
    pass

class PushEffectiveInd(DPInd):
    """Push 16b from ((Direct Page + offset) indirect) to stack."""
    pass

class PushEffectiveRel(InstructionType):
    """Push 16b = (PC + offset) to stack."""
    nbytes = 3

    def asm_str(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} ${:04x}      [PC+{:04x}]".format(self.mnemonic, op16, op16)

    def target_info(self, addr, state, op0, op1, op2):
        pbr = addr & 0xFF0000
        pc = addr & 0xFFFF
        next_pc = (pc + self.nbytes) & 0xFFFF
        op16 = op0 | (op1 << 8)
        # Always wraps to 16b
        data = (next_pc + op16) & 0xFFFF

        def str_fn(label=None):
            # Can't know if this is supposed to refer to code (PBR) or
            # data (DBR).
            assert label is None
            return "[{:04x}]"

        return TargetInfo(addr=None, str_fn=str_fn)

# Special cases, or derived from basic addressing modes.

class CallAbs(Absolute):
    def target_info(self, addr, state, op0, op1, op2):
        pbr = addr & 0xFF0000
        pbr_str = "{:02x}".format(pbr << 16)
        pc = op0 | (op1 << 8)
        tgt_addr = pbr | pc
        addr_str = "{:06x}".format(tgt_addr)

        def str_fn(label=None):
            if label is None:
                label = addr_str
            return "[{}]".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Call into the 16b address provided. This is in the same program
        # bank as this instruction.
        op16 = op0 | (op1 << 8)
        pbr = addr & 0xFF0000
        target = pbr + op16
        # Return address from the call.
        base = super().next_instruction_addr(addr, state, op0, op1, op2)
        assert base[0] == NextAction.step
        after_return = base[1]

        return (NextAction.call, target, after_return)

    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        # Technically we don't know anything about the state after returning
        # from a subroutine, but I'll assume that changing the emulation mode
        # is unlikely.
        state.m = None
        state.x = None
        state.c = None
        state.dbr = None
        return state

class CallAbsLong(AbsLong):
    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Call into the 24b address provided.
        op24 = op0 | (op1 << 8) | (op2 << 16)
        target = op24
        # Return address from the call.
        base = super().next_instruction_addr(addr, state, op0, op1, op2)
        assert base[0] == NextAction.step
        after_return = base[1]

        return (NextAction.call, target, after_return)

    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        # Technically we don't know anything about the state after returning
        # from a subroutine, but I'll assume that changing the emulation mode
        # is unlikely.
        state.m = None
        state.x = None
        state.c = None
        state.dbr = None
        return state

class CallAbsXInd(AbsXInd):
    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # We can't tell where the call goes.
        target = None
        # Return address from the call.
        base = super().next_instruction_addr(addr, state, op0, op1, op2)
        assert base[0] == NextAction.step
        after_return = base[1]

        return (NextAction.call, target, after_return)

    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        # Technically we don't know anything about the state after returning
        # from a subroutine, but I'll assume that changing the emulation mode
        # is unlikely.
        state.m = None
        state.x = None
        state.c = None
        state.dbr = None
        return state

class ReturnInt(Stack):
    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        return (NextAction.ret, )

class ReturnSub(Stack):
    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        return (NextAction.ret, )

class ReturnSubLong(Stack):
    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        return (NextAction.ret, )

class JumpAbs(Absolute):
    def target_info(self, addr, state, op0, op1, op2):
        pbr = addr & 0xFF0000
        pbr_str = "{:02x}".format(pbr >> 16)
        pc = op0 | (op1 << 8)
        tgt_addr = pbr | pc
        addr_str = "{:06x}".format(tgt_addr)

        def str_fn(label=None):
            if label is None:
                label = addr_str
            return "[{}]".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Jump to the 16b address provided. This is in the same program
        # bank as this instruction.
        op16 = op0 | (op1 << 8)
        pbr = addr & 0xFF0000
        target = pbr + op16

        return (NextAction.jump, target)

class JumpAbsInd(InstructionType):
    """Jump to 16b address in (bank 0 + offset) indirect."""
    nbytes = 3

    def asm_str(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} (${:04x})".format(self.mnemonic, op16)

    def target_info(self, addr, state, op0, op1, op2):
        pbr = addr & 0xFF0000
        pbr_str = "{:02x}".format(pbr >> 16)
        ind_addr = op0 | (op1 << 8)

        def str_fn(label=None):
            if label is None:
                label = "00:{:04x}".format(ind_addr)
            return "[{pbr}:({label})]".format(
                pbr=pbr_str, label=label)

        return TargetInfo(addr=ind_addr, str_fn=str_fn)

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Don't know where the jump goes.
        return (NextAction.jump, None)

class JumpAbsIndLong(InstructionType):
    """Jump to 24b address in (bank 0 + offset) indirect."""
    nbytes = 3

    def asm_str(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        if state.e is not False:
            raise ValueError(
                "JumpAbsIndLong address mode only available in native mode")
        return "{} [${:04x}]".format(self.mnemonic, op16)

    def target_info(self, addr, state, op0, op1, op2):
        pbr = addr & 0xFF0000
        pbr_str = "{:02x}".format(pbr >> 16)
        ind_addr = op0 | (op1 << 8)

        def str_fn(label=None):
            if label is None:
                label = "00:{:04x}".format(ind_addr)
            return "[{pbr}:({label})]".format(
                pbr=pbr_str, label=label)

        return TargetInfo(addr=ind_addr, str_fn=str_fn)

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Don't know where the jump goes.
        return (NextAction.jump, None)

class JumpAbsXInd(AbsXInd):
    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Don't know where the jump goes.
        return (NextAction.jump, None)

class JumpAbsLong(AbsLong):
    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Jump to the 24b address provided.
        op24 = op0 | (op1 << 8) | (op2 << 16)
        return (NextAction.jump, op24)

class BranchCond(InstructionType):
    nbytes = 2

    @classmethod
    def calc_target(cls, addr, operand):
        assert cls.nbytes is not None
        offset = util.s8_to_num(operand)
        pbr = addr & 0xff0000
        pc = (((addr & 0xffff) + cls.nbytes + offset) & 0xffff)
        target = pbr + pc
        return target

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        target = self.calc_target(addr, op8)
        return "{} ${:04x}".format(
            self.mnemonic, target & 0xFFFF, target)

    def target_info(self, addr, state, op0, op1, op2):
        op8 = op0
        tgt_addr = self.calc_target(addr, op8)

        def str_fn(label=None):
            if label is None:
                label = "{:06x}".format(tgt_addr)
            return "[{}]".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Stays within the same program bank as this instruction.
        # If branch is taken.
        op8 = op0
        taken = self.calc_target(addr, op8)
        # If branch is not taken.
        base = super().next_instruction_addr(addr, state, op0, op1, op2)
        assert base[0] == NextAction.step
        not_taken = base[1]

        return (NextAction.branch, taken, not_taken)

class BranchAlways(InstructionType):
    nbytes = 2

    @classmethod
    def calc_target(cls, addr, operand):
        assert cls.nbytes is not None
        offset = util.s8_to_num(operand)
        pbr = addr & 0xff0000
        pc = (((addr & 0xffff) + cls.nbytes + offset) & 0xffff)
        target = pbr + pc
        return target

    def asm_str(self, addr, state, op0, op1, op2):
        op8 = op0
        target = self.calc_target(addr, op8)
        return "{} ${:04x}".format(
            self.mnemonic, target & 0xFFFF, target)

    def target_info(self, addr, state, op0, op1, op2):
        op8 = op0
        tgt_addr = self.calc_target(addr, op8)

        def str_fn(label=None):
            if label is None:
                label = "{:06x}".format(tgt_addr)
            return "[{}]".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Stays within the same program bank as this instruction.
        op8 = op0
        target = self.calc_target(addr, op8)
        return (NextAction.jump, target)

class BranchAlwaysLong(InstructionType):
    nbytes = 3

    @classmethod
    def calc_target(cls, addr, operand):
        assert cls.nbytes is not None
        offset = util.s16_to_num(operand)
        pbr = addr & 0xff0000
        pc = (((addr & 0xffff) + cls.nbytes + offset) & 0xffff)
        target = pbr + pc
        return target

    def asm_str(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        if state.e is not False:
            raise ValueError(
                "BranchAlwaysLong address mode only available in native mode")
        target = self.calc_target(addr, op16)
        return "{} ${:04x}".format(self.mnemonic, target & 0xFFFF)

    def target_info(self, addr, state, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        tgt_addr = self.calc_target(addr, op16)

        def str_fn(label=None):
            if label is None:
                label = "{:06x}".format(tgt_addr)
            return "[{}]".format(label)

        ti = TargetInfo(addr=tgt_addr, str_fn=str_fn)
        return ti

    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Stays within the same program bank as this instruction.
        op16 = op0 | (op1 << 8)
        target = self.calc_target(addr, op16)
        return (NextAction.jump, target)

class Interrupt(InstructionType):
    def next_instruction_addr(self, addr, state, op0, op1, op2):
        """Get the PBR:PC value for the next instruction."""
        # Most instructions can't cross bank boundaries. If the PC increments
        # past 0xFFFF it rolls over to 0x0000 without changing PBR.
        assert self.nbytes is not None
        raise NotImplementedError("Interrupt")

class RFU(Implied):
    """Reserved for future use."""
    nbytes = 2

class REP(Immediate8):
    """Special handling of the REP opcode."""
    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        op8 = op0
        clear_m = bool(op8 & 0b00100000)
        clear_x = bool(op8 & 0b00010000)
        clear_c = bool(op8 & 0b00000001)

        # Native mode.
        if state.e is False:
            # Clear flags as specified.
            pass

        # Emulation mode.
        elif state.e is True:
            # Flags cannot be cleared.
            clear_m = False
            clear_x = False

        # Unknown native/emulation mode.
        else:
            # If the m or x bits are unaltered then it doesn't matter.
            # If they are being cleared then we have a problem.
            if clear_m or clear_x:
                raise dsnes.AmbiguousDisassembly(self.mnemonic, "e flag")

        if clear_m:
            state.m = False
        if clear_x:
            state.x = False
        if clear_c:
            state.c = False

        return state

    def get_default_comment(self, addr, state, op0, op1, op2):
        """Get the default comment for this instruction.

        Default comment says which flags were cleared.
        """
        op8 = op0
        flags = {
            "m": 0b00100000,
            "x": 0b00010000,
            "c": 0b00000001
        }
        was_clr = [letter for letter, mask in flags.items() if bool(op8 & mask)]
        if was_clr:
            return "Clear {}".format("/".join(was_clr))
        else:
            return None

class SEP(Immediate8):
    """Special handling of the SEP opcode."""
    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        op8 = op0
        set_m = bool(op8 & 0b00100000)
        set_x = bool(op8 & 0b00010000)
        set_c = bool(op8 & 0b00000001)

        # Native mode.
        if state.e is False:
            # Set flags as specified.
            pass

        # Emulation mode.
        elif state.e is True:
            # Flags cannot be set.
            set_m = False
            set_x = False

        # Unknown native/emulation mode.
        else:
            # If the m or x bits are unaltered then it doesn't matter.
            # If they are being set then we have a problem.
            if set_m or set_x:
                raise dsnes.AmbiguousDisassembly(self.mnemonic, "e flag")

        if set_m:
            state.m = True
        if set_x:
            state.x = True
        if set_c:
            state.c = True

        return state

    def get_default_comment(self, addr, state, op0, op1, op2):
        """Get the default comment for this instruction.

        Default comment says which flags were set.
        """
        op8 = op0
        flags = {
            "m": 0b00100000,
            "x": 0b00010000,
            "c": 0b00000001
        }
        was_set = [letter for letter, mask in flags.items() if bool(op8 & mask)]
        if was_set:
            return "Set {}".format("/".join(was_set))
        else:
            return None

class PLP(Stack):
    """Special handling of the PLP opcode."""
    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        op8 = op0

        # Native mode.
        if state.e is False:
            # Flags are replaced with unknown values.
            state.m = None
            state.x = None
            state.c = None

        # Emulation mode.
        elif state.e is True:
            state.c = None
            # m/x cannot be changed.

        # Unknown native/emulation mode.
        else:
            raise dsnes.AmbiguousDisassembly(self.mnemonic, "e flag")

        return state

class XCE(Implied):
    """Special handling of the XCE opcode."""
    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        # Enter native mode.
        # Assume that going native->native is treated the same way.
        if state.c is False:
            state.c = state.e
            state.e = False
            state.m = True
            state.x = True

        # Enter emulation mode.
        # Assume that going emulation->emulation is treated the same way.
        elif state.c is True:
            state.c = state.e
            state.e = True
            state.m = True
            state.x = True

        # Don't know which mode we're going into.
        else:
            # We could just set emulation mode to unknown and that would be ok.
            # But it's more useful to error out at this point and force the user
            # to figure out what's happening.
            raise dsnes.AmbiguousDisassembly(self.mnemonic, "c flag")

        return state

class SEC(Implied):
    """Special handling of the SEC opcode."""
    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        state.c = True
        return state

class CLC(Implied):
    """Special handling of the CLC opcode."""
    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        state.c = False
        return state

class PLB(Stack):
    """Special handling of the PLB opcode."""
    def new_state(self, addr, state, op0, op1, op2):
        """Get the CPU state after executing the instruction.

        Return a modified State.
        """
        state.dbr = None
        return state


codes = {
0x00: Interrupt("brk"), # ("brk #$%.2x              ", op8),
0x01: DPXInd("ora"), # ("ora ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0x02: Interrupt("cop"), # ("cop #$%.2x              ", op8),
0x03: StackRelative("ora"), # ("ora $%.2x,s     [%.6x]", op8, decode(OPTYPE_SR, op8)),
0x04: DirectPage("tsb"), # ("tsb $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x05: DirectPage("ora"), # ("ora $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x06: DirectPage("asl"), # ("asl $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x07: DPIndLong("ora"), # ("ora [$%.2x]     [%.6x]", op8, decode(OPTYPE_ILDP, op8)),
0x08: Stack("php"), # ("php                   "),
0x09: ImmediateAmbiguous("ora", "a8"), # (     ("ora #$%.2x              ", op8) if a8 else ("ora #$%.4x            ", op16)),
0x0a: Accumulator("asl a"), # ("asl a                 "),
0x0b: Stack("phd"), # ("phd                   "),
0x0c: Absolute("tsb"), # ("tsb $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x0d: Absolute("ora"), # ("ora $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x0e: Absolute("asl"), # ("asl $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x0f: AbsLong("ora"), # ("ora $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0x10: BranchCond("bpl"), # ("bpl $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0x11: DPIndY("ora"), # ("ora ($%.2x),y   [%.6x]", op8, decode(OPTYPE_IDPY, op8)),
0x12: DPInd("ora"), # ("ora ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0x13: StackRelativeIndY("ora"), # ("ora ($%.2x,s),y [%.6x]", op8, decode(OPTYPE_ISRY, op8)),
0x14: DirectPage("trb"), # ("trb $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x15: DirectPageX("ora"), # ("ora $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x16: DirectPageX("asl"), # ("asl $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x17: DPIndLongY("ora"), # ("ora [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0x18: CLC("clc"), # ("clc                   "),
0x19: AbsoluteY("ora"), # ("ora $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0x1a: Accumulator("inc"), # ("inc                   "),
0x1b: Implied("tcs", default_comment="Transfer 16b acc to SP"), # ("tcs                   "),
0x1c: Absolute("trb"), # ("trb $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x1d: AbsoluteX("ora"), # ("ora $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x1e: AbsoluteX("asl"), # ("asl $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x1f: AbsLongX("ora"), # ("ora $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
0x20: CallAbs("jsr"), # ("jsr $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR_PC, op16)),
0x21: DPXInd("and"), # ("and ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0x22: CallAbsLong("jsl"), # ("jsl $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0x23: StackRelative("and"), # ("and $%.2x,s     [%.6x]", op8, decode(OPTYPE_SR, op8)),
0x24: DirectPage("bit"), # ("bit $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x25: DirectPage("and"), # ("and $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x26: DirectPage("rol"), # ("rol $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x27: DPIndLong("and"), # ("and [$%.2x]     [%.6x]", op8, decode(OPTYPE_ILDP, op8)),
0x28: PLP("plp"), # ("plp                   "),
0x29: ImmediateAmbiguous("and", "a8"), # (     ("and #$%.2x              ", op8) if a8 else ("and #$%.4x            ", op16)),
0x2a: Accumulator("rol a"), # ("rol a                 "),
0x2b: Stack("pld"), # ("pld                   "),
0x2c: Absolute("bit"), # ("bit $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x2d: Absolute("and"), # ("and $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x2e: Absolute("rol"), #("rol $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x2f: AbsLong("and"), # ("and $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0x30: BranchCond("bmi"), # ("bmi $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0x31: DPIndY("and"), # ("and ($%.2x),y   [%.6x]", op8, decode(OPTYPE_IDPY, op8)),
0x32: DPInd("and"), # ("and ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0x33: StackRelativeIndY("and"), # ("and ($%.2x,s),y [%.6x]", op8, decode(OPTYPE_ISRY, op8)),
0x34: DirectPageX("bit"), # ("bit $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x35: DirectPageX("and"), # ("and $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x36: DirectPageX("rol"), # ("rol $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x37: DPIndLongY("and"), # ("and [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0x38: SEC("sec"), # ("sec                   "),
0x39: AbsoluteY("and"), # ("and $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0x3a: Accumulator("dec"), # ("dec                   "),
0x3b: Implied("tsc", default_comment="Transfer SP to 16b acc"), # ("tsc                   "),
0x3c: AbsoluteX("bit"), # ("bit $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x3d: AbsoluteX("and"), # ("and $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x3e: AbsoluteX("rol"), # ("rol $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x3f: AbsLongX("and"), # ("and $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
0x40: ReturnInt("rti"), # ("rti                   "),
0x41: DPXInd("eor"), # ("eor ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0x42: RFU("wdm", default_comment="!!RESERVED FOR FUTURE USE!!"), # ("wdm                   "),
0x43: StackRelative("eor"), # ("eor $%.2x,s     [%.6x]", op8, decode(OPTYPE_SR, op8)),
0x44: BlockMove("mvp"), # ("mvp $%.2x,$%.2x           ", op1, op8),
0x45: DirectPage("eor"), # ("eor $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x46: DirectPage("lsr"), # ("lsr $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x47: DPIndLong("eor"), # ("eor [$%.2x]     [%.6x]", op8, decode(OPTYPE_ILDP, op8)),
0x48: Stack("pha"), # ("pha                   "),
0x49: ImmediateAmbiguous("eor", "a8"), # (     ("eor #$%.2x              ", op8) if a8 else ("eor #$%.4x            ", op16)),
0x4a: Accumulator("lsr a"), # ("lsr a                 "),
0x4b: Stack("phk"), # ("phk                   "),
0x4c: JumpAbs("jmp"), # ("jmp $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR_PC, op16)),
0x4d: Absolute("eor"), # ("eor $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x4e: Absolute("lsr"), # ("lsr $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x4f: AbsLong("eor"), # ("eor $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0x50: BranchCond("bvc"), # ("bvc $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0x51: DPIndY("eor"), # ("eor ($%.2x),y   [%.6x]", op8, decode(OPTYPE_IDPY, op8)),
0x52: DPInd("eor"), # ("eor ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0x53: StackRelativeIndY("eor"), # ("eor ($%.2x,s),y [%.6x]", op8, decode(OPTYPE_ISRY, op8)),
0x54: BlockMove("mvn"), # ("mvn $%.2x,$%.2x           ", op1, op8),
0x55: DirectPageX("eor"), # ("eor $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x56: DirectPageX("lsr"), # ("lsr $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x57: DPIndLongY("eor"), # ("eor [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0x58: Implied("cli", default_comment="Enable interrupts"), # ("cli                   "),
0x59: AbsoluteY("eor"), # ("eor $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0x5a: Stack("phy"), # ("phy                   "),
0x5b: Implied("tcd", default_comment="Transfer 16b acc to DP reg"), # ("tcd                   "),
0x5c: JumpAbsLong("jml"), # ("jml $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0x5d: AbsoluteX("eor"), # ("eor $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x5e: AbsoluteX("lsr"), # ("lsr $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x5f: AbsLongX("eor"), # ("eor $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
0x60: ReturnSub("rts"), # ("rts                   "),
0x61: DPXInd("adc"), # ("adc ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0x62: PushEffectiveRel("per", default_comment="Push 16b [nextPC+offset], TODO validate"), # ("per $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x63: StackRelative("adc"), # ("adc $%.2x,s     [%.6x]", op8, decode(OPTYPE_SR, op8)),
0x64: DirectPage("stz"), # ("stz $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x65: DirectPage("adc"), # ("adc $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x66: DirectPage("ror"), # ("ror $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x67: DPIndLong("adc"), # ("adc [$%.2x]     [%.6x]", op8, decode(OPTYPE_ILDP, op8)),
0x68: Stack("pla"), # ("pla                   "),
0x69: ImmediateAmbiguous("adc", "a8"), # (     ("adc #$%.2x              ", op8) if a8 else ("adc #$%.4x            ", op16)),
0x6a: Accumulator("ror a"), # ("ror a                 "),
0x6b: ReturnSubLong("rtl"), # ("rtl                   "),
0x6c: JumpAbsInd("jmp"), # ("jmp ($%.4x)   [%.6x]", op16, decode(OPTYPE_IADDR_PC, op16)),
0x6d: Absolute("adc"), # ("adc $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x6e: Absolute("ror"), # ("ror $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x6f: AbsLong("adc"), # ("adc $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0x70: BranchCond("bvs"), # ("bvs $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0x71: DPIndY("adc"), # ("adc ($%.2x),y   [%.6x]", op8, decode(OPTYPE_IDPY, op8)),
0x72: DPInd("adc"), # ("adc ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0x73: StackRelativeIndY("adc"), # ("adc ($%.2x,s),y [%.6x]", op8, decode(OPTYPE_ISRY, op8)),
0x74: DirectPageX("stz"), # ("stz $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x75: DirectPageX("adc"), # ("adc $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x76: DirectPageX("ror"), # ("ror $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x77: DPIndLongY("adc"), # ("adc [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0x78: Implied("sei", default_comment="Disable interrupts"), # ("sei                   "),
0x79: AbsoluteY("adc"), # ("adc $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0x7a: Stack("ply"), # ("ply                   "),
0x7b: Implied("tdc", default_comment="Transfer DP reg to 16b acc"), # ("tdc                   "),
0x7c: JumpAbsXInd("jmp"), # ("jmp ($%.4x,x) [%.6x]", op16, decode(OPTYPE_IADDRX, op16)),
0x7d: AbsoluteX("adc"), # ("adc $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x7e: AbsoluteX("ror"), # ("ror $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x7f: AbsLongX("adc"), # ("adc $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
0x80: BranchAlways("bra"), # ("bra $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0x81: DPXInd("sta"), # ("sta ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0x82: BranchAlwaysLong("brl"), # ("brl $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELW, op16)), decode(OPTYPE_RELW, op16)),
0x83: StackRelative("sta"), # ("sta $%.2x,s     [%.6x]", op8, decode(OPTYPE_SR, op8)),
0x84: DirectPage("sty"), # ("sty $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x85: DirectPage("sta"), # ("sta $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x86: DirectPage("stx"), # ("stx $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0x87: DPIndLong("sta"), # ("sta [$%.2x]     [%.6x]", op8, decode(OPTYPE_ILDP, op8)),
0x88: Implied("dey"), # ("dey                   "),
0x89: ImmediateAmbiguous("bit", "a8"), # (     ("bit #$%.2x              ", op8) if a8 else ("bit #$%.4x            ", op16)),
0x8a: Implied("txa"), # ("txa                   "),
0x8b: Stack("phb"), # ("phb                   "),
0x8c: Absolute("sty"), # ("sty $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x8d: Absolute("sta"), # ("sta $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x8e: Absolute("stx"), # ("stx $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x8f: AbsLong("sta"), # ("sta $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0x90: BranchCond("bcc"), # ("bcc $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0x91: DPIndY("sta"), # ("sta ($%.2x),y   [%.6x]", op8, decode(OPTYPE_IDPY, op8)),
0x92: DPInd("sta"), # ("sta ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0x93: StackRelativeIndY("sta"), # ("sta ($%.2x,s),y [%.6x]", op8, decode(OPTYPE_ISRY, op8)),
0x94: DirectPageX("sty"), # ("sty $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x95: DirectPageX("sta"), # ("sta $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0x96: DirectPageY("stx"), # ("stx $%.2x,y     [%.6x]", op8, decode(OPTYPE_DPY, op8)),
0x97: DPIndLongY("sta"), # ("sta [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0x98: Implied("tya"), # ("tya                   "),
0x99: AbsoluteY("sta"), # ("sta $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0x9a: Implied("txs"), # ("txs                   "),
0x9b: Implied("txy"), # ("txy                   "),
0x9c: Absolute("stz"), # ("stz $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0x9d: AbsoluteX("sta"), # ("sta $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x9e: AbsoluteX("stz", default_comment="Store zero"), # ("stz $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x9f: AbsLongX("sta"), # ("sta $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
0xa0: ImmediateAmbiguous("ldy", "x8"), # (     ("ldy #$%.2x              ", op8) if x8 else ("ldy #$%.4x            ", op16)),
0xa1: DPXInd("lda"), # ("lda ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0xa2: ImmediateAmbiguous("ldx", "x8"), # (     ("ldx #$%.2x              ", op8) if x8 else ("ldx #$%.4x            ", op16)),
0xa3: StackRelative("lda"), # ("lda $%.2x,s     [%.6x]", op8, decode(OPTYPE_SR, op8)),
0xa4: DirectPage("ldy"), # ("ldy $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xa5: DirectPage("lda"), # ("lda $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xa6: DirectPage("ldx"), # ("ldx $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xa7: DPIndLong("lda"), # ("lda [$%.2x]     [%.6x]", op8, decode(OPTYPE_ILDP, op8)),
0xa8: Implied("tay"), # ("tay                   "),
0xa9: ImmediateAmbiguous("lda", "a8"), # (     ("lda #$%.2x              ", op8) if a8 else ("lda #$%.4x            ", op16)),
0xaa: Implied("tax"), # ("tax                   "),
0xab: PLB("plb"), # ("plb                   "),
0xac: Absolute("ldy"), # ("ldy $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xad: Absolute("lda"), # ("lda $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xae: Absolute("ldx"), # ("ldx $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xaf: AbsLong("lda"), # ("lda $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0xb0: BranchCond("bcs"), # ("bcs $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0xb1: DPIndY("lda"), # ("lda ($%.2x),y   [%.6x]", op8, decode(OPTYPE_IDPY, op8)),
0xb2: DPInd("lda"), # ("lda ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0xb3: StackRelativeIndY("lda"), # ("lda ($%.2x,s),y [%.6x]", op8, decode(OPTYPE_ISRY, op8)),
0xb4: DirectPageX("ldy"), # ("ldy $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0xb5: DirectPageX("lda"), # ("lda $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0xb6: DirectPageY("ldx"), # ("ldx $%.2x,y     [%.6x]", op8, decode(OPTYPE_DPY, op8)),
0xb7: DPIndLongY("lda"), # ("lda [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0xb8: Implied("clv", default_comment="Clear overflow"), # ("clv                   "),
0xb9: AbsoluteY("lda"), # ("lda $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0xba: Implied("tsx"), # ("tsx                   "),
0xbb: Implied("tyx"), # ("tyx                   "),
0xbc: AbsoluteX("ldy"), # ("ldy $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0xbd: AbsoluteX("lda"), # ("lda $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0xbe: AbsoluteY("ldx"), # ("ldx $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0xbf: AbsLongX("lda"), # ("lda $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
0xc0: ImmediateAmbiguous("cpy", "x8"), # (     ("cpy #$%.2x              ", op8) if x8 else ("cpy #$%.4x            ", op16)),
0xc1: DPXInd("cmp"), # ("cmp ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0xc2: REP("rep"), # ("rep #$%.2x              ", op8),
0xc3: StackRelative("cmp"), # ("cmp $%.2x,s     [%.6x]", op8, decode(OPTYPE_SR, op8)),
0xc4: DirectPage("cpy"), # ("cpy $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xc5: DirectPage("cmp"), # ("cmp $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xc6: DirectPage("dec"), # ("dec $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xc7: DPIndLong("cmp"), # ("cmp [$%.2x]     [%.6x]", op8, decode(OPTYPE_ILDP, op8)),
0xc8: Implied("iny"), # ("iny                   "),
0xc9: ImmediateAmbiguous("cmp", "a8"), # (     ("cmp #$%.2x              ", op8) if a8 else ("cmp #$%.4x            ", op16)),
0xca: Implied("dex"), # ("dex                   "),
0xcb: Implied("wai", default_comment="Wait for external hw interrupt"), #("wai                   "),
0xcc: Absolute("cpy"), # ("cpy $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xcd: Absolute("cmp"), # ("cmp $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xce: Absolute("dec"), # ("dec $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xcf: AbsLong("cmp"), # ("cmp $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0xd0: BranchCond("bne"), # ("bne $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0xd1: DPIndY("cmp"), # ("cmp ($%.2x),y   [%.6x]", op8, decode(OPTYPE_IDPY, op8)),
0xd2: DPInd("cmp"), # ("cmp ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0xd3: StackRelativeIndY("cmp"), # ("cmp ($%.2x,s),y [%.6x]", op8, decode(OPTYPE_ISRY, op8)),
0xd4: PushEffectiveInd("pei", default_comment="Push 16b as per DP ind, TODO: validate"), # ("pei ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0xd5: DirectPageX("cmp"), # ("cmp $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0xd6: DirectPageX("dec"), # ("dec $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0xd7: DPIndLongY("cmp"), # ("cmp [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0xd8: Implied("cld", default_comment="Clear decimal mode"), # ("cld                   "),
0xd9: AbsoluteY("cmp"), # ("cmp $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0xda: Stack("phx"), # ("phx                   "),
0xdb: Implied("stp", default_comment="Stop CPU until reset"), # ("stp                   "),
0xdc: JumpAbsIndLong("jmp"), # ("jmp [$%.4x]   [%.6x]", op16, decode(OPTYPE_ILADDR, op16)),
0xdd: AbsoluteX("cmp"), # ("cmp $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0xde: AbsoluteX("dec"), # ("dec $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0xdf: AbsLongX("cmp"), # ("cmp $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
0xe0: ImmediateAmbiguous("cpx", "x8"), # (     ("cpx #$%.2x              ", op8) if x8 else ("cpx #$%.4x            ", op16)),
0xe1: DPXInd("sbc"), # ("sbc ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0xe2: SEP("sep"), # manual instruction list has a misprint, it's really sep ("sep #$%.2x              ", op8),
0xe3: StackRelative("sbc"), # ("sbc $%.2x,s     [%.6x]", op8, decode(OPTYPE_SR, op8)),
0xe4: DirectPage("cpx"), # manual instruction list has a misprint, it's really cpx. ("cpx $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xe5: DirectPage("sbc"), # ("sbc $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xe6: DirectPage("inc"), # ("inc $%.2x       [%.6x]", op8, decode(OPTYPE_DP, op8)),
0xe7: DPIndLong("sbc"), # ("sbc [$%.2x]     [%.6x]", op8, decode(OPTYPE_ILDP, op8)),
0xe8: Implied("inx"), # ("inx                   "),
0xe9: ImmediateAmbiguous("sbc", "a8"), # (     ("sbc #$%.2x              ", op8) if a8 else ("sbc #$%.4x            ", op16)),
0xea: Implied("nop"), # ("nop                   "),
0xeb: Implied("xba", default_comment="Swap B and A accs (hi/lo bytes)"), # ("xba                   "),
0xec: Absolute("cpx"), # ("cpx $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xed: Absolute("sbc"), # ("sbc $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xee: Absolute("inc"), # ("inc $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xef: AbsLong("sbc"), # ("sbc $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0xf0: BranchCond("beq"), # ("beq $%.4x     [%.6x]", uint16_t(decode(OPTYPE_RELB, op8)), decode(OPTYPE_RELB, op8)),
0xf1: DPIndY("sbc"), # ("sbc ($%.2x),y   [%.6x]", op8, decode(OPTYPE_IDPY, op8)),
0xf2: DPInd("sbc"), # ("sbc ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
0xf3: StackRelativeIndY("sbc"), # ("sbc ($%.2x,s),y [%.6x]", op8, decode(OPTYPE_ISRY, op8)),
0xf4: PushEffectiveAbs("pea", default_comment="Push 16b of data, TODO: validate"), # ("pea $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xf5: DirectPageX("sbc"), # ("sbc $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0xf6: DirectPageX("inc"), # ("inc $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0xf7: DPIndLongY("sbc"), # ("sbc [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0xf8: Implied("sed", default_comment="Set decimal mode"), # ("sed                   "),
0xf9: AbsoluteY("sbc"), # ("sbc $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0xfa: Stack("plx"), # ("plx                   "),
0xfb: XCE("xce"), # ("xce                   "),
0xfc: CallAbsXInd("jsr"), # ("jsr ($%.4x,x) [%.6x]", op16, decode(OPTYPE_IADDRX, op16)),
0xfd: AbsoluteX("sbc"), # ("sbc $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0xfe: AbsoluteX("inc"), # ("inc $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0xff: AbsLongX("sbc"), # ("sbc $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
}

def disassemble(addr, bus, state):
    original_addr = addr

    opcode = bus.read(addr); addr = increment_pc(addr)
    op0 = bus.read(addr); addr = increment_pc(addr)
    op1 = bus.read(addr); addr = increment_pc(addr)
    op2 = bus.read(addr)

    # We should be able to deal with this, but let's not bother unless
    # we actually see such code in the wild.
    if addr < original_addr:
        raise NotImplementedError(
            "Instruction at 0x{:06x} wraps off the end of this bank".format(
                original_addr))

    info = codes[opcode]
    disassembly = info.disassemble(original_addr, state, opcode, op0, op1, op2)
    return disassembly

def increment_pc(addr):
    """Increment the PC as the CPU would when executing instructions.

    CPU manual: "program segments cannot cross bank boundaries; if the program
    counter increments past $FFFF, it rolls over to $0000 without incrementing
    the program counter bank."
    """
    pbr = addr & 0xFF0000
    pc = (addr + 1) & 0x00FFFF
    return pbr | pc

"""Code adapted from the higan emulator.
See https://gitlab.com/higan/higan/tree/master/processor/wdc65816

Original code copyright byuu, and licensed under GPLv3 (see
https://byuu.org/emulation/higan/licensing).
"""
# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import dsnes
from dsnes import util


class InstructionType:
    def __init__(self, mnemonic, default_comment=None):
        self.mnemonic = mnemonic
        self.default_comment = default_comment

    def disassemble(self, addr, e, m, x, op0, op1, op2):
        raise NotImplementedError(
            "Not implemented for {}".format(self.__class__.__name__))

# Basic addressing modes.

class Immediate8(InstructionType):
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} #${:02x}".format(self.mnemonic, op8)

class ImmediateAmbiguous(InstructionType):
    def __init__(self, mnemonic, selector, default_comment=None):
        assert selector in ("a8", "x8")
        super().__init__(mnemonic, default_comment)
        self.selector = selector

    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        op16 = op0 | (op1 << 8)
        a8 = e or m
        x8 = e or x

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

class Absolute(InstructionType):
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} ${:04x}     [DBR:{:04x}]".format(self.mnemonic, op16, op16)

class AbsLong(InstructionType):
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op24 = op0 | (op1 << 8) | (op2 << 16)
        return "{} ${:06x}".format(self.mnemonic, op24)

class AbsLongX(InstructionType):
    """Absolute long, indexed by X."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op24 = op0 | (op1 << 8) | (op2 << 16)
        return "{} ${:06x},x [{:06x}]+x".format(self.mnemonic, op24, op24)

class AbsoluteX(InstructionType):
    """Absolute, indexed by X."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} ${:04x},x   [DBR:{:04X}]+x".format(self.mnemonic, op16, op16)

class AbsoluteY(InstructionType):
    """Absolute, indexed by Y."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} ${:04x},y   [DBR:{:04x}]+y".format(self.mnemonic, op16, op16)

class AbsXInd(InstructionType):
    """(Absolute, indexed by X) indirect."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} (${:04x},x) [PBR:{:04x}+x]".format(self.mnemonic, op16, op16)

class DirectPage(InstructionType):
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} ${:02x}        [00:DPR+{:02x}]".format(
            self.mnemonic, op8, op8)

class DirectPageX(InstructionType):
    """Direct Page, indexed by X."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} ${:02x},x      [00:DPR+{:02x}]+x".format(
            self.mnemonic, op8, op8)

class DirectPageY(InstructionType):
    """Direct Page, indexed by Y."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} ${:02x},y      [00:DPR+{:02x}]+y".format(
            self.mnemonic, op8, op8)

class DPInd(InstructionType):
    """Direct Page indirect."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} (${:02x})      [DBR:(00:DPR+{:02x})]".format(
            self.mnemonic, op8, op8)

class DPIndLong(InstructionType):
    """Direct Page indirect, long."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} [${:02x}]     [(00:DPR+{:02x})]".format(
            self.mnemonic, op8, op8)

class DPIndY(InstructionType):
    """(Direct Page indirect), indexed by Y."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} (${:02x}),y   [DBR:(00:DPR+{:02x})]+y".format(
            self.mnemonic, op8, op8)

class DPIndLongY(InstructionType):
    """(Direct Page indirect) long, indexed by Y."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} [${:02x}],y   [(00:DPR+{:02x})]+y".format(
            self.mnemonic, op8, op8)

class DPXInd(InstructionType):
    """(Direct Page, indexed by X) indirect."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} (${:02x},x)   [DBR:(00:DPR+{:02x}+x)]".format(
            self.mnemonic, op8, op8)

class BlockMove(InstructionType):
    """Move a block of memory."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        return "{} ${:02x},${:02x}".format(self.mnemonic, op1, op0)
        # TODO: could put additional info into this dasm.

class Implied(InstructionType):
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        return self.mnemonic

class Accumulator(Implied):
    """Currently as Implied, may need to do special case later."""
    pass

class Stack(Implied):
    """Currently as Implied, may need to do special case later."""
    pass

class StackRelative(InstructionType):
    """Stack pointer + offset."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} ${:02x},s      [00:SP+{:02x}]".format(
            self.mnemonic, op8, op8)

class StackRelativeIndY(InstructionType):
    """(Stack pointer + offset) indirect, indexed by Y."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        return "{} (${:02x},s),y [DBR:(SP+{:02x})]+y".format(
            self.mnemonic, op8, op8)

class PushEffectiveAbs(Absolute):
    """Push 16b of data to stack."""
    pass

class PushEffectiveInd(DPInd):
    """Push 16b from ((Direct Page + offset) indirect) to stack."""
    pass

class PushEffectiveRel(InstructionType):
    """Push 16b = (PC + offset) to stack."""
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op16 = op0 | (op1 << 8)
        return "{} ${:04x}      [PC+{:04x}]".format(self.mnemonic, op16, op16)

# Special cases, or derived from basic addressing modes.

class CallAbs(Absolute):
    pass

class CallAbsLong(AbsLong):
    pass

class CallAbsXInd(AbsXInd):
    pass

class ReturnInt(Stack):
    pass

class ReturnSub(Stack):
    pass

class ReturnSubLong(Stack):
    pass

class JumpAbs(Absolute):
    pass

class JumpAbsInd(InstructionType):
    """Jump to 16b address in (bank 0 + offset) indirect."""
    pass

class JumpAbsIndLong(InstructionType):
    """Jump to 24b address in (bank 0 + offset) indirect."""
    pass

class JumpAbsXInd(AbsXInd):
    pass

class JumpAbsLong(AbsLong):
    pass

class BranchCond(InstructionType):
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        op16 = op0 | (op1 << 8)
        op24 = op0 | (op1 << 8) | (op2 << 16)
        TODO

class BranchAlways(InstructionType):
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        target = (addr & 0xff0000) + (((addr & 0xffff) + 2) & 0xffff)
        target += util.s8_to_num(op8)
        return "{} ${:04x}     [{:06x}]".format(
            self.mnemonic, target & 0xFFFF, target)

class BranchAlwaysLong(InstructionType):
    def disassemble(self, addr, e, m, x, op0, op1, op2):
        op8 = op0
        op16 = op0 | (op1 << 8)
        op24 = op0 | (op1 << 8) | (op2 << 16)
        TODO

class Interrupt(InstructionType):
    pass

class RFU(Implied):
    """Reserved for future use."""
    pass


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
0x18: Implied("clc"), # ("clc                   "),
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
0x28: Stack("plp"), # ("plp                   "),
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
0x38: Implied("sec"), # ("sec                   "),
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
0x58: Implied("cli", default_comment="Clear interrupt-disable"), # ("cli                   "),
0x59: AbsoluteY("eor"), # ("eor $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0x5a: Stack("phy"), # ("phy                   "),
0x5b: Implied("tcd", default_comment="Transfer 16b acc to DP reg"), # ("tcd                   "),
0x5c: JumpAbsLong("jml"), # ("jml $%.6x   [%.6x]", op24, decode(OPTYPE_LONG, op24)),
0x5d: AbsoluteX("eor"), # ("eor $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x5e: AbsoluteX("lsr"), # ("lsr $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0x5f: AbsLongX("eor"), # ("eor $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
0x60: ReturnSub("rts"), # ("rts                   "),
0x61: DPXInd("adc"), # ("adc ($%.2x,x)   [%.6x]", op8, decode(OPTYPE_IDPX, op8)),
0x62: PushEffectiveRel("per", default_comment="TODO"), # ("per $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
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
0x78: Implied("sei", default_comment="Set interrupt-disable"), # ("sei                   "),
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
0xab: Stack("plb"), # ("plb                   "),
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
0xc2: Immediate8("rep", default_comment="Reset status bits"), # ("rep #$%.2x              ", op8),
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
0xd4: PushEffectiveInd("pei", default_comment="TODO"), # ("pei ($%.2x)     [%.6x]", op8, decode(OPTYPE_IDP, op8)),
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
0xe2: Immediate8("sep", default_comment="Set status bits"), # ("sep #$%.2x              ", op8),
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
0xf4: PushEffectiveAbs("pea", default_comment="TODO"), # ("pea $%.4x     [%.6x]", op16, decode(OPTYPE_ADDR, op16)),
0xf5: DirectPageX("sbc"), # ("sbc $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0xf6: DirectPageX("inc"), # ("inc $%.2x,x     [%.6x]", op8, decode(OPTYPE_DPX, op8)),
0xf7: DPIndLongY("sbc"), # ("sbc [$%.2x],y   [%.6x]", op8, decode(OPTYPE_ILDPY, op8)),
0xf8: Implied("sed", default_comment="Set decimal mode"), # ("sed                   "),
0xf9: AbsoluteY("sbc"), # ("sbc $%.4x,y   [%.6x]", op16, decode(OPTYPE_ADDRY, op16)),
0xfa: Stack("plx"), # ("plx                   "),
0xfb: Implied("xce", default_comment="Exchange carry and emulation bits"), # ("xce                   "),
0xfc: CallAbsXInd("jsr"), # ("jsr ($%.4x,x) [%.6x]", op16, decode(OPTYPE_IADDRX, op16)),
0xfd: AbsoluteX("sbc"), # ("sbc $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0xfe: AbsoluteX("inc"), # ("inc $%.4x,x   [%.6x]", op16, decode(OPTYPE_ADDRX, op16)),
0xff: AbsLongX("sbc"), # ("sbc $%.6x,x [%.6x]", op24, decode(OPTYPE_LONGX, op24)),
}

class Disassembler:
    def __init__(self, project):
        self.bus = project.bus

    def disassemble(self, addr, e=None, m=None, x=None):
        original_addr = addr
        addr_str = "{:06x}".format(addr)

        op = self.bus.read(addr); addr = increment_pc(addr)
        op0 = self.bus.read(addr); addr = increment_pc(addr)
        op1 = self.bus.read(addr); addr = increment_pc(addr)
        op2 = self.bus.read(addr)

        # We should be able to deal with this, but let's not bother unless
        # we actually see such code in the wild.
        if addr < original_addr:
            raise NotImplementedError(
                "Instruction at 0x{:06x} wraps off the end of this bank".format(
                    original_addr))

        op8 = op0
        op16 = op0 | (op1 << 8)
        op24 = op0 | (op1 << 8) | (op2 << 16)
        if e is None or m is None:
            a8 = "unknown"
        else:
            a8 = e or m
        if e is None or x is None:
            x8 = "unknown"
        else:
            x8 = e or x

        info = codes[op]
        asm_str = info.disassemble(original_addr, e, m, x, op0, op1, op2)
        return asm_str

def increment_pc(addr):
    """Increment the PC as the CPU would when executing instructions.

    CPU manual: "program segments cannot cross bank boundaries; if the program
    counter increments past $FFFF, it rolls over to $0000 without incrementing
    the program counter bank."
    """
    pbr = addr & 0xFF0000
    pc = (addr + 1) & 0x00FFFF
    return pbr | pc
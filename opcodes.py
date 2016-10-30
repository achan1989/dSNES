import collections
import types


class BaseInstruction():
    # The following class variables will be available (will be set by child
    # classes, access as self._Blah):
    # _Opcode
    # _Mnemonic
    # _Category
    # _Operand_size

    def __init__(self, mem, address):
        self._address = address
        self._operands = self._get_operands(mem)

    def __str__(self):
        return "{}@0x{:04X}".format(self.mnemonic, self.address)

    def _get_operands(self, mem):
        """ Get the operands for this instruction. """
        address = self._address
        num_operands = self._Operand_size
        operands = tuple()

        while num_operands > 0:
            address += 1
            operands += (mem[address],)
            num_operands -= 1
        return operands

    @property
    def opcode(self):
        return self._Opcode

    @property
    def mnemonic(self):
        return self._Mnemonic

    @property
    def category(self):
        return self._Category

    @property
    def size(self):
        return 1 + self._Operand_size

    @property
    def operands(self):
        return self._operands

    @property
    def address(self):
        return self._address

    @property
    def assembly_string(self):
        operands = "[{} operand bytes todo]".format(self._Operand_size)
        return " ".join((self._Mnemonic, operands))

    @property
    def is_conditional_jump(self):
        return type(self) in conditional_jump_classes

    @property
    def is_unconditional_jump(self):
        return type(self) in unconditional_jump_classes

    @property
    def is_function_call(self):
        return type(self) in function_call_classes

    @property
    def is_function_return(self):
        return type(self) in function_return_classes


category = types.SimpleNamespace(
    Absolute="Absolute",
    AbsoluteX="AbsoluteX",
    AbsoluteY="AbsoluteY",
    Accumulator="Accumulator",
    Direct="Direct",
    DirectIndirectY="DirectIndirectY",
    DirectX="DirectX",
    DirectXIndirect="DirectXIndirect",
    DirectY="DirectY",
    Illegal="Illegal",
    Immediate="Immediate",
    Implicit="Implicit",
    JmpAbsolute="JmpAbsolute",
    JmpAbsoluteIndirect="JmpAbsoluteIndirect",
    Relative="Relative",
    Ret="Ret"
    )


def make_instruction_class(opcode, mnemonic, category, operand_size):
    classname = "{}_{}_0x{:02X}".format(mnemonic, category, opcode)
    return type(classname, (BaseInstruction,),
        {
        "_Opcode" : opcode,
        "_Mnemonic" : mnemonic,
        "_Category" : category,
        "_Operand_size" : operand_size
        })


def Absolute(opcode, mnemonic):
    operand_size = 2
    return make_instruction_class(opcode, mnemonic, category.Absolute, operand_size)

def AbsoluteX(opcode, mnemonic):
    operand_size = 2
    return make_instruction_class(opcode, mnemonic, category.AbsoluteX, operand_size)

def AbsoluteY(opcode, mnemonic):
    operand_size = 2
    return make_instruction_class(opcode, mnemonic, category.AbsoluteY, operand_size)

def Accumulator(opcode, mnemonic):
    operand_size = 0
    return make_instruction_class(opcode, mnemonic, category.Accumulator, operand_size)

def Direct(opcode, mnemonic):
    operand_size = 1
    return make_instruction_class(opcode, mnemonic, category.Direct, operand_size)

def DirectIndirectY(opcode, mnemonic):
    operand_size = 1
    return make_instruction_class(opcode, mnemonic, category.DirectIndirectY, operand_size)

def DirectX(opcode, mnemonic):
    operand_size = 1
    return make_instruction_class(opcode, mnemonic, category.DirectX, operand_size)

def DirectXIndirect(opcode, mnemonic):
    operand_size = 1
    return make_instruction_class(opcode, mnemonic, category.DirectXIndirect, operand_size)

def DirectY(opcode, mnemonic):
    operand_size = 1
    return make_instruction_class(opcode, mnemonic, category.DirectY, operand_size)

def Illegal(opcode, mnemonic):
    operand_size = 0
    return make_instruction_class(opcode, mnemonic, category.Illegal, operand_size)

def Immediate(opcode, mnemonic):
    operand_size = 1
    return make_instruction_class(opcode, mnemonic, category.Immediate, operand_size)

def Implicit(opcode, mnemonic):
    operand_size = 0
    return make_instruction_class(opcode, mnemonic, category.Implicit, operand_size)

def JmpAbsolute(opcode, mnemonic):
    operand_size = 2
    return make_instruction_class(opcode, mnemonic, category.JmpAbsolute, operand_size)

def JmpAbsoluteIndirect(opcode, mnemonic):
    operand_size = 2
    return make_instruction_class(opcode, mnemonic, category.JmpAbsoluteIndirect, operand_size)

def Relative(opcode, mnemonic):
    operand_size = 1
    return make_instruction_class(opcode, mnemonic, category.Relative, operand_size)

def Ret(opcode, mnemonic):
    operand_size = 0
    return make_instruction_class(opcode, mnemonic, category.Ret, operand_size)


opcode_table = [
    Implicit(0x00, "BRK"),
    DirectXIndirect(0x01, "ORA"),
    Illegal(0x02, "???"),
    Illegal(0x03, "???"),
    Illegal(0x04, "???"),
    Direct(0x05, "ORA"),
    Direct(0x06, "ASL"),
    Illegal(0x07, "???"),
    Implicit(0x08, "PHP"),
    Immediate(0x09, "ORA"),
    Accumulator(0x0a, "ASL"),
    Illegal(0x0b, "???"),
    Illegal(0x0c, "???"),
    Absolute(0x0d, "ORA"),
    Absolute(0x0e, "ASL"),
    Illegal(0x0f, "???"),
    Relative(0x10, "BPL"),
    DirectIndirectY(0x11, "ORA"),
    Illegal(0x12, "???"),
    Illegal(0x13, "???"),
    Illegal(0x14, "???"),
    DirectX(0x15, "ORA"),
    DirectX(0x16, "ASL"),
    Illegal(0x17, "???"),
    Implicit(0x18, "CLC"),
    AbsoluteY(0x19, "ORA"),
    Illegal(0x1a, "???"),
    Illegal(0x1b, "???"),
    Illegal(0x1c, "???"),
    AbsoluteX(0x1d, "ORA"),
    AbsoluteX(0x1e, "ASL"),
    Illegal(0x1f, "???"),
    JmpAbsolute(0x20, "JSR"),
    DirectXIndirect(0x21, "AND"),
    Illegal(0x22, "???"),
    Illegal(0x23, "???"),
    Direct(0x24, "BIT"),
    Direct(0x25, "AND"),
    Direct(0x26, "ROL"),
    Illegal(0x27, "???"),
    Implicit(0x28, "PLP"),
    Immediate(0x29, "AND"),
    Accumulator(0x2a, "ROL"),
    Illegal(0x2b, "???"),
    Absolute(0x2c, "BIT"),
    Absolute(0x2d, "AND"),
    Absolute(0x2e, "ROL"),
    Illegal(0x2f, "???"),
    Relative(0x30, "BMI"),
    DirectIndirectY(0x31, "AND"),
    Illegal(0x32, "???"),
    Illegal(0x33, "???"),
    Illegal(0x34, "???"),
    DirectX(0x35, "AND"),
    DirectX(0x36, "ROL"),
    Illegal(0x37, "???"),
    Implicit(0x38, "SEC"),
    AbsoluteY(0x39, "AND"),
    Illegal(0x3a, "???"),
    Illegal(0x3b, "???"),
    Illegal(0x3c, "???"),
    AbsoluteX(0x3d, "AND"),
    AbsoluteX(0x3e, "ROL"),
    Illegal(0x3f, "???"),
    Ret(0x40, "RTI"),
    DirectXIndirect(0x41, "EOR"),
    Illegal(0x42, "???"),
    Illegal(0x43, "???"),
    Illegal(0x44, "???"),
    Direct(0x45, "EOR"),
    Direct(0x46, "LSR"),
    Illegal(0x47, "???"),
    Implicit(0x48, "PHA"),
    Immediate(0x49, "EOR"),
    Accumulator(0x4a, "LSR"),
    Illegal(0x4b, "???"),
    JmpAbsolute(0x4c, "JMP"),
    Absolute(0x4d, "EOR"),
    Absolute(0x4e, "LSR"),
    Illegal(0x4f, "???"),
    Relative(0x50, "BVC"),
    DirectIndirectY(0x51, "EOR"),
    Illegal(0x52, "???"),
    Illegal(0x53, "???"),
    Illegal(0x54, "???"),
    DirectX(0x55, "EOR"),
    DirectX(0x56, "LSR"),
    Illegal(0x57, "???"),
    Implicit(0x58, "CLI"),
    AbsoluteY(0x59, "EOR"),
    Illegal(0x5a, "???"),
    Illegal(0x5b, "???"),
    Illegal(0x5c, "???"),
    AbsoluteX(0x5d, "EOR"),
    AbsoluteX(0x5e, "LSR"),
    Illegal(0x5f, "???"),
    Ret(0x60, "RTS"),
    DirectXIndirect(0x61, "ADC"),
    Illegal(0x62, "???"),
    Illegal(0x63, "???"),
    Illegal(0x64, "???"),
    Direct(0x65, "ADC"),
    Direct(0x66, "ROR"),
    Illegal(0x67, "???"),
    Implicit(0x68, "PLA"),
    Immediate(0x69, "ADC"),
    Accumulator(0x6a, "ROR"),
    Illegal(0x6b, "???"),
    JmpAbsoluteIndirect(0x6c, "JMP"),
    Absolute(0x6d, "ADC"),
    Absolute(0x6e, "ROR"),
    Illegal(0x6f, "???"),
    Relative(0x70, "BVS"),
    DirectIndirectY(0x71, "ADC"),
    Illegal(0x72, "???"),
    Illegal(0x73, "???"),
    Illegal(0x74, "???"),
    DirectX(0x75, "ADC"),
    DirectX(0x76, "ROR"),
    Illegal(0x77, "???"),
    Implicit(0x78, "SEI"),
    AbsoluteY(0x79, "ADC"),
    Illegal(0x7a, "???"),
    Illegal(0x7b, "???"),
    Illegal(0x7c, "???"),
    AbsoluteX(0x7d, "ADC"),
    AbsoluteX(0x7e, "ROR"),
    Illegal(0x7f, "???"),
    Illegal(0x80, "???"),
    DirectXIndirect(0x81, "STA"),
    Illegal(0x82, "???"),
    Illegal(0x83, "???"),
    Direct(0x84, "STY"),
    Direct(0x85, "STA"),
    Direct(0x86, "STX"),
    Illegal(0x87, "???"),
    Implicit(0x88, "DEY"),
    Illegal(0x89, "???"),
    Implicit(0x8a, "TXA"),
    Illegal(0x8b, "???"),
    Absolute(0x8c, "STY"),
    Absolute(0x8d, "STA"),
    Absolute(0x8e, "STX"),
    Illegal(0x8f, "???"),
    Relative(0x90, "BCC"),
    DirectIndirectY(0x91, "STA"),
    Illegal(0x92, "???"),
    Illegal(0x93, "???"),
    DirectX(0x94, "STY"),
    DirectX(0x95, "STA"),
    DirectY(0x96, "STX"),
    Illegal(0x97, "???"),
    Implicit(0x98, "TYA"),
    AbsoluteY(0x99, "STA"),
    Implicit(0x9a, "TXS"),
    Illegal(0x9b, "???"),
    Illegal(0x9c, "???"),
    AbsoluteX(0x9d, "STA"),
    Illegal(0x9e, "???"),
    Illegal(0x9f, "???"),
    Immediate(0xa0, "LDY"),
    DirectXIndirect(0xa1, "LDA"),
    Immediate(0xa2, "LDX"),
    Illegal(0xa3, "???"),
    Direct(0xa4, "LDY"),
    Direct(0xa5, "LDA"),
    Direct(0xa6, "LDX"),
    Illegal(0xa7, "???"),
    Implicit(0xa8, "TAY"),
    Immediate(0xa9, "LDA"),
    Implicit(0xaa, "TAX"),
    Illegal(0xab, "???"),
    Absolute(0xac, "LDY"),
    Absolute(0xad, "LDA"),
    Absolute(0xae, "LDX"),
    Illegal(0xaf, "???"),
    Relative(0xb0, "BCS"),
    DirectIndirectY(0xb1, "LDA"),
    Illegal(0xb2, "???"),
    Illegal(0xb3, "???"),
    DirectX(0xb4, "LDY"),
    DirectX(0xb5, "LDA"),
    DirectY(0xb6, "LDX"),
    Illegal(0xb7, "???"),
    Implicit(0xb8, "CLV"),
    AbsoluteY(0xb9, "LDA"),
    Implicit(0xba, "TSX"),
    Illegal(0xbb, "???"),
    AbsoluteX(0xbc, "LDY"),
    AbsoluteX(0xbd, "LDA"),
    AbsoluteY(0xbe, "LDX"),
    Illegal(0xbf, "???"),
    Immediate(0xc0, "CPY"),
    DirectXIndirect(0xc1, "CMP"),
    Illegal(0xc2, "???"),
    Illegal(0xc3, "???"),
    Direct(0xc4, "CPY"),
    Direct(0xc5, "CMP"),
    Direct(0xc6, "DEC"),
    Illegal(0xc7, "???"),
    Implicit(0xc8, "INY"),
    Immediate(0xc9, "CMP"),
    Implicit(0xca, "DEX"),
    Illegal(0xcb, "???"),
    Absolute(0xcc, "CPY"),
    Absolute(0xcd, "CMP"),
    Absolute(0xce, "DEC"),
    Illegal(0xcf, "???"),
    Relative(0xd0, "BNE"),
    DirectIndirectY(0xd1, "CMP"),
    Illegal(0xd2, "???"),
    Illegal(0xd3, "???"),
    Illegal(0xd4, "???"),
    DirectX(0xd5, "CMP"),
    DirectX(0xd6, "DEC"),
    Illegal(0xd7, "???"),
    Implicit(0xd8, "CLD"),
    AbsoluteY(0xd9, "CMP"),
    Illegal(0xda, "???"),
    Illegal(0xdb, "???"),
    Illegal(0xdc, "???"),
    AbsoluteX(0xdd, "CMP"),
    AbsoluteX(0xde, "DEC"),
    Illegal(0xdf, "???"),
    Immediate(0xe0, "CPX"),
    DirectXIndirect(0xe1, "SBC"),
    Illegal(0xe2, "???"),
    Illegal(0xe3, "???"),
    Direct(0xe4, "CPX"),
    Direct(0xe5, "SBC"),
    Direct(0xe6, "INC"),
    Illegal(0xe7, "???"),
    Implicit(0xe8, "INX"),
    Immediate(0xe9, "SBC"),
    Implicit(0xea, "NOP"),
    Illegal(0xeb, "???"),
    Absolute(0xec, "CPX"),
    Absolute(0xed, "SBC"),
    Absolute(0xee, "INC"),
    Illegal(0xef, "???"),
    Relative(0xf0, "BEQ"),
    DirectIndirectY(0xf1, "SBC"),
    Illegal(0xf2, "???"),
    Illegal(0xf3, "???"),
    Illegal(0xf4, "???"),
    DirectX(0xf5, "SBC"),
    DirectX(0xf6, "INC"),
    Illegal(0xf7, "???"),
    Implicit(0xf8, "SED"),
    AbsoluteY(0xf9, "SBC"),
    Illegal(0xfa, "???"),
    Illegal(0xfb, "???"),
    Illegal(0xfc, "???"),
    AbsoluteX(0xfd, "SBC"),
    AbsoluteX(0xfe, "INC"),
    Illegal(0xff, "???")
]


def find_instructions(mnemonic=None, category=None):
    """
    Find instructions by mnemonic and/or category.
    """
    assert not (mnemonic is None and category is None)

    found = []
    for cls in opcode_table:
        if (mnemonic is not None) and (mnemonic != cls._Mnemonic):
            continue
        if (category is not None) and (category != cls._Category):
            continue
        found.append(cls)

    return found

def find_unique_instruction(mnemonic=None, category=None):
    found = find_instructions(mnemonic, category)
    assert len(found) == 1, "Expected one result, got {}".format(found)
    return found[0]


conditional_jump_classes = frozenset([
    find_unique_instruction("BCC"),
    find_unique_instruction("BCS"),
    find_unique_instruction("BEQ"),
    find_unique_instruction("BMI"),
    find_unique_instruction("BNE"),
    find_unique_instruction("BPL"),
    find_unique_instruction("BVC"),
    find_unique_instruction("BVS"),
    ])

unconditional_jump_classes = frozenset([
    find_unique_instruction("JMP", category.JmpAbsolute),
    find_unique_instruction("JMP", category.JmpAbsoluteIndirect),
    ])

function_call_classes = frozenset([
    find_unique_instruction("JSR")
    ])

function_return_classes = frozenset([
    find_unique_instruction("RTI"),
    find_unique_instruction("RTS")
    ])

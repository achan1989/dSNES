import opcodes
from util import dw_to_uint, tc_to_int


def format_absolute(instruction, symbols):
    return "{ins} ${ops:04X}".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_absolute_x(instruction, symbols):
    return "{ins} ${ops:04X},X".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_absolute_y(instruction, symbols):
    return "{ins} ${ops:04X},Y".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_accumulator(instruction, symbols):
    return "{ins} A".format(ins=instruction.mnemonic)

def format_direct(instruction, symbols):
    return "{ins} ${ops:02X}".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_direct_indirect_y(instruction, symbols):
    return "{ins} (${ops:02X}),Y".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_direct_x(instruction, symbols):
    return "{ins} ${ops:02X},X".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_direct_x_indirect(instruction, symbols):
    return "{ins} (${ops:02X},X)".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_direct_y(instruction, symbols):
    return "{ins} ${ops:02X},Y".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_illegal(instruction, symbols):
    return "??? ???"

def format_immediate(instruction, symbols):
    return "{ins} #${ops:02X}".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_implicit(instruction, symbols):
    return "{ins}".format(ins=instruction.mnemonic)

def format_jmp_absolute(instruction, symbols):
    return "{ins} ${ops:04X}".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_jmp_absolute_indirect(instruction, symbols):
    return "{ins} (${ops:04X})".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_relative(instruction, symbols):
    value = tc_to_int(instruction.operands[0])
    sign = "+" if value >= 0 else "-"
    return "{ins} {sign}${ops:02X}".format(
        ins=instruction.mnemonic,
        sign=sign,
        ops=value)

def format_ret(instruction, symbols):
    return "{ins}".format(ins=instruction.mnemonic)


category_formatters = {
    opcodes.category.Absolute : format_absolute,
    opcodes.category.AbsoluteX : format_absolute_x,
    opcodes.category.AbsoluteY : format_absolute_y,
    opcodes.category.Accumulator : format_accumulator,
    opcodes.category.Direct : format_direct,
    opcodes.category.DirectIndirectY : format_direct_indirect_y,
    opcodes.category.DirectX : format_direct_x,
    opcodes.category.DirectXIndirect : format_direct_x_indirect,
    opcodes.category.DirectY : format_direct_y,
    opcodes.category.Illegal : format_illegal,
    opcodes.category.Immediate : format_immediate,
    opcodes.category.Implicit : format_implicit,
    opcodes.category.JmpAbsolute : format_jmp_absolute,
    opcodes.category.JmpAbsoluteIndirect : format_jmp_absolute_indirect,
    opcodes.category.Relative : format_relative,
    opcodes.category.Ret : format_ret
}

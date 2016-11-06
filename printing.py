import opcodes
from util import dw_to_uint, tc_to_int


def format_absolute(instruction, symbols=None):
    return "{ins} ${ops:04X}".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_absolute_x(instruction, symbols=None):
    return "{ins} ${ops:04X},X".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_absolute_y(instruction, symbols=None):
    return "{ins} ${ops:04X},Y".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_accumulator(instruction, symbols=None):
    return "{ins} A".format(ins=instruction.mnemonic)

def format_direct(instruction, symbols=None):
    return "{ins} ${ops:02X}".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_direct_indirect_y(instruction, symbols=None):
    return "{ins} (${ops:02X}),Y".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_direct_x(instruction, symbols=None):
    return "{ins} ${ops:02X},X".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_direct_x_indirect(instruction, symbols=None):
    return "{ins} (${ops:02X},X)".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_direct_y(instruction, symbols=None):
    return "{ins} ${ops:02X},Y".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_illegal(instruction, symbols=None):
    return "??? ???"

def format_immediate(instruction, symbols=None):
    return "{ins} #${ops:02X}".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_implicit(instruction, symbols=None):
    return "{ins}".format(ins=instruction.mnemonic)

def format_jmp_absolute(instruction, symbols=None):
    return "{ins} ${ops:04X}".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_jmp_absolute_indirect(instruction, symbols=None):
    return "{ins} (${ops:04X})".format(
        ins=instruction.mnemonic,
        ops=dw_to_uint(instruction.operands))

def format_relative(instruction, symbols=None):
    value = tc_to_int(instruction.operands[0])
    sign = "+" if value >= 0 else "-"
    return "{ins} {sign}${ops:02X}".format(
        ins=instruction.mnemonic,
        sign=sign,
        ops=value)

def format_ret(instruction, symbols=None):
    return "{ins}".format(ins=instruction.mnemonic)

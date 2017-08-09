# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import opcodes
from util import dw_to_uint, tc_to_int


def format_absolute(instruction, symbols=None):
    format_string = "{ins} ${address:04X}"
    address = dw_to_uint(instruction.operands)
    label = None

    if symbols:
        label = symbols.get_label(address)
        if label:
            format_string = "{ins} {label}"

    return format_string.format(
        ins=instruction.mnemonic,
        address=address,
        label=label)

def format_absolute_x(instruction, symbols=None):
    format_string = "{ins} ${address:04X},X"
    address = dw_to_uint(instruction.operands)
    label = None

    if symbols:
        label = symbols.get_label(address)
        if label:
            format_string = "{ins} {label},X"

    return format_string.format(
        ins=instruction.mnemonic,
        address=address,
        label=label)

def format_absolute_y(instruction, symbols=None):
    format_string = "{ins} ${address:04X},Y"
    address = dw_to_uint(instruction.operands)
    label = None

    if symbols:
        label = symbols.get_label(address)
        if label:
            format_string = "{ins} {label},Y"

    return format_string.format(
        ins=instruction.mnemonic,
        address=address,
        label=label)

def format_accumulator(instruction, symbols=None):
    return "{ins} A".format(ins=instruction.mnemonic)

def format_zero_page(instruction, symbols=None):
    format_string = "{ins} ${address:02X}"
    address = instruction.operands[0]
    label = None

    if symbols:
        label = symbols.get_label(address)
        if label:
            format_string = "{ins} {label}"

    return format_string.format(
        ins=instruction.mnemonic,
        address=address,
        label=label)

def format_zero_page_indirect_y(instruction, symbols=None):
    format_string = "{ins} (${address:02X}),Y"
    address = instruction.operands[0]
    label = None

    if symbols:
        label = symbols.get_label(address)
        if label:
            format_string = "{ins} ({label}),Y"

    return format_string.format(
        ins=instruction.mnemonic,
        address=address,
        label=label)

def format_zero_page_x(instruction, symbols=None):
    format_string = "{ins} ${address:02X},X"
    address = instruction.operands[0]
    label = None

    if symbols:
        label = symbols.get_label(address)
        if label:
            format_string = "{ins} {label},X"

    return format_string.format(
        ins=instruction.mnemonic,
        address=address,
        label=label)

def format_zero_page_x_indirect(instruction, symbols=None):
    format_string = "{ins} (${address:02X},X)"
    address = instruction.operands[0]
    label = None

    if symbols:
        label = symbols.get_label(address)
        if label:
            format_string = "{ins} ({label},X)"

    return format_string.format(
        ins=instruction.mnemonic,
        address=address,
        label=label)

def format_zero_page_y(instruction, symbols=None):
    format_string = "{ins} ${address:02X},Y"
    address = instruction.operands[0]
    label = None

    if symbols:
        label = symbols.get_label(address)
        if label:
            format_string = "{ins} {label},Y"

    return format_string.format(
        ins=instruction.mnemonic,
        address=address,
        label=label)

def format_illegal(instruction, symbols=None):
    return "??? ???"

def format_immediate(instruction, symbols=None):
    return "{ins} #${ops:02X}".format(
        ins=instruction.mnemonic,
        ops=instruction.operands[0])

def format_implicit(instruction, symbols=None):
    return "{ins}".format(ins=instruction.mnemonic)

def format_jmp_absolute(instruction, symbols=None):
    format_string = "{ins} ${address:04X}"
    jmp_target = dw_to_uint(instruction.operands)
    label = None

    if symbols:
        label = symbols.get_label(jmp_target)
        if label:
            format_string = "{ins} {label}"

    return format_string.format(
        ins=instruction.mnemonic,
        address=jmp_target,
        label=label)

def format_jmp_absolute_indirect(instruction, symbols=None):
    format_string = "{ins} (${address:04X})"
    ind_target = dw_to_uint(instruction.operands)
    label = None

    if symbols:
        label = symbols.get_label(ind_target)
        if label:
            format_string = "{ins} ({label})"

    return format_string.format(
        ins=instruction.mnemonic,
        address=ind_target,
        label=label)

def format_relative(instruction, symbols=None):
    format_string = "{ins} ${offset:+02X}"
    offset = tc_to_int(instruction.operands[0])
    label = None

    if symbols:
        relative_base = instruction.address + instruction.size
        target = relative_base + offset
        label = symbols.get_label(target)
        if label:
            format_string = "{ins} {label}"

    return format_string.format(
        ins=instruction.mnemonic,
        offset=offset,
        label=label)

def format_ret(instruction, symbols=None):
    return "{ins}".format(ins=instruction.mnemonic)

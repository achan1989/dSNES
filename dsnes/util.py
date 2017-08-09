# Copyright 2017 Adrian Chan
# Licensed under GPLv3

def dw_to_uint(dw):
    assert len(dw) == 2
    lsb, msb = dw
    return (msb << 8) | lsb

def tc_to_int(value):
    """ Convert an 8-bit word of 2's complement into an int. """
    # Python has interpreted the value as an unsigned int.
    assert 0 <= value <= 0xFF
    sign = (value & (1 << 7))
    if sign != 0:
        value -= (1 << 8)
    return value

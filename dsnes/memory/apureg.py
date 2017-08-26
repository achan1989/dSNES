# Copyright 2017 Adrian Chan
# Licensed under GPLv3

reg_map = {
    # 2140 - 2143
    0x2140: "raAPUIO0",
    0x2141: "raAPUIO1",
    0x2142: "raAPUIO2",
    0x2143: "raAPUIO3",
}
# Sanity check.
assert len(reg_map.keys()) == 4
assert len(set(reg_map.values())) == 4

map_to_banks = ((0, 0x3f), (0x80, 0xbf))
map_to_addresses = ((0x2140, 0x217f), )

def get_label(addr):
    pc = addr & 0xFFFF
    return reg_map.get(pc, "INVALID_APU_REG")

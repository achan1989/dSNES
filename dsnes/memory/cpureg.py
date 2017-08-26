# Copyright 2017 Adrian Chan
# Licensed under GPLv3

reg_map = {
    # 2180 - 2183
    0x2180: "rcWMDATA",
    0x2181: "rcWMADDL",
    0x2182: "rcWMADDM",
    0x2183: "rcWMADDH",
    # 4016 - 4017
    0x4016: "rcJOYA",
    0x4017: "rcJOYB",
    # 4200 - 420d
    0x4200: "rcNMITIMEN",
    0x4201: "rcWRIO",
    0x4202: "rcWRMPYA",
    0x4203: "rcWRMPYB",
    0x4204: "rcWRDIVL",
    0x4205: "rcWRDIVH",
    0x4206: "rcWRDIVB",
    0x4207: "rcHTIMEL",
    0x4208: "rcHTIMEH",
    0x4209: "rcVTIMEL",
    0x420a: "rcVTIMEH",
    0x420b: "rcDMAEN",
    0x420c: "rcHDMAEN",
    0x420d: "rcMEMSEL",
    # 4210 - 421f
    0x4210: "rcRDNMI",
    0x4211: "rcTIMEUP",
    0x4212: "rcHVBJOY",
    0x4213: "rcRDIO",
    0x4214: "rcRDDIVL",
    0x4215: "rcRDDIVH",
    0x4216: "rcRDMPYL",
    0x4217: "rcRDMPYH",
    0x4218: "rcJOY1L",
    0x4219: "rcJOY1H",
    0x421a: "rcJOY2L",
    0x421b: "rcJOY2H",
    0x421c: "rcJOY3L",
    0x421d: "rcJOY3H",
    0x421e: "rcJOY4L",
    0x421f: "rcJOY4H",
}

map_to_banks = ((0, 0x3f), (0x80, 0xbf))
map_to_addresses = ((0x2180, 0x2183), (0x4016, 0x4017), (0x4200, 0x421f))

def get_label(addr):
    pc = addr & 0xFFFF
    return reg_map.get(pc, "INVALID_CPU_REG")

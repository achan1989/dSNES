# Copyright 2017 Adrian Chan
# Licensed under GPLv3

reg_map = {
    # Channel 0, 4300 - 430a
    0x4300: "rdDMAP0",
    0x4301: "rdBBAD0",
    0x4302: "rdA1T0L",
    0x4303: "rdA1T0H",
    0x4304: "rdA1B0",
    0x4305: "rdDAS0L",
    0x4306: "rdDAS0H",
    0x4307: "rdDASB0",
    0x4308: "rdA2A0L",
    0x4309: "rdA2A0H",
    0x430a: "rdNTRL0",
    # Channel 1, 4310 - 431a
    0x4310: "rdDMAP1",
    0x4311: "rdBBAD1",
    0x4312: "rdA1T1L",
    0x4313: "rdA1T1H",
    0x4314: "rdA1B1",
    0x4315: "rdDAS1L",
    0x4316: "rdDAS1H",
    0x4317: "rdDASB1",
    0x4318: "rdA2A1L",
    0x4319: "rdA2A1H",
    0x431a: "rdNTRL1",
    # Channel 2, 4320 - 432a
    0x4320: "rdDMAP2",
    0x4321: "rdBBAD2",
    0x4322: "rdA1T2L",
    0x4323: "rdA1T2H",
    0x4324: "rdA1B2",
    0x4325: "rdDAS2L",
    0x4326: "rdDAS2H",
    0x4327: "rdDASB2",
    0x4328: "rdA2A2L",
    0x4329: "rdA2A2H",
    0x432a: "rdNTRL2",
    # Channel 3, 4330 - 433a
    0x4330: "rdDMAP3",
    0x4331: "rdBBAD3",
    0x4332: "rdA1T3L",
    0x4333: "rdA1T3H",
    0x4334: "rdA1B3",
    0x4335: "rdDAS3L",
    0x4336: "rdDAS3H",
    0x4337: "rdDASB3",
    0x4338: "rdA2A3L",
    0x4339: "rdA2A3H",
    0x433a: "rdNTRL3",
    # Channel 4, 4340 - 434a
    0x4340: "rdDMAP4",
    0x4341: "rdBBAD4",
    0x4342: "rdA1T4L",
    0x4343: "rdA1T4H",
    0x4344: "rdA1B4",
    0x4345: "rdDAS4L",
    0x4346: "rdDAS4H",
    0x4347: "rdDASB4",
    0x4348: "rdA2A4L",
    0x4349: "rdA2A4H",
    0x434a: "rdNTRL4",
    # Channel 5, 4350 - 435a
    0x4350: "rdDMAP5",
    0x4351: "rdBBAD5",
    0x4352: "rdA1T5L",
    0x4353: "rdA1T5H",
    0x4354: "rdA1B5",
    0x4355: "rdDAS5L",
    0x4356: "rdDAS5H",
    0x4357: "rdDASB5",
    0x4358: "rdA2A5L",
    0x4359: "rdA2A5H",
    0x435a: "rdNTRL5",
    # Channel 6, 4360 - 436a
    0x4360: "rdDMAP6",
    0x4361: "rdBBAD6",
    0x4362: "rdA1T6L",
    0x4363: "rdA1T6H",
    0x4364: "rdA1B6",
    0x4365: "rdDAS6L",
    0x4366: "rdDAS6H",
    0x4367: "rdDASB6",
    0x4368: "rdA2A6L",
    0x4369: "rdA2A6H",
    0x436a: "rdNTRL6",
    # Channel 7, 4370 - 437a
    0x4370: "rdDMAP7",
    0x4371: "rdBBAD7",
    0x4372: "rdA1T7L",
    0x4373: "rdA1T7H",
    0x4374: "rdA1B7",
    0x4375: "rdDAS7L",
    0x4376: "rdDAS7H",
    0x4377: "rdDASB7",
    0x4378: "rdA2A7L",
    0x4379: "rdA2A7H",
    0x437a: "rdNTRL7",
}
# Sanity check.
assert len(reg_map.keys()) == 88
assert len(set(reg_map.values())) == 88

map_to_banks = ((0, 0x3f), (0x80, 0xbf))
map_to_addresses = ((0x4300, 0x437f), )

def get_label(addr):
    pc = addr & 0xFFFF
    return reg_map.get(pc, "INVALID_DMA_REG")

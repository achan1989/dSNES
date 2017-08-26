# Copyright 2017 Adrian Chan
# Licensed under GPLv3

reg_map = {
    # 3000 - 303F
    0x3000: "grR0L/src/dest",
    0x3001: "grR0H/src/dest",
    0x3002: "grR1L/PLOTx",
    0x3003: "grR1H/PLOTx",
    0x3004: "grR2L/PLOTy",
    0x3005: "grR2H/PLOTy",
    0x3006: "grR3L",
    0x3007: "grR3H",
    0x3008: "grR4L/MULTres",
    0x3009: "grR4H/MULTres",
    0x300a: "grR5L",
    0x300b: "grR5H",
    0x300c: "grR6L/MULT",
    0x300d: "grR6H/MULT",
    0x300e: "grR7L/MERGE",
    0x300f: "grR7H/MERGE",
    0x3010: "grR8L/MERGE",
    0x3011: "grR8H/MERGE",
    0x3012: "grR9L",
    0x3013: "grR9H",
    0x3014: "grR10L/sp",
    0x3015: "grR10H/sp",
    0x3016: "grR11L/LINKdst",
    0x3017: "grR11H/LINKdst",
    0x3018: "grR12L/LOOPcnt",
    0x3019: "grR12H/LOOPcnt",
    0x301a: "grR13L/LOOPadr",
    0x301b: "grR13H/LOOPadr",
    0x301c: "grR14L/GETadr",
    0x301d: "grR14H/GETadr",
    0x301e: "grR15L/pc/GO",
    0x301f: "grR15H/pc/GO",
    0x3030: "grSFRL",
    0x3031: "grSFRH",
    0x3033: "grBRAMR",
    0x3034: "grPBR",
    0x3036: "grROMBR",
    0x3037: "grCFGR",
    0x3038: "grSCBR",
    0x3039: "grCLSR",
    0x303a: "grSCMR",
    0x303b: "grVCR",
    0x303c: "grRAMBR",
    0x303e: "grCBRL",
    0x303f: "grCBRH",
}
# Sanity check.
assert len(reg_map.keys()) == 45
assert len(set(reg_map.values())) == 45

cache_ram_lo = 0x3100
cache_ram_hi = 0x32ff

def get_label(addr):
    pc = addr & 0xFFFF
    label = "INVALID_GSU_REG"
    reg = reg_map.get(pc, None)
    if reg:
        label = reg
    elif pc >= cache_ram_lo and pc <= cache_ram_hi:
        idx = pc - cache_ram_lo
        label = "grCACHE_{:x}".format(idx)

    return label

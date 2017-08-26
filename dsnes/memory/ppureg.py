# Copyright 2017 Adrian Chan
# Licensed under GPLv3

reg_map = {
    # Write-only, 2100 - 2133
    0x2100: "rpINIDISP",
    0x2101: "rpOBSEL",
    0x2102: "rpOAMADDL",
    0x2103: "rpOAMADDH",
    0x2104: "rpOAMDATA",
    0x2105: "rpBGMODE",
    0x2106: "rpMOSAIC",
    0x2107: "rpBG1SC",
    0x2108: "rpBG2SC",
    0x2109: "rpBG3SC",
    0x210a: "rpBG4SC",
    0x210b: "rpBG12NBA",
    0x210c: "rpBG34NBA",
    0x210d: "rpBG1HOFS",
    0x210e: "rpBG1VOFS",
    0x210f: "rpBG2HOFS",
    0x2110: "rpBG2VOFS",
    0x2111: "rpBG3HOFS",
    0x2112: "rpBG3VOFS",
    0x2113: "rpBG4HOFS",
    0x2114: "rpBG4VOFS",
    0x2115: "rpVMAIN",
    0x2116: "rpVMADDL",
    0x2117: "rpVMADDH",
    0x2118: "rpVMDATAL",
    0x2119: "rpVMDATAH",
    0x211a: "rpM7SEL",
    0x211b: "rpM7A",
    0x211c: "rpM7B",
    0x211d: "rpM7C",
    0x211e: "rpM7D",
    0x211f: "rpM7X",
    0x2120: "rpM7Y",
    0x2121: "rpCGADD",
    0x2122: "rpCGDATA",
    0x2123: "rpW12SEL",
    0x2124: "rpW34SEL",
    0x2125: "rpWOBJSEL",
    0x2126: "rpWH0",
    0x2127: "rpWH1",
    0x2128: "rpWH2",
    0x2129: "rpWH3",
    0x212a: "rpWBGLOG",
    0x212b: "rpWOBJLOG",
    0x212c: "rpTM",
    0x212d: "rpTS",
    0x212e: "rpTMW",
    0x212f: "rpTSW",
    0x2130: "rpCGWSEL",
    0x2131: "rpCGADSUB",
    0x2132: "rpCOLDATA",
    0x2133: "rpSETINI",
    # Read-only, 2134 - 213f
    0x2134: "rpMPYL",
    0x2135: "rpMPYM",
    0x2136: "rpMPYH",
    0x2137: "rpSLHV",
    0x2138: "rpRDOAM",
    0x2139: "rpRDVRAML",
    0x213a: "rpRDVRAMH",
    0x213b: "rpRDCGRAM",
    0x213c: "rpOPHCT",
    0x213d: "rpOPVCT",
    0x213e: "rpSTAT77",
    0x213f: "rpSTAT78",
}
# Sanity check.
assert len(reg_map.keys()) == 64
assert len(set(reg_map.values())) == 64

map_to_banks = ((0, 0x3f), (0x80, 0xbf))
map_to_addresses = ((0x2100, 0x213f), )

def get_label(addr):
    pc = addr & 0xFFFF
    return reg_map.get(pc, "INVALID_PPU_REG")

import dsnes
from dsnes import disassembler

project = dsnes.project.load("starfox")

dis = disassembler.Disassembler(project)
addresses = [0xff9c, 0xff96, 0xff97, 0xff98, 0x1fbdb1, 0x1fbdb2, 0x1fbdb3, 0x1fbdb4, 0x1fbdb6]
for address in addresses:
    print(dis.disassemble(address))

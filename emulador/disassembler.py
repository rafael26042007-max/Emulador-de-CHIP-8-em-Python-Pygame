# ===== DISASSEMBLER =====
# Traduz um opcode (ex: 0x6A2F) num texto que humano entende (ex: "V A = 2F").
# É o mesmo "decode" da CPU, só que em vez de executar, descreve.


def descrever(opcode):
    tipo = (opcode & 0xF000) >> 12
    x    = (opcode & 0x0F00) >> 8
    y    = (opcode & 0x00F0) >> 4
    n    =  opcode & 0x000F
    nn   =  opcode & 0x00FF
    nnn  =  opcode & 0x0FFF

    # ----- instruções com opcode fixo -----
    if opcode == 0x00E0:
        return "CLS"
    if opcode == 0x00EE:
        return "RET"

    # ----- pelo tipo (primeiro dígito) -----
    if tipo == 0x1:
        return f"JUMP {nnn:03X}"
    if tipo == 0x2:
        return f"CALL {nnn:03X}"
    if tipo == 0x3:
        return f"SKIP V{x:X} == {nn:02X}"
    if tipo == 0x4:
        return f"SKIP V{x:X} != {nn:02X}"
    if tipo == 0x5:
        return f"SKIP V{x:X} == V{y:X}"
    if tipo == 0x6:
        return f"V{x:X} = {nn:02X}"
    if tipo == 0x7:
        return f"V{x:X} += {nn:02X}"
    if tipo == 0x8:
        contas = {0x0: "=", 0x1: "|=", 0x2: "&=", 0x3: "^=",
                  0x4: "+=", 0x5: "-=", 0x7: "=-"}
        if n in contas:
            return f"V{x:X} {contas[n]} V{y:X}"
        if n == 0x6:
            return f"V{x:X} >>= 1"
        if n == 0xE:
            return f"V{x:X} <<= 1"
    if tipo == 0x9:
        return f"SKIP V{x:X} != V{y:X}"
    if tipo == 0xA:
        return f"I = {nnn:03X}"
    if tipo == 0xB:
        return f"JUMP {nnn:03X}+V0"
    if tipo == 0xC:
        return f"V{x:X} = RAND & {nn:02X}"
    if tipo == 0xD:
        return f"DRAW V{x:X},V{y:X} h={n}"
    if tipo == 0xE:
        if nn == 0x9E:
            return f"SKIP tecla V{x:X}"
        if nn == 0xA1:
            return f"SKIP !tecla V{x:X}"
    if tipo == 0xF:
        textos = {
            0x07: f"V{x:X} = DELAY",
            0x0A: f"V{x:X} = espera tecla",
            0x15: f"DELAY = V{x:X}",
            0x18: f"SOM = V{x:X}",
            0x1E: f"I += V{x:X}",
            0x29: f"I = fonte[V{x:X}]",
            0x33: f"BCD V{x:X}",
            0x55: f"salva V0..V{x:X}",
            0x65: f"carrega V0..V{x:X}",
        }
        if nn in textos:
            return textos[nn]

    return "???"   # não é instrução (provavelmente é desenho/dado)

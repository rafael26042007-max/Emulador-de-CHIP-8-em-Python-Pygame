# ===== CPU DO GAME BOY (SM83) =====
# Mesmo ciclo do CHIP-8: fetch → decode → execute.
# A diferença: são ~500 opcodes. Em vez de 500 "if", a gente usa um truque
# que os emuladores de Z80 usam: os bits do opcode SEGUEM UM PADRÃO.
#
#   opcode = xx yyy zzz   (em binário)
#     x = 2 bits de cima   → o "grupo" da instrução
#     y = 3 bits do meio   → geralmente o registrador de DESTINO (ou qual operação)
#     z = 3 bits de baixo  → geralmente o registrador de ORIGEM
#
#   ex: 0x78 = 01 111 000 → x=1 (LD r,r), y=7 (A), z=0 (B)  →  LD A, B
#
# Os registradores numerados de 0 a 7 seguem a ordem: B C D E H L (HL) A
# onde (HL) = "o byte da memória no endereço HL".

# ===== IMPORTS =====
from gameboy.registradores import Registradores, FLAG_Z, FLAG_N, FLAG_H, FLAG_C

# ===== CONSTANTES =====
NOMES_R = ("b", "c", "d", "e", "h", "l", None, "a")   # índice 6 = (HL), tratado à parte
REG_IF = 0xFF0F          # Interrupt Flag: quais interrupções estão pedindo atenção
REG_IE = 0xFFFF          # Interrupt Enable: quais estão permitidas
# vetores de interrupção: VBlank, LCD, Timer, Serial, Joypad
ENDERECOS_INTERRUPCAO = (0x40, 0x48, 0x50, 0x58, 0x60)


# ===== CLASSE CPU =====
class CPU:
    def __init__(self, memoria):
        self.mem = memoria
        self.reg = Registradores()
        self.ime = False          # Interrupt Master Enable: interrupções ligadas?
        self.ime_pendente = False # o EI só liga o IME depois da PRÓXIMA instrução
        self.parada = False       # HALT: dorme até chegar uma interrupção

    # ===== AJUDANTES DE MEMÓRIA =====
    def ler_byte_pc(self):
        valor = self.mem.ler(self.reg.pc)
        self.reg.pc = (self.reg.pc + 1) & 0xFFFF
        return valor

    def ler_word_pc(self):
        valor = self.mem.ler16(self.reg.pc)
        self.reg.pc = (self.reg.pc + 2) & 0xFFFF
        return valor

    def ler_signed_pc(self):
        # byte com sinal: 0x00-0x7F = 0 a 127 / 0x80-0xFF = -128 a -1
        valor = self.ler_byte_pc()
        return valor - 256 if valor > 127 else valor

    def push(self, valor):
        self.reg.sp = (self.reg.sp - 2) & 0xFFFF
        self.mem.escrever16(self.reg.sp, valor)

    def pop(self):
        valor = self.mem.ler16(self.reg.sp)
        self.reg.sp = (self.reg.sp + 2) & 0xFFFF
        return valor

    # ===== REGISTRADORES PELO NÚMERO (0 a 7) =====
    def get_r(self, i):
        if i == 6:
            return self.mem.ler(self.reg.hl)
        return getattr(self.reg, NOMES_R[i])

    def set_r(self, i, valor):
        valor &= 0xFF
        if i == 6:
            self.mem.escrever(self.reg.hl, valor)
        else:
            setattr(self.reg, NOMES_R[i], valor)

    # pares: rp = BC DE HL SP / rp2 = BC DE HL AF (usado no PUSH/POP)
    def get_rp(self, p):
        return (self.reg.bc, self.reg.de, self.reg.hl, self.reg.sp)[p]

    def set_rp(self, p, valor):
        valor &= 0xFFFF
        if p == 0:   self.reg.bc = valor
        elif p == 1: self.reg.de = valor
        elif p == 2: self.reg.hl = valor
        else:        self.reg.sp = valor

    def get_rp2(self, p):
        return (self.reg.bc, self.reg.de, self.reg.hl, self.reg.af)[p]

    def set_rp2(self, p, valor):
        if p == 3:
            self.reg.af = valor
        else:
            self.set_rp(p, valor)

    # condições: NZ, Z, NC, C
    def condicao(self, cc):
        if cc == 0: return not self.reg.flag(FLAG_Z)
        if cc == 1: return self.reg.flag(FLAG_Z)
        if cc == 2: return not self.reg.flag(FLAG_C)
        return self.reg.flag(FLAG_C)

    def set_flags(self, z, n, h, c):
        # None = "não mexe nessa flag"
        r = self.reg
        if z is not None: r.set_flag(FLAG_Z, z)
        if n is not None: r.set_flag(FLAG_N, n)
        if h is not None: r.set_flag(FLAG_H, h)
        if c is not None: r.set_flag(FLAG_C, c)

    # ===== ALU: as 8 contas com o registrador A =====
    # y: 0 ADD, 1 ADC, 2 SUB, 3 SBC, 4 AND, 5 XOR, 6 OR, 7 CP
    def alu(self, y, v):
        a = self.reg.a
        carry = 1 if self.reg.flag(FLAG_C) else 0

        if y == 0 or y == 1:                       # ADD / ADC
            c = carry if y == 1 else 0
            res = a + v + c
            self.set_flags((res & 0xFF) == 0, False,
                           (a & 0xF) + (v & 0xF) + c > 0xF, res > 0xFF)
            self.reg.a = res & 0xFF

        elif y == 2 or y == 3 or y == 7:           # SUB / SBC / CP
            c = carry if y == 3 else 0
            res = a - v - c
            self.set_flags((res & 0xFF) == 0, True,
                           (a & 0xF) - (v & 0xF) - c < 0, res < 0)
            if y != 7:                             # CP só compara, não guarda
                self.reg.a = res & 0xFF

        elif y == 4:                               # AND
            self.reg.a = a & v
            self.set_flags(self.reg.a == 0, False, True, False)
        elif y == 5:                               # XOR
            self.reg.a = a ^ v
            self.set_flags(self.reg.a == 0, False, False, False)
        else:                                      # OR
            self.reg.a = a | v
            self.set_flags(self.reg.a == 0, False, False, False)

    # ===== ROTAÇÕES E DESLOCAMENTOS (prefixo CB) =====
    # y: 0 RLC, 1 RRC, 2 RL, 3 RR, 4 SLA, 5 SRA, 6 SWAP, 7 SRL
    def rot(self, y, v):
        carry = 1 if self.reg.flag(FLAG_C) else 0
        if y == 0:   c = v >> 7;  res = (v << 1) | c
        elif y == 1: c = v & 1;   res = (v >> 1) | (c << 7)
        elif y == 2: c = v >> 7;  res = (v << 1) | carry
        elif y == 3: c = v & 1;   res = (v >> 1) | (carry << 7)
        elif y == 4: c = v >> 7;  res = v << 1
        elif y == 5: c = v & 1;   res = (v >> 1) | (v & 0x80)   # mantém o sinal
        elif y == 6: c = 0;       res = ((v & 0x0F) << 4) | (v >> 4)
        else:        c = v & 1;   res = v >> 1
        res &= 0xFF
        self.set_flags(res == 0, False, False, c == 1)
        return res

    # ===== INTERRUPÇÕES =====
    def tratar_interrupcoes(self):
        pendentes = self.mem.ler(REG_IF) & self.mem.ler(REG_IE) & 0x1F
        if not pendentes:
            return 0
        self.parada = False                # qualquer interrupção acorda do HALT
        if not self.ime:
            return 0
        for bit in range(5):               # a de número menor tem prioridade
            if pendentes & (1 << bit):
                self.ime = False
                self.mem.escrever(REG_IF, self.mem.ler(REG_IF) & ~(1 << bit))
                self.push(self.reg.pc)
                self.reg.pc = ENDERECOS_INTERRUPCAO[bit]
                return 20
        return 0

    # ===== UM PASSO: devolve quantos ciclos de clock gastou =====
    def passo(self):
        ciclos = self.tratar_interrupcoes()
        if ciclos:
            return ciclos
        if self.parada:
            return 4

        # o EI liga o IME só depois da instrução seguinte
        ligar_ime = self.ime_pendente
        self.ime_pendente = False

        opcode = self.ler_byte_pc()
        ciclos = self.executar(opcode)

        if ligar_ime:
            self.ime = True
        return ciclos

    # ===== DECODE + EXECUTE =====
    def executar(self, op):
        r = self.reg
        x, y, z = op >> 6, (op >> 3) & 7, op & 7
        p, q = y >> 1, y & 1

        # ----- x = 1: LD r, r  (e o HALT no meio) -----
        if x == 1:
            if op == 0x76:                           # HALT
                self.parada = True
                return 4
            self.set_r(y, self.get_r(z))
            return 8 if (y == 6 or z == 6) else 4

        # ----- x = 2: ALU A, r -----
        if x == 2:
            self.alu(y, self.get_r(z))
            return 8 if z == 6 else 4

        # ----- x = 0 -----
        if x == 0:
            if z == 0:
                if y == 0:                           # NOP
                    return 4
                if y == 1:                           # LD (nn), SP
                    self.mem.escrever16(self.ler_word_pc(), r.sp)
                    return 20
                if y == 2:                           # STOP (tratado como NOP)
                    self.ler_byte_pc()
                    return 4
                d = self.ler_signed_pc()             # JR d / JR cc, d
                if y == 3 or self.condicao(y - 4):
                    r.pc = (r.pc + d) & 0xFFFF
                    return 12
                return 8

            if z == 1:
                if q == 0:                           # LD rp, nn
                    self.set_rp(p, self.ler_word_pc())
                    return 12
                hl, v = r.hl, self.get_rp(p)         # ADD HL, rp
                res = hl + v
                self.set_flags(None, False, (hl & 0xFFF) + (v & 0xFFF) > 0xFFF, res > 0xFFFF)
                r.hl = res & 0xFFFF
                return 8

            if z == 2:
                endereco = (r.bc, r.de, r.hl, r.hl)[p]
                if q == 0:
                    self.mem.escrever(endereco, r.a)     # LD (rr), A
                else:
                    r.a = self.mem.ler(endereco)         # LD A, (rr)
                if p == 2: r.hl = (r.hl + 1) & 0xFFFF    # HL+
                if p == 3: r.hl = (r.hl - 1) & 0xFFFF    # HL-
                return 8

            if z == 3:                               # INC rp / DEC rp
                self.set_rp(p, self.get_rp(p) + (1 if q == 0 else -1))
                return 8

            if z == 4:                               # INC r
                v = self.get_r(y)
                res = (v + 1) & 0xFF
                self.set_r(y, res)
                self.set_flags(res == 0, False, (v & 0xF) == 0xF, None)
                return 12 if y == 6 else 4

            if z == 5:                               # DEC r
                v = self.get_r(y)
                res = (v - 1) & 0xFF
                self.set_r(y, res)
                self.set_flags(res == 0, True, (v & 0xF) == 0, None)
                return 12 if y == 6 else 4

            if z == 6:                               # LD r, n
                self.set_r(y, self.ler_byte_pc())
                return 12 if y == 6 else 8

            # z == 7: operações especiais no A
            a = r.a
            if y == 0:                               # RLCA
                c = a >> 7; r.a = ((a << 1) | c) & 0xFF
                self.set_flags(False, False, False, c == 1)
            elif y == 1:                             # RRCA
                c = a & 1; r.a = (a >> 1) | (c << 7)
                self.set_flags(False, False, False, c == 1)
            elif y == 2:                             # RLA
                c = a >> 7; r.a = ((a << 1) | int(r.flag(FLAG_C))) & 0xFF
                self.set_flags(False, False, False, c == 1)
            elif y == 3:                             # RRA
                c = a & 1; r.a = (a >> 1) | (int(r.flag(FLAG_C)) << 7)
                self.set_flags(False, False, False, c == 1)
            elif y == 4:                             # DAA: ajusta A pra decimal
                if not r.flag(FLAG_N):
                    if r.flag(FLAG_C) or a > 0x99:
                        a += 0x60; r.set_flag(FLAG_C, True)
                    if r.flag(FLAG_H) or (a & 0x0F) > 0x09:
                        a += 0x06
                else:
                    if r.flag(FLAG_C): a -= 0x60
                    if r.flag(FLAG_H): a -= 0x06
                r.a = a & 0xFF
                self.set_flags(r.a == 0, None, False, None)
            elif y == 5:                             # CPL: inverte os bits de A
                r.a = a ^ 0xFF
                self.set_flags(None, True, True, None)
            elif y == 6:                             # SCF: liga o carry
                self.set_flags(None, False, False, True)
            else:                                    # CCF: inverte o carry
                self.set_flags(None, False, False, not r.flag(FLAG_C))
            return 4

        # ----- x = 3 -----
        if z == 0:
            if y <= 3:                               # RET cc
                if self.condicao(y):
                    r.pc = self.pop()
                    return 20
                return 8
            if y == 4:                               # LDH (n), A
                self.mem.escrever(0xFF00 + self.ler_byte_pc(), r.a)
                return 12
            if y == 6:                               # LDH A, (n)
                r.a = self.mem.ler(0xFF00 + self.ler_byte_pc())
                return 12
            # y == 5: ADD SP, d   /   y == 7: LD HL, SP+d
            d = self.ler_signed_pc()
            sp = r.sp
            res = (sp + d) & 0xFFFF
            self.set_flags(False, False, (sp & 0xF) + (d & 0xF) > 0xF, (sp & 0xFF) + (d & 0xFF) > 0xFF)
            if y == 5:
                r.sp = res
                return 16
            r.hl = res
            return 12

        if z == 1:
            if q == 0:                               # POP rp2
                self.set_rp2(p, self.pop())
                return 12
            if p == 0:                               # RET
                r.pc = self.pop()
                return 16
            if p == 1:                               # RETI
                r.pc = self.pop()
                self.ime = True
                return 16
            if p == 2:                               # JP HL
                r.pc = r.hl
                return 4
            r.sp = r.hl                              # LD SP, HL
            return 8

        if z == 2:
            if y <= 3:                               # JP cc, nn
                endereco = self.ler_word_pc()
                if self.condicao(y):
                    r.pc = endereco
                    return 16
                return 12
            if y == 4:                               # LD (FF00+C), A
                self.mem.escrever(0xFF00 + r.c, r.a)
                return 8
            if y == 5:                               # LD (nn), A
                self.mem.escrever(self.ler_word_pc(), r.a)
                return 16
            if y == 6:                               # LD A, (FF00+C)
                r.a = self.mem.ler(0xFF00 + r.c)
                return 8
            r.a = self.mem.ler(self.ler_word_pc())   # LD A, (nn)
            return 16

        if z == 3:
            if y == 0:                               # JP nn
                r.pc = self.ler_word_pc()
                return 16
            if y == 1:                               # prefixo CB
                return self.executar_cb(self.ler_byte_pc())
            if y == 6:                               # DI
                self.ime = False
                self.ime_pendente = False
                return 4
            if y == 7:                               # EI
                self.ime_pendente = True
                return 4

        if z == 4 and y <= 3:                        # CALL cc, nn
            endereco = self.ler_word_pc()
            if self.condicao(y):
                self.push(r.pc)
                r.pc = endereco
                return 24
            return 12

        if z == 5:
            if q == 0:                               # PUSH rp2
                self.push(self.get_rp2(p))
                return 16
            if p == 0:                               # CALL nn
                endereco = self.ler_word_pc()
                self.push(r.pc)
                r.pc = endereco
                return 24

        if z == 6:                                   # ALU A, n
            self.alu(y, self.ler_byte_pc())
            return 8

        if z == 7:                                   # RST: CALL rápido pra y*8
            self.push(r.pc)
            r.pc = y * 8
            return 16

        # sobrou: os 11 opcodes que não existem no Game Boy
        raise RuntimeError(f"Opcode ilegal {op:02X} em {(r.pc - 1) & 0xFFFF:04X}")

    # ===== INSTRUÇÕES COM PREFIXO CB =====
    def executar_cb(self, op):
        x, y, z = op >> 6, (op >> 3) & 7, op & 7
        v = self.get_r(z)

        if x == 0:                                   # rotações / SWAP
            self.set_r(z, self.rot(y, v))
            return 16 if z == 6 else 8
        if x == 1:                                   # BIT y, r: testa um bit
            self.set_flags((v >> y) & 1 == 0, False, True, None)
            return 12 if z == 6 else 8
        if x == 2:                                   # RES y, r: desliga um bit
            self.set_r(z, v & ~(1 << y))
        else:                                        # SET y, r: liga um bit
            self.set_r(z, v | (1 << y))
        return 16 if z == 6 else 8
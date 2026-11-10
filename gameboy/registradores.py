# ===== REGISTRADORES DA CPU DO GAME BOY (SM83) =====
# 8 registradores de 8 bits: A, F, B, C, D, E, H, L
# Eles se juntam em PARES de 16 bits: AF, BC, DE, HL
#   ex: B = 0x12 e C = 0x34  →  BC = 0x1234
# O F é especial: guarda as FLAGS (avisos) nos 4 bits de cima:
#   bit 7 = Z (zero)   bit 6 = N (foi subtração)
#   bit 5 = H (meio vai-um)   bit 4 = C (vai-um / carry)

# ===== MÁSCARAS DAS FLAGS =====
FLAG_Z = 0x80
FLAG_N = 0x40
FLAG_H = 0x20
FLAG_C = 0x10


# ===== CLASSE REGISTRADORES =====
class Registradores:
    def __init__(self):
        # valores que o Game Boy original deixa depois da tela de boot
        self.a, self.f = 0x01, 0xB0
        self.b, self.c = 0x00, 0x13
        self.d, self.e = 0x00, 0xD8
        self.h, self.l = 0x01, 0x4D
        self.sp = 0xFFFE      # Stack Pointer: topo da pilha
        self.pc = 0x0100      # o jogo começa a rodar no 0x100

    # ----- pares de 16 bits (property = parece variável, mas é função) -----
    @property
    def bc(self):
        return (self.b << 8) | self.c

    @bc.setter
    def bc(self, valor):
        self.b, self.c = (valor >> 8) & 0xFF, valor & 0xFF

    @property
    def de(self):
        return (self.d << 8) | self.e

    @de.setter
    def de(self, valor):
        self.d, self.e = (valor >> 8) & 0xFF, valor & 0xFF

    @property
    def hl(self):
        return (self.h << 8) | self.l

    @hl.setter
    def hl(self, valor):
        self.h, self.l = (valor >> 8) & 0xFF, valor & 0xFF

    @property
    def af(self):
        return (self.a << 8) | self.f

    @af.setter
    def af(self, valor):
        # os 4 bits de baixo do F são sempre 0 no hardware
        self.a, self.f = (valor >> 8) & 0xFF, valor & 0xF0

    # ----- flags -----
    def flag(self, mascara):
        return (self.f & mascara) != 0

    def set_flag(self, mascara, ligada):
        if ligada:
            self.f |= mascara
        else:
            self.f &= ~mascara & 0xFF

    def __str__(self):
        flags = "".join(nome if self.flag(m) else "-"
                        for nome, m in (("Z", FLAG_Z), ("N", FLAG_N), ("H", FLAG_H), ("C", FLAG_C)))
        return (f"AF={self.af:04X} BC={self.bc:04X} DE={self.de:04X} HL={self.hl:04X} "
                f"SP={self.sp:04X} PC={self.pc:04X} [{flags}]")


# ===== TESTE =====
if __name__ == "__main__":
    from gameboy.cartucho import Cartucho
    from gameboy.memoria import Memoria

    reg = Registradores()
    print("Registradores no início:", reg)

    reg.bc = 0x1234
    print(f"BC = 0x1234  →  B = {reg.b:02X}, C = {reg.c:02X}")

    mem = Memoria(Cartucho("rom/gb/dmg-acid2.gb"))
    mem.escrever(0xC000, 0x42)
    print(f"Escrevi 42 na WRAM (C000). Lendo C000: {mem.ler(0xC000):02X} / lendo o eco E000: {mem.ler(0xE000):02X}")
    mem.escrever16(0xC010, 0xBEEF)
    print(f"Escrevi BEEF em C010 (16 bits). Byte C010 = {mem.ler(0xC010):02X}, C011 = {mem.ler(0xC011):02X}")
    print(f"Primeira instrução do jogo (em 0x100): {mem.ler(0x100):02X} {mem.ler(0x101):02X} {mem.ler(0x102):02X} {mem.ler(0x103):02X}")

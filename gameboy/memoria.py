# ===== MAPA DE MEMÓRIA DO GAME BOY =====
# A CPU enxerga 64 KB de endereços (0x0000 a 0xFFFF), mas cada faixa
# é uma peça diferente do console. O ler()/escrever() funciona como um
# carteiro: olha o "CEP" (endereço) e entrega no bairro certo.

# ===== CONSTANTES (início de cada faixa) =====
INICIO_VRAM = 0x8000
INICIO_RAM_CART = 0xA000   # RAM extra que alguns cartuchos têm (save)
INICIO_WRAM = 0xC000
INICIO_ECO = 0xE000        # "espelho" da WRAM (um defeito de hardware que virou regra)
INICIO_OAM = 0xFE00
INICIO_IO = 0xFF00
INICIO_HRAM = 0xFF80
REG_IE = 0xFFFF            # Interrupt Enable: quais interrupções estão ligadas


# ===== CLASSE MEMÓRIA =====
class Memoria:
    def __init__(self, cartucho):
        self.cartucho = cartucho
        self.vram = bytearray(8 * 1024)      # 0x8000-0x9FFF: desenhos da tela
        self.ram_cart = bytearray(8 * 1024)  # 0xA000-0xBFFF: RAM do cartucho
        self.wram = bytearray(8 * 1024)      # 0xC000-0xDFFF: RAM de trabalho
        self.oam = bytearray(160)            # 0xFE00-0xFE9F: 40 sprites × 4 bytes
        self.io = bytearray(128)             # 0xFF00-0xFF7F: botões, timers, som, tela
        self.hram = bytearray(127)           # 0xFF80-0xFFFE: RAM rápida
        self.ie = 0                          # 0xFFFF
        self.timer = None                    # o console liga o timer aqui
        self.serial = ""                     # texto mandado pelo cabo de link (os testes escrevem aqui!)

    # ----- LER: devolve o byte do endereço -----
    def ler(self, endereco):
        endereco &= 0xFFFF

        if 0x0000 <= endereco <= 0x7FFF:     # cartucho
            if endereco < len(self.cartucho.rom):
                return self.cartucho.rom[endereco]
            return 0xFF

        if endereco <= 0x9FFF:               # VRAM
            return self.vram[endereco - INICIO_VRAM]

        if endereco <= 0xBFFF:               # RAM do cartucho
            return self.ram_cart[endereco - INICIO_RAM_CART]

        if endereco <= 0xDFFF:               # WRAM
            return self.wram[endereco - INICIO_WRAM]

        if endereco <= 0xFDFF:               # eco: lê a WRAM
            return self.wram[endereco - INICIO_ECO]

        if endereco <= 0xFE9F:               # OAM
            return self.oam[endereco - INICIO_OAM]

        if endereco <= 0xFEFF:               # área proibida (não existe nada aqui)
            return 0xFF

        if endereco <= 0xFF7F:               # registradores de hardware
            if endereco == 0xFF0F:           # IF: os 3 bits de cima sempre leem 1
                return self.io[0x0F] | 0xE0
            return self.io[endereco - INICIO_IO]

        if endereco <= 0xFFFE:               # HRAM
            return self.hram[endereco - INICIO_HRAM]

        return self.ie                       # 0xFFFF

    # ----- ESCREVER: guarda o byte no endereço -----
    def escrever(self, endereco, valor):
        endereco &= 0xFFFF
        valor &= 0xFF

        if endereco <= 0x7FFF:
            # ROM não dá pra escrever. Nos cartuchos com MBC, escrever aqui
            # é um "comando" pro chip trocar de banco (fica pra depois)
            return

        if endereco <= 0x9FFF:
            self.vram[endereco - INICIO_VRAM] = valor
        elif endereco <= 0xBFFF:
            self.ram_cart[endereco - INICIO_RAM_CART] = valor
        elif endereco <= 0xDFFF:
            self.wram[endereco - INICIO_WRAM] = valor
        elif endereco <= 0xFDFF:
            self.wram[endereco - INICIO_ECO] = valor
        elif endereco <= 0xFE9F:
            self.oam[endereco - INICIO_OAM] = valor
        elif endereco <= 0xFEFF:
            pass                             # área proibida: ignora
        elif endereco <= 0xFF7F:
            if endereco == 0xFF04:           # escrever no DIV zera ele
                valor = 0
                if self.timer:
                    self.timer.conta_div = 0
            elif endereco == 0xFF02 and valor & 0x80:
                # cabo de link: o jogo mandou o byte do FF01. Os testes do Blargg
                # usam isso pra "imprimir" o resultado, então a gente guarda como texto
                self.serial += chr(self.io[0x01])
                valor &= 0x7F                # transferência concluída na hora
            self.io[endereco - INICIO_IO] = valor
        elif endereco <= 0xFFFE:
            self.hram[endereco - INICIO_HRAM] = valor
        else:
            self.ie = valor

    # ----- 16 bits: o Game Boy guarda o byte BAIXO primeiro (little-endian) -----
    def ler16(self, endereco):
        baixo = self.ler(endereco)
        alto = self.ler(endereco + 1)
        return (alto << 8) | baixo

    def escrever16(self, endereco, valor):
        self.escrever(endereco, valor & 0xFF)
        self.escrever(endereco + 1, valor >> 8)
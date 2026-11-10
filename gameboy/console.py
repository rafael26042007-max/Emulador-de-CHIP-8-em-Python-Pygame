# ===== O CONSOLE: junta as peças do Game Boy =====

# ===== IMPORTS =====
from gameboy.cartucho import Cartucho
from gameboy.memoria import Memoria
from gameboy.cpu import CPU
from gameboy.timer import Timer

# ===== CONSTANTES =====
LY = 0xFF44                  # linha da tela que está sendo desenhada (0 a 153)
CICLOS_POR_LINHA = 456
REG_IF = 0xFF0F


# ===== CLASSE GAMEBOY =====
class GameBoy:
    def __init__(self, caminho_rom):
        self.cartucho = Cartucho(caminho_rom)
        self.memoria = Memoria(self.cartucho)
        self.cpu = CPU(self.memoria)
        self.timer = Timer(self.memoria)
        self.memoria.timer = self.timer
        self.conta_linha = 0
        self.ciclos_total = 0

    def passo(self):
        ciclos = self.cpu.passo()
        self.timer.passo(ciclos)
        self.ciclos_total += ciclos

        # ----- "tela de mentira" por enquanto: só conta as linhas (LY) -----
        # muitos jogos esperam a tela chegar na linha 144 (VBlank) antes de continuar
        self.conta_linha += ciclos
        if self.conta_linha >= CICLOS_POR_LINHA:
            self.conta_linha -= CICLOS_POR_LINHA
            io = self.memoria.io
            ly = (io[LY - 0xFF00] + 1) % 154
            io[LY - 0xFF00] = ly
            if ly == 144:
                io[REG_IF - 0xFF00] |= 0x01      # pede interrupção de VBlank (bit 0)
        return ciclos

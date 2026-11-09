# ===== IMPORTS =====
import pygame

# ===== MAPA DE TECLAS =====
# Teclado do CHIP-8:     Seu teclado:
#   1 2 3 C                1 2 3 4
#   4 5 6 D                Q W E R
#   7 8 9 E                A S D F
#   A 0 B F                Z X C V
MAPA = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
}


# ===== CLASSE TECLADO =====
class Teclado:
    def __init__(self):
        # 16 teclas, todas soltas (False)
        self.teclas = [False] * 16

    # ----- recebe os eventos do pygame e marca apertada/solta -----
    def processar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in MAPA:
            self.teclas[MAPA[evento.key]] = True
        elif evento.type == pygame.KEYUP and evento.key in MAPA:
            self.teclas[MAPA[evento.key]] = False

    # ----- a tecla do CHIP-8 está apertada? -----
    def apertada(self, tecla):
        return self.teclas[tecla & 0xF]

    # ----- devolve a primeira tecla apertada, ou None -----
    def qualquer_apertada(self):
        for i, apertada in enumerate(self.teclas):
            if apertada:
                return i
        return None

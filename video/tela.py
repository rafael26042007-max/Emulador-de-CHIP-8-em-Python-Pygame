# ===== IMPORTS =====
import pygame

# ===== CONSTANTES =====
LARGURA = 64
ALTURA = 32
ESCALA = 10          # cada pixel do CHIP-8 vira um quadrado de 10x10 na janela
COR_LIGADO = (255, 255, 255)
COR_DESLIGADO = (0, 0, 0)


# ===== CLASSE TELA =====
class Tela:
    def __init__(self):
        # matriz 32 linhas x 64 colunas, tudo apagado (0)
        self.pixels = [[0] * LARGURA for _ in range(ALTURA)]

    # ----- limpar (instrução 00E0) -----
    def limpar(self):
        for linha in self.pixels:
            for i in range(LARGURA):
                linha[i] = 0

    # ----- desenhar sprite (instrução DXYN) -----
    def desenhar_sprite(self, x, y, sprite):
        colisao = False

        # cada byte do sprite é uma linha de 8 pixels
        for linha, byte in enumerate(sprite):
            for bit in range(8):
                # 0x80 = 10000000 → vai andando pra direita: 01000000, 00100000...
                if byte & (0x80 >> bit):
                    px = (x + bit) % LARGURA
                    py = (y + linha) % ALTURA

                    # se o pixel já estava aceso, vai apagar → isso é "colisão"
                    if self.pixels[py][px] == 1:
                        colisao = True

                    # XOR: inverte o pixel (0 vira 1, 1 vira 0)
                    self.pixels[py][px] ^= 1

        return colisao

    # ----- desenhar na janela do pygame -----
    def render(self, janela):
        janela.fill(COR_DESLIGADO)
        for y, linha in enumerate(self.pixels):
            for x, pixel in enumerate(linha):
                if pixel:
                    pygame.draw.rect(janela, COR_LIGADO,
                                     (x * ESCALA, y * ESCALA, ESCALA, ESCALA))
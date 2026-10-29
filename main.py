# ===== IMPORTS =====
import pygame
from emulador.memoria import Memoria
from emulador.cpu import CPU
from video.tela import Tela, LARGURA, ALTURA, ESCALA

# ===== CONSTANTES =====
INSTRUCOES_POR_FRAME = 10   # quantas instruções a CPU roda a cada quadro

# ===== EXECUÇÃO =====
if __name__ == "__main__":
    # ----- pygame -----
    pygame.init()
    janela = pygame.display.set_mode((LARGURA * ESCALA, ALTURA * ESCALA))
    pygame.display.set_caption("CHIP-8")
    relogio = pygame.time.Clock()

    # ----- emulador -----
    mem = Memoria()
    mem.carregar_rom("rom/3-corax+.ch8")
    tela = Tela()
    cpu = CPU(mem, tela)

    # ----- loop principal -----
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:   # clicou no X da janela
                rodando = False

        for _ in range(INSTRUCOES_POR_FRAME):
            cpu.ciclo()

        tela.render(janela)
        pygame.display.flip()
        relogio.tick(60)                     # 60 quadros por segundo

    pygame.quit()
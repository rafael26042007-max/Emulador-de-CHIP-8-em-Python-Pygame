# ===== IMPORTS =====
import pygame
from emulador.memoria import Memoria
from emulador.cpu import CPU
from video.tela import Tela, LARGURA, ALTURA, ESCALA
from entrada.teclado import Teclado
from audio.som import Som

# ===== CONSTANTES =====
INSTRUCOES_POR_FRAME = 10   # quantas instruções a CPU roda a cada quadro
ROM = "rom/3-corax+.ch8"    # troque aqui pra rodar outro jogo

# ===== EXECUÇÃO =====
if __name__ == "__main__":
    # ----- pygame -----
    pygame.init()
    janela = pygame.display.set_mode((LARGURA * ESCALA, ALTURA * ESCALA))
    pygame.display.set_caption("CHIP-8")
    relogio = pygame.time.Clock()

    # ----- emulador -----
    mem = Memoria()
    mem.carregar_rom(ROM)
    tela = Tela()
    teclado = Teclado()
    som = Som()
    cpu = CPU(mem, tela, teclado)

    # ----- loop principal -----
    rodando = True
    while rodando:
        # ----- eventos: fechar janela e teclado -----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:   # clicou no X da janela
                rodando = False
            teclado.processar_evento(evento)

        # ----- CPU: várias instruções por quadro -----
        for _ in range(INSTRUCOES_POR_FRAME):
            cpu.ciclo()

        # ----- timers e som: 1 vez por quadro (60x por segundo) -----
        cpu.atualizar_timers()
        som.atualizar(cpu.som)

        # ----- desenhar -----
        tela.render(janela)
        pygame.display.flip()
        relogio.tick(60)                     # 60 quadros por segundo

    pygame.quit()
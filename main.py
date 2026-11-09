# ===== IMPORTS =====
import pygame
from emulador.memoria import Memoria
from emulador.cpu import CPU
from video.tela import Tela, LARGURA, ALTURA, ESCALA
from video.debugger import Debugger, LARGURA_PAINEL
from entrada.teclado import Teclado
from audio.som import Som

# ===== CONSTANTES =====
INSTRUCOES_POR_FRAME = 10   # quantas instruções a CPU roda a cada quadro
ROM = "rom/pong9.ch8"        # troque aqui pra rodar outro jogo

# Atalhos do emulador (nenhum deles é tecla do CHIP-8):
#   TAB = mostra/esconde o debugger
#   P   = pausa / continua
#   N   = executa 1 instrução (só quando pausado)
#   F5  = reinicia o jogo
LARGURA_JOGO = LARGURA * ESCALA
ALTURA_JOGO = ALTURA * ESCALA


# ===== FUNÇÕES =====
def criar_janela(com_debugger):
    largura = LARGURA_JOGO + (LARGURA_PAINEL if com_debugger else 0)
    return pygame.display.set_mode((largura, ALTURA_JOGO))


def iniciar_emulador(teclado):
    # cria memória, tela e CPU do zero (usado no começo e no F5)
    mem = Memoria()
    mem.carregar_rom(ROM)
    tela = Tela()
    cpu = CPU(mem, tela, teclado)
    return tela, cpu


# ===== EXECUÇÃO =====
if __name__ == "__main__":
    # ----- pygame -----
    pygame.init()
    pygame.display.set_caption("CHIP-8")
    relogio = pygame.time.Clock()
    mostrar_debugger = False
    pausado = False
    janela = criar_janela(mostrar_debugger)

    # ----- emulador -----
    teclado = Teclado()
    som = Som()
    debugger = Debugger()
    tela, cpu = iniciar_emulador(teclado)

    # ----- loop principal -----
    rodando = True
    while rodando:
        passo = False   # N pede pra rodar só 1 instrução

        # ----- eventos: janela, atalhos e teclado do CHIP-8 -----
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:   # clicou no X da janela
                rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_TAB:
                    mostrar_debugger = not mostrar_debugger
                    janela = criar_janela(mostrar_debugger)
                elif evento.key == pygame.K_p:
                    pausado = not pausado
                elif evento.key == pygame.K_n and pausado:
                    passo = True
                elif evento.key == pygame.K_F5:
                    tela, cpu = iniciar_emulador(teclado)

            teclado.processar_evento(evento)

        # ----- CPU -----
        if not pausado:
            for _ in range(INSTRUCOES_POR_FRAME):
                cpu.ciclo()
            cpu.atualizar_timers()      # timers só andam com o jogo rodando
        elif passo:
            cpu.ciclo()

        # ----- som: desliga quando pausado -----
        som.atualizar(0 if pausado else cpu.som)

        # ----- desenhar -----
        tela.render(janela)
        if mostrar_debugger:
            debugger.render(janela, cpu, LARGURA_JOGO, pausado)
        pygame.display.flip()
        relogio.tick(60)                     # 60 quadros por segundo

    pygame.quit()
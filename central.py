# ===== CENTRAL DE JOGOS =====
# Lista os jogos da pasta rom/ e abre cada um no emulador certo.
#   ↑ ↓   = escolher
#   ENTER = jogar
#   ESC   = sair

# ===== IMPORTS =====
import subprocess
import pygame
from frontend.catalogo import carregar_consoles, listar_jogos, montar_comando
import os
import sys

# ===== CONSTANTES =====
LARGURA, ALTURA = 640, 480
LINHAS_VISIVEIS = 12
COR_FUNDO = (15, 15, 25)
COR_TITULO = (120, 200, 255)
COR_TEXTO = (200, 200, 200)
COR_SELECIONADO = (255, 220, 80)
COR_FAIXA = (40, 40, 60)
COR_ERRO = (255, 100, 100)
COR_DICA = (110, 110, 130)
CORES_CONSOLE = {"chip8": (120, 255, 140), "n64": (255, 120, 120)}


# ===== DESENHO =====
def desenhar(janela, fontes, jogos, consoles, selecionado, topo, mensagem, jogando):
    fonte, fonte_grande = fontes
    janela.fill(COR_FUNDO)

    # ----- título -----
    janela.blit(fonte_grande.render("CENTRAL DE JOGOS", True, COR_TITULO), (30, 20))

    # ----- lista -----
    if not jogos:
        janela.blit(fonte.render("Nenhum jogo na pasta rom/", True, COR_ERRO), (30, 90))

    y = 80
    for i in range(topo, min(topo + LINHAS_VISIVEIS, len(jogos))):
        jogo = jogos[i]
        if i == selecionado:
            pygame.draw.rect(janela, COR_FAIXA, (20, y - 3, LARGURA - 40, 28), border_radius=4)

        etiqueta = consoles[jogo["console"]]["nome"]
        cor_console = CORES_CONSOLE.get(jogo["console"], COR_TEXTO)
        janela.blit(fonte.render(f"[{etiqueta}]", True, cor_console), (30, y))

        cor = COR_SELECIONADO if i == selecionado else COR_TEXTO
        janela.blit(fonte.render(jogo["nome"], True, cor), (200, y))
        y += 30

    # ----- rodapé: mensagem ou dicas -----
    if jogando:
        texto, cor = f"Jogando {jogando}... feche o jogo pra voltar", COR_SELECIONADO
    elif mensagem:
        texto, cor = mensagem, COR_ERRO
    else:
        texto, cor = "↑ ↓ escolher   ENTER jogar   ESC sair", COR_DICA
    janela.blit(fonte.render(texto, True, cor), (30, ALTURA - 40))

    pygame.display.flip()


# ===== EXECUÇÃO =====
if __name__ == "__main__":
    pygame.init()
    janela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Central de Jogos")
    relogio = pygame.time.Clock()
    fontes = (pygame.font.SysFont("consolas,couriernew,monospace", 18),
              pygame.font.SysFont("consolas,couriernew,monospace", 32, bold=True))

    consoles = carregar_consoles()
    jogos = listar_jogos(consoles)
    selecionado = 0
    topo = 0              # primeira linha mostrada (pra rolar a lista)
    mensagem = ""
    processo = None       # o emulador que está aberto agora
    jogando = ""

    rodando = True
    while rodando:
        # ----- o jogo foi fechado? volta pro menu -----
        if processo and processo.poll() is not None:
            processo = None
            jogando = ""

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.KEYDOWN and not processo and jogos:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(jogos)
                    mensagem = ""
                elif evento.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(jogos)
                    mensagem = ""
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    jogo = jogos[selecionado]
                    comando, erro = montar_comando(jogo, consoles)
                    if erro:
                        mensagem = erro
                    else:
                        # Popen abre o emulador SEM travar o menu
                        # roda o emulador "de dentro" da pasta dele
                        # (ex: RMG/), pra ele achar as configurações e plugins
                        pasta = None
                        if comando[0] != sys.executable:
                            pasta = os.path.dirname(comando[0])
                        processo = subprocess.Popen(comando, cwd=pasta)
                        jogando = jogo["nome"]

        # ----- rolagem: mantém o selecionado na tela -----
        if selecionado < topo:
            topo = selecionado
        elif selecionado >= topo + LINHAS_VISIVEIS:
            topo = selecionado - LINHAS_VISIVEIS + 1

        desenhar(janela, fontes, jogos, consoles, selecionado, topo, mensagem, jogando)
        relogio.tick(30)

    pygame.quit()

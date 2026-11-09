# ===== IMPORTS =====
import pygame
from emulador.disassembler import descrever

# ===== CONSTANTES =====
LARGURA_PAINEL = 300            # largura do painel, em pixels da janela
COR_FUNDO = (20, 20, 30)
COR_TEXTO = (200, 200, 200)
COR_TITULO = (120, 200, 255)
COR_DESTAQUE = (255, 220, 80)   # instrução atual / valores que mudaram
LINHAS_CODIGO = 7               # quantas instruções mostrar a partir do pc


# ===== CLASSE DEBUGGER =====
class Debugger:
    def __init__(self):
        # fonte monoespaçada: cada letra tem a mesma largura (alinha as colunas)
        self.fonte = pygame.font.SysFont("consolas,couriernew,monospace", 15)
        self.altura_linha = self.fonte.get_linesize()
        self.V_anterior = [0] * 16   # pra destacar registrador que mudou

    # ----- escreve uma linha de texto e desce -----
    def _texto(self, janela, texto, x, y, cor=COR_TEXTO):
        imagem = self.fonte.render(texto, True, cor)
        janela.blit(imagem, (x, y))
        return y + self.altura_linha

    # ----- desenha o painel inteiro -----
    def render(self, janela, cpu, x_inicio, pausado):
        altura = janela.get_height()
        pygame.draw.rect(janela, COR_FUNDO, (x_inicio, 0, LARGURA_PAINEL, altura))

        x = x_inicio + 10
        y = 6

        # ----- estado -----
        estado = "PAUSADO (N = passo)" if pausado else "RODANDO"
        y = self._texto(janela, estado, x, y, COR_DESTAQUE if pausado else COR_TITULO)

        # ----- registradores V0..VF, em 2 colunas -----
        y += 4
        for i in range(8):
            for coluna, reg in enumerate((i, i + 8)):
                valor = cpu.V[reg]
                cor = COR_DESTAQUE if valor != self.V_anterior[reg] else COR_TEXTO
                self._texto(janela, f"V{reg:X}={valor:02X}", x + coluna * 85, y, cor)
            y += self.altura_linha
        self.V_anterior = list(cpu.V)

        # ----- outros registradores -----
        y += 4
        y = self._texto(janela, f"PC={cpu.pc:03X}  I={cpu.I:03X}", x, y)
        y = self._texto(janela, f"DELAY={cpu.delay:02X} SOM={cpu.som:02X}", x, y)
        pilha = " ".join(f"{e:03X}" for e in cpu.pilha[-3:]) or "-"
        y = self._texto(janela, f"PILHA: {pilha}", x, y)

        # ----- próximas instruções -----
        y += 4
        y = self._texto(janela, "CÓDIGO", x, y, COR_TITULO)
        endereco = cpu.pc
        for linha in range(LINHAS_CODIGO):
            if endereco + 1 >= len(cpu.memoria.dados):
                break
            opcode = (cpu.memoria.ler(endereco) << 8) | cpu.memoria.ler(endereco + 1)
            seta = ">" if linha == 0 else " "
            cor = COR_DESTAQUE if linha == 0 else COR_TEXTO
            texto = f"{seta}{endereco:03X} {opcode:04X} {descrever(opcode)}"
            y = self._texto(janela, texto, x, y, cor)
            endereco += 2

# ===== IMPORTS =====
from emulador.memoria import INICIO_PROGRAMA


# ===== CLASSE CPU =====
class CPU:
    def __init__(self, memoria, tela):
        self.memoria = memoria
        self.tela = tela

        # ----- registradores -----
        self.V = [0] * 16          # V0 até VF
        self.I = 0                 # registrador de endereço
        self.pc = INICIO_PROGRAMA  # Program Counter
        self.pilha = []            # pilha de retorno

    # ----- FETCH: buscar a instrução -----
    def fetch(self):
        alto = self.memoria.ler(self.pc)
        baixo = self.memoria.ler(self.pc + 1)
        self.pc += 2
        return (alto << 8) | baixo

    # ----- DECODE: separar as partes da instrução -----
    def decode(self, opcode):
        tipo = (opcode & 0xF000) >> 12
        x    = (opcode & 0x0F00) >> 8
        y    = (opcode & 0x00F0) >> 4
        n    =  opcode & 0x000F
        nn   =  opcode & 0x00FF
        nnn  =  opcode & 0x0FFF
        return tipo, x, y, n, nn, nnn

    # ----- CICLO: fetch → decode → execute -----
    def ciclo(self):
        opcode = self.fetch()
        tipo, x, y, n, nn, nnn = self.decode(opcode)

        # ===== EXECUTE =====
        if opcode == 0x00E0:                 # CLS: limpa a tela
            self.tela.limpar()

        elif opcode == 0x00EE:               # RET: volta da sub-rotina
            self.pc = self.pilha.pop()

        elif tipo == 0x1:                    # JUMP: pula pra NNN
            self.pc = nnn

        elif tipo == 0x2:                    # CALL: chama sub-rotina
            self.pilha.append(self.pc)
            self.pc = nnn

        elif tipo == 0x3:                    # SKIP se VX == NN
            if self.V[x] == nn:
                self.pc += 2

        elif tipo == 0x4:                    # SKIP se VX != NN
            if self.V[x] != nn:
                self.pc += 2

        elif tipo == 0x5:                    # SKIP se VX == VY
            if self.V[x] == self.V[y]:
                self.pc += 2

        elif tipo == 0x6:                    # SET: VX = NN
            self.V[x] = nn                   # ⬅️ UM "=" só!

        elif tipo == 0x7:                    # ADD: VX = VX + NN
            self.V[x] = (self.V[x] + nn) & 0xFF

        elif tipo == 0x9:                    # SKIP se VX != VY
            self.I = self.I[x]

        elif tipo == 0xA:                    # SET I = NNN
            self.I = nnn

        elif tipo == 0xD:                    # DRAW
            sprite = [self.memoria.ler(self.I + i) for i in range(n)]
            colisao = self.tela.desenhar_sprite(self.V[x], self.V[y], sprite)
            self.V[0xF] = 1 if colisao else 0

        else:
            print(f"Instrução não implementada: {opcode:04X}")
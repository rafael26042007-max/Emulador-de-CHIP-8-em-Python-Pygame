# ===== TIMER DO GAME BOY =====
# DIV  (FF04): sobe sozinho 16384 vezes por segundo (a cada 256 ciclos)
# TIMA (FF05): contador configurável; quando passa de 255, volta pro TMA
#              e pede a interrupção de Timer
# TMA  (FF06): valor de recomeço do TIMA
# TAC  (FF07): bit 2 = ligado / bits 0-1 = velocidade

# ===== CONSTANTES =====
DIV, TIMA, TMA, TAC = 0xFF04, 0xFF05, 0xFF06, 0xFF07
REG_IF = 0xFF0F
CICLOS_POR_TAC = (1024, 16, 64, 256)   # TAC 00, 01, 10, 11


# ===== CLASSE TIMER =====
class Timer:
    def __init__(self, memoria):
        self.mem = memoria
        self.conta_div = 0
        self.conta_tima = 0

    def passo(self, ciclos):
        io = self.mem.io

        # ----- DIV -----
        self.conta_div += ciclos
        while self.conta_div >= 256:
            self.conta_div -= 256
            io[DIV - 0xFF00] = (io[DIV - 0xFF00] + 1) & 0xFF

        # ----- TIMA -----
        tac = io[TAC - 0xFF00]
        if not tac & 0x04:
            return
        periodo = CICLOS_POR_TAC[tac & 0x03]
        self.conta_tima += ciclos
        while self.conta_tima >= periodo:
            self.conta_tima -= periodo
            tima = io[TIMA - 0xFF00] + 1
            if tima > 0xFF:
                tima = io[TMA - 0xFF00]
                io[REG_IF - 0xFF00] |= 0x04          # pede interrupção de Timer (bit 2)
            io[TIMA - 0xFF00] = tima

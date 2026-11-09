# ===== IMPORTS =====
import array
import pygame

# ===== CONSTANTES =====
TAXA = 44100        # amostras por segundo
FREQUENCIA = 440    # nota do bip (Lá)
VOLUME = 3000       # 0 a 32767


# ===== CLASSE SOM =====
class Som:
    def __init__(self):
        self.tocando = False
        self.bip = None

        try:
            pygame.mixer.init(frequency=TAXA, size=-16, channels=1)

            # monta 1 ciclo de onda quadrada: metade em cima, metade embaixo
            amostras_por_ciclo = TAXA // FREQUENCIA
            metade = amostras_por_ciclo // 2
            onda = array.array("h", [VOLUME] * metade + [-VOLUME] * metade)

            self.bip = pygame.mixer.Sound(buffer=onda.tobytes())
        except pygame.error:
            # sem placa de som: o emulador roda mudo, sem quebrar
            print("Aviso: som desativado (nenhum dispositivo de áudio)")

    # ----- liga ou desliga conforme o sound timer -----
    def atualizar(self, sound_timer):
        if self.bip is None:
            return

        if sound_timer > 0 and not self.tocando:
            self.bip.play(loops=-1)     # -1 = repete até mandar parar
            self.tocando = True
        elif sound_timer == 0 and self.tocando:
            self.bip.stop()
            self.tocando = False

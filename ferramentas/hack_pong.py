# ===== HACK DO PONG: FIM DE JOGO EM 9 PONTOS =====
# Lê o rom/pong.ch8 original e cria o rom/pong9.ch8 modificado.
# Truque de ROM hacking: trocar UMA instrução por um CALL pra um código novo,
# colocado num pedaço livre da memória, depois do fim do jogo original.

# ----- onde mexer -----
INICIO = 0x200              # o jogo começa no endereço 0x200
ENDERECO_TROCA = 0x2AA      # aqui o jogo original faz "CALL 2D4" (desenha o placar)
ENDERECO_NOVO = 0x300       # memória livre: o código novo fica aqui

# ----- código novo, em opcodes (cada linha = 1 instrução de 2 bytes) -----
CODIGO_NOVO = [
    0x22D4,  # 300  CALL 2D4         desenha o placar (o que o jogo já fazia)
    #                       e deixa V1 = dígito da esquerda, V2 = da direita
    0x4109,  # 302  SKIP V1 != 9     esquerda chegou em 9?
    0x1310,  # 304  JUMP 310         ...sim: fim de jogo
    0x4209,  # 306  SKIP V2 != 9     direita chegou em 9?
    0x1310,  # 308  JUMP 310         ...sim: fim de jogo
    0x00EE,  # 30A  RET              ninguém ganhou: volta pro jogo
    0x0000,  # 30C  (sobra)
    0x0000,  # 30E  (sobra)

    # ----- FIM DE JOGO -----
    0x6078,  # 310  V0 = 78          120 quadros = 2 segundos
    0xF015,  # 312  DELAY = V0
    0xF007,  # 314  V0 = DELAY       espera os 2 segundos
    0x3000,  # 316  SKIP V0 == 0     (pra não reiniciar com a tecla ainda apertada)
    0x1314,  # 318  JUMP 314
    0xF00A,  # 31A  V0 = espera tecla

    # ----- NOVA PARTIDA -----
    0x00E0,  # 31C  CLS              limpa a tela (o jogo original nunca precisou)
    0x6E00,  # 31E  VE = 0           zera o placar
    0xA2EA,  # 320  I = 2EA          desenho da raquete
    0xDAB6,  # 322  DRAW VA,VB       redesenha a raquete da esquerda
    0xDCD6,  # 324  DRAW VC,VD       redesenha a raquete da direita
    0x22D4,  # 326  CALL 2D4         desenha o placar 0 0
    0x00EE,  # 328  RET              volta pro jogo, que saca a bola de novo
]


# ===== EXECUÇÃO =====
if __name__ == "__main__":
    with open("rom/pong.ch8", "rb") as arquivo:
        rom = bytearray(arquivo.read())

    # confere se é mesmo o Pong que a gente estudou
    posicao = ENDERECO_TROCA - INICIO
    assert rom[posicao:posicao + 2] == bytes([0x22, 0xD4]), "Essa não é a ROM esperada!"

    # 1) troca o "CALL 2D4" por "CALL 300"
    rom[posicao] = 0x20 | (ENDERECO_NOVO >> 8)    # 0x23
    rom[posicao + 1] = ENDERECO_NOVO & 0xFF       # 0x00

    # 2) completa com zeros até o 0x300
    while len(rom) < ENDERECO_NOVO - INICIO:
        rom.append(0)

    # 3) escreve o código novo
    for opcode in CODIGO_NOVO:
        rom.append(opcode >> 8)      # byte alto
        rom.append(opcode & 0xFF)    # byte baixo

    with open("rom/pong9.ch8", "wb") as arquivo:
        arquivo.write(rom)

    print(f"rom/pong9.ch8 criado ({len(rom)} bytes)")
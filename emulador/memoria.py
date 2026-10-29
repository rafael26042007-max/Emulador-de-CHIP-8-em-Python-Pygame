# ===== CONSTANTES =====
TAMANHO_MEMORIA = 4096
INICIO_PROGRAMA = 0x200   # 0x200 = 512 em decimal


# ===== CLASSE MEMORIA =====
class Memoria:
    def __init__(self):
        # cria as 4096 caixinhas, todas com 0
        self.dados = bytearray(TAMANHO_MEMORIA)

    def carregar_rom(self, caminho):
        # "rb" = read (ler) + binary (binário)
        # binário porque o .ch8 não é texto, são números puros
        with open(caminho, "rb") as arquivo:
            conteudo = arquivo.read()   # pega todos os números do arquivo

        # enumerate dá a posição (i) e o valor (byte) de cada número
        # ex: i=0, byte=0x00 / i=1, byte=0xE0 / ...
        for i, byte in enumerate(conteudo):
            # guarda na caixinha 512, 513, 514...
            self.dados[INICIO_PROGRAMA + i] = byte

    def ler(self, endereco):
        return self.dados[endereco]

    def escrever(self, endereco, valor):
        # & 0xFF corta o número pra caber numa caixinha (0 a 255)
        self.dados[endereco] = valor & 0xFF

    def dump(self, inicio, quantidade):
        # pega um pedaço das caixinhas
        pedaco = self.dados[inicio:inicio + quantidade]

        # transforma cada número em texto hexadecimal com 2 dígitos
        # ex: 224 vira "E0", 10 vira "0A"
        textos = [f"{b:02X}" for b in pedaco]

        # junta tudo com espaço e mostra na tela
        print(" ".join(textos))
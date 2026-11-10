# ===== CLASSE CARTUCHO =====
class Cartucho:
    def __init__(self, caminho):
        with open(caminho, "rb") as arquivo:
            self.rom = arquivo.read()

    def titulo(self):
        # bytes 0x134 a 0x143, texto; os bytes 0 no final são "espaço vazio"
        bruto = self.rom[0x134:0x144]
        return bruto.split(b"\x00")[0].decode("ascii", errors="replace")

    def tamanho_kb(self):
        return 32 << self.rom[0x148]   # 0 = 32 KB, 1 = 64 KB, 2 = 128 KB...

    def tipo(self):
        return self.rom[0x147]

    def checksum_ok(self):
        x = 0
        # range(0x134, 0x14D) vai de 0x134 até 0x14C (o 0x14D fica de fora)
        for endereco in range(0x134, 0x14D):
            # subtrai o byte e mais 1; o & 0xFF faz o número "dar a volta" e ficar entre 0 e 255
            x = (x - self.rom[endereco] - 1) & 0xFF
        # o resultado tem que bater com o checksum gravado no cartucho
        return x == self.rom[0x14D]


# ===== EXECUÇÃO =====
if __name__ == "__main__":
    cart = Cartucho("rom/gb/dmg-acid2.gb")
    print("Título:  ", cart.titulo())
    print("Tipo:    ", hex(cart.tipo()))
    print("Tamanho: ", cart.tamanho_kb(), "KB")
    print("Checksum:", "OK ✅" if cart.checksum_ok() else "ERRADO ❌")
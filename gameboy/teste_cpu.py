# ===== TESTA A CPU COM AS ROMs DO BLARGG =====
# Uso:  python -m gameboy.teste_cpu rom/gb/blargg/06-ld_r_r.gb
#       python -m gameboy.teste_cpu rom/gb/blargg        (roda todas da pasta)
# As ROMs "imprimem" o resultado pelo cabo de link (serial).

# ===== IMPORTS =====
import os
import sys
import time
from gameboy.console import GameBoy

# ===== CONSTANTES =====
LIMITE_CICLOS = 200_000_000     # ~48 segundos de Game Boy de verdade


# ===== RODAR UMA ROM =====
def rodar(caminho):
    gb = GameBoy(caminho)
    inicio = time.time()
    try:
        while gb.ciclos_total < LIMITE_CICLOS:
            gb.passo()
            texto = gb.memoria.serial
            if "Passed" in texto or "Failed" in texto:
                break
    except RuntimeError as erro:
        gb.memoria.serial += f"\n[ERRO] {erro}"

    duracao = time.time() - inicio
    texto = gb.memoria.serial.strip().replace("\n", " | ")
    ok = "Passed" in texto
    print(f"{'✅' if ok else '❌'} {os.path.basename(caminho):28s} {duracao:6.1f}s  {texto}")
    return ok


# ===== EXECUÇÃO =====
if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else "rom/gb/blargg"
    if os.path.isdir(alvo):
        roms = sorted(os.path.join(alvo, f) for f in os.listdir(alvo) if f.endswith(".gb"))
    else:
        roms = [alvo]
    passou = sum(rodar(r) for r in roms)
    print(f"\n{passou}/{len(roms)} testes passaram")

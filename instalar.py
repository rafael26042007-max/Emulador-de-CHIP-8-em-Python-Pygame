# ===== INSTALADOR =====
# Baixa sozinho os jogos de CHIP-8 e o emulador de N64 listados no downloads.json.
# Rodar uma vez depois de clonar o projeto:   python instalar.py
# O que já existe é pulado, então pode rodar de novo sem medo.

# ===== IMPORTS =====
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import webbrowser
import zipfile

# ===== CONSTANTES =====
ARQUIVO_DOWNLOADS = "downloads.json"


# ===== BAIXAR =====
def baixar(url, destino):
    # baixa a url pro arquivo destino, mostrando o progresso em %
    pedido = urllib.request.Request(url, headers={"User-Agent": "CHIP-8-Central"})
    with urllib.request.urlopen(pedido, timeout=60) as resposta, open(destino, "wb") as arquivo:
        total = int(resposta.headers.get("Content-Length") or 0)
        baixado = 0
        while True:
            pedaco = resposta.read(64 * 1024)
            if not pedaco:
                break
            arquivo.write(pedaco)
            baixado += len(pedaco)
            if total > 100_000:   # só mostra % em arquivo grande
                print(f"\r    {baixado * 100 // total:3d}%", end="", flush=True)
    if total > 100_000:
        print()


def sha256_do_arquivo(caminho):
    # calcula a "impressão digital" do arquivo, pra conferir que não foi alterado
    soma = hashlib.sha256()
    with open(caminho, "rb") as arquivo:
        for pedaco in iter(lambda: arquivo.read(1024 * 1024), b""):
            soma.update(pedaco)
    return soma.hexdigest()


# ===== JOGOS DE CHIP-8 =====
def instalar_chip8(itens):
    print("\n== Jogos de CHIP-8 ==")
    for item in itens:
        destino = item["destino"]
        if os.path.exists(destino):
            print(f"  ✓ {item['nome']} (já tinha)")
            continue
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        try:
            baixar(item["url"], destino)
            print(f"  ↓ {item['nome']}")
        except Exception as erro:
            print(f"  ✗ {item['nome']}: {erro}")
            if os.path.exists(destino):
                os.remove(destino)   # não deixa arquivo pela metade

    # o pong9 é gerado a partir do pong (nosso ROM hack)
    if os.path.exists("rom/pong.ch8") and not os.path.exists("rom/pong9.ch8"):
        subprocess.run([sys.executable, "ferramentas/hack_pong.py"])


# ===== EMULADORES =====
def instalar_emulador(item):
    nome, destino = item["nome"], item["destino"]

    if os.path.exists(destino):
        print(f"  ✓ {nome} (já tinha)")
        return
    if item.get("so_windows") and os.name != "nt":
        print(f"  - {nome}: só tem versão pra Windows aqui, pulei")
        return

    with tempfile.TemporaryDirectory() as temp:
        arquivo_zip = os.path.join(temp, "download.zip")
        print(f"  ↓ {nome}")
        baixar(item["url"], arquivo_zip)

        # segurança: confere a impressão digital antes de extrair qualquer coisa
        esperado = item.get("sha256")
        if esperado and sha256_do_arquivo(arquivo_zip) != esperado:
            print(f"  ✗ {nome}: o arquivo baixado NÃO bate com o sha256 esperado. Cancelado.")
            return

        extraido = os.path.join(temp, "extraido")
        with zipfile.ZipFile(arquivo_zip) as zip_:
            zip_.extractall(extraido)

        # o zip vem com uma pasta dentro (ex: ares-v148/): ela vira a pasta destino
        origem = os.path.join(extraido, item.get("zip_pasta_interna", ""))
        shutil.move(origem, destino)
        print(f"  ✓ {nome} instalado em {destino}/")


# ===== JOGOS QUE PRECISAM DE CLIQUE =====
def mostrar_manuais(itens):
    # o itch.io não deixa baixar automático: abre a página e explica onde salvar
    print("\n== Jogos que você baixa pela página do autor ==")
    for item in itens:
        print(f"  • {item['nome']}: {item['pagina']}  →  salvar em {item['destino']}")

    resposta = input("\nAbrir essas páginas no navegador agora? (s/n) ").strip().lower()
    if resposta == "s":
        for item in itens:
            webbrowser.open(item["pagina"])


# ===== EXECUÇÃO =====
if __name__ == "__main__":
    # roda sempre a partir da pasta do projeto, de onde quer que seja chamado
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with open(ARQUIVO_DOWNLOADS, encoding="utf-8") as arquivo:
        lista = json.load(arquivo)

    instalar_chip8(lista["chip8"])

    print("\n== Emuladores ==")
    for emulador in lista["emuladores"]:
        try:
            instalar_emulador(emulador)
        except Exception as erro:
            print(f"  ✗ {emulador['nome']}: {erro}")

    os.makedirs("rom/n64", exist_ok=True)
    mostrar_manuais(lista["manuais"])

    print("\nPronto! Agora é só rodar:  python central.py")

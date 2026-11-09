# ===== IMPORTS =====
import json
import os
import shutil
import sys

# ===== CONSTANTES =====
ARQUIVO_CONSOLES = "consoles.json"
PASTA_ROMS = "rom"


# ===== CONSOLES =====
def carregar_consoles():
    # lê o consoles.json: cada console diz suas extensões e como chamar o emulador
    with open(ARQUIVO_CONSOLES, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def console_do_arquivo(nome_arquivo, consoles):
    # descobre o console pela extensão: "pong.ch8" → chip8
    extensao = os.path.splitext(nome_arquivo)[1].lower()
    for chave, console in consoles.items():
        if extensao in console["extensoes"]:
            return chave
    return None


# ===== JOGOS =====
def listar_jogos(consoles):
    # procura em rom/ e nas subpastas (dá pra separar: rom/n64/, rom/chip8/...)
    jogos = []
    for pasta, _, arquivos in os.walk(PASTA_ROMS):
        for nome in arquivos:
            chave = console_do_arquivo(nome, consoles)
            if chave:
                jogos.append({
                    "nome": os.path.splitext(nome)[0],
                    "caminho": os.path.join(pasta, nome),
                    "console": chave,
                })

    # ordena por console e depois por nome
    jogos.sort(key=lambda j: (consoles[j["console"]]["nome"], j["nome"].lower()))
    return jogos


# ===== MONTAR O COMANDO =====
def montar_comando(jogo, consoles):
    # troca {python} e {rom} pelos valores de verdade
    modelo = consoles[jogo["console"]]["comando"]
    comando = [parte.replace("{python}", sys.executable)
               .replace("{rom}", os.path.abspath(jogo["caminho"]))
               for parte in modelo]

    # confere se o programa existe antes de tentar abrir
    programa = comando[0]
    if not (os.path.isfile(programa) or shutil.which(programa)):
        nome_console = consoles[jogo["console"]]["nome"]
        return None, f"Emulador de {nome_console} não encontrado (veja consoles.json)"

    # caminho relativo (ex: "RMG/RMG.exe") vira completo, pro Windows achar
    if os.path.isfile(programa):
        comando[0] = os.path.abspath(programa)

    return comando, None
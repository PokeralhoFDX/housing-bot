import time
import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os

URL = "https://www.mymoveoldham.co.uk/Choice/OLDHAM_PropertyList.aspx"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

FICHEIRO_ESTADO = "casas_vistas.json"

TELEGRAM_TOKEN = os.getenv("8774528470:AAHJYXnRf1caGUtPyo3uef3vM1qcnO-vSaA")
CHAT_ID = os.getenv("7928542961")


def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def carregar_estado():
    if os.path.exists(FICHEIRO_ESTADO):
        with open(FICHEIRO_ESTADO, "r") as f:
            return set(json.load(f))
    return set()


def guardar_estado(ids):
    with open(FICHEIRO_ESTADO, "w") as f:
        json.dump(list(ids), f)


def gerar_id(texto):
    return hashlib.md5(texto.encode()).hexdigest()


def obter_casas():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    textos = soup.get_text(separator="\n").split("\n")

    casas = []
    for linha in textos:
        linha = linha.strip()
        if "£" in linha and len(linha) > 10:
            casas.append(linha)

    return casas


def monitorar():
    print("A monitorizar casas...")

    vistos = carregar_estado()

    while True:
        try:
            casas = obter_casas()

            novos_ids = set()
            novas_casas = []

            for casa in casas:
                cid = gerar_id(casa)
                novos_ids.add(cid)

                if cid not in vistos:
                    novas_casas.append(casa)

            if novas_casas:
                msg = "🏠 Novas casas disponíveis:\n\n"
                for casa in novas_casas:
                    msg += f"- {casa}\n"

                enviar_telegram(msg)
                print(f"{len(novas_casas)} novas casas!")

            vistos = vistos.union(novos_ids)
            guardar_estado(vistos)

        except Exception as e:
            print("Erro:", e)

        time.sleep(180)


if __name__ == "__main__":
    enviar_telegram("✅ Bot is online and working!")
    monitorar()

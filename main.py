import time
import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os

URL = "https://www.mymoveoldham.co.uk/Choice/OLDHAM_PropertyList.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0"}
FICHEIRO_ESTADO = "casas_vistas.json"

# FIXED: Hardcoded strings (or use proper os.getenv("KEY_NAME"))
TELEGRAM_TOKEN = "8774528470:AAHJYXnRf1caGUtPyo3uef3vM1qcnO-vSaA"
CHAT_ID = "7928542961"

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        payload = {"chat_id": CHAT_ID, "text": msg}
        r = requests.post(url, data=payload)
        r.raise_for_status() # Check if the request actually worked
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def carregar_estado():
    if os.path.exists(FICHEIRO_ESTADO):
        try:
            with open(FICHEIRO_ESTADO, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def guardar_estado(ids):
    with open(FICHEIRO_ESTADO, "w") as f:
        json.dump(list(ids), f)

def gerar_id(texto):
    return hashlib.md5(texto.encode('utf-8')).hexdigest()

def obter_casas():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Suggestion: Try to find specific property containers if possible
        # For now, keeping your logic but making it a bit cleaner
        textos = soup.get_text(separator="\n").split("\n")
        casas = [l.strip() for l in textos if "£" in l and len(l.strip()) > 10]
        
        return list(set(casas)) # Remove duplicates in the same fetch
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

def monitorar():
    print("A monitorizar casas... (Press Ctrl+C to stop)")
    vistos = carregar_estado()

    while True:
        try:
            casas = obter_casas()
            novas_casas = []

            for casa in casas:
                cid = gerar_id(casa)
                if cid not in vistos:
                    novas_casas.append(casa)
                    vistos.add(cid) # Add to seen set immediately

            if novas_casas:
                msg = "🏠 Novas casas disponíveis:\n\n" + "\n".join([f"- {c}" for c in novas_casas])
                enviar_telegram(msg)
                print(f"{len(novas_casas)} novas casas encontradas!")
                guardar_estado(vistos) # Only save if there's a change
            else:
                print("Sem novidades...")

        except Exception as e:
            print("Erro no loop principal:", e)

        time.sleep(300) # Increased to 5 mins to be polite to the server

if __name__ == "__main__":
    # Test connection on startup
    enviar_telegram("✅ Bot is online and working!")
    monitorar()

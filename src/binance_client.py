import hashlib
import hmac
import os
import time
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()

URL_TESTNET = "https://testnet.binance.vision/api"
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


def heure_serveur():
    """Demande l'heure à Binance pour éviter tout décalage d'horloge."""
    r = requests.get(f"{URL_TESTNET}/v3/time", timeout=15)
    r.raise_for_status()
    return r.json()["serverTime"]


def requete_signee(methode, chemin, params=None):
    """Envoie une requête authentifiée au Testnet Binance."""
    params = dict(params or {})
    params["timestamp"] = heure_serveur()
    params["recvWindow"] = 10000
    texte = urlencode(params)
    signature = hmac.new(
        API_SECRET.encode(), texte.encode(), hashlib.sha256
    ).hexdigest()
    url = f"{URL_TESTNET}{chemin}?{texte}&signature={signature}"
    reponse = requests.request(
        methode, url, headers={"X-MBX-APIKEY": API_KEY}, timeout=15
    )
    if not reponse.ok:
        print("Réponse de Binance :", reponse.text)
    reponse.raise_for_status()
    return reponse.json()


def lire_soldes():
    """Retourne les soldes non nuls sous forme de dictionnaire."""
    compte = requete_signee("GET", "/v3/account")
    return {
        b["asset"]: float(b["free"])
        for b in compte["balances"]
        if float(b["free"]) > 0
    }


def prix_actuel(symbole):
    r = requests.get(
        f"{URL_TESTNET}/v3/ticker/price", params={"symbol": symbole}, timeout=15
    )
    r.raise_for_status()
    return float(r.json()["price"])


def acheter_au_marche(symbole, montant_usdt):
    """Achète pour `montant_usdt` USDT au prix du marché (Testnet uniquement)."""
    return requete_signee(
        "POST",
        "/v3/order",
        {
            "symbol": symbole,
            "side": "BUY",
            "type": "MARKET",
            "quoteOrderQty": montant_usdt,
        },
    )


if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        raise SystemExit("Clés introuvables : vérifie le fichier .env")
    for monnaie, quantite in lire_soldes().items():
        print(f"{monnaie} : {quantite}")
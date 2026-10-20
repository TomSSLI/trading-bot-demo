import hashlib
import hmac
import os
import time
from urllib.parse import urlencode
from decimal import Decimal, ROUND_DOWN

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

def regles_symbole(symbole):
    """Lit sur Binance le pas de quantité et le pas de prix de la paire."""
    r = requests.get(
        f"{URL_TESTNET}/v3/exchangeInfo", params={"symbol": symbole}, timeout=15
    )
    r.raise_for_status()
    filtres = {f["filterType"]: f for f in r.json()["symbols"][0]["filters"]}
    return filtres["LOT_SIZE"]["stepSize"], filtres["PRICE_FILTER"]["tickSize"]


def arrondir(valeur, pas):
    """Arrondit vers le bas à un multiple de `pas` et renvoie un texte."""
    pas_d = Decimal(str(pas))
    n = (Decimal(str(valeur)) / pas_d).to_integral_value(rounding=ROUND_DOWN)
    return format(n * pas_d, "f")


def acheter_quantite(symbole, quantite):
    """Achat au marché d'une quantité de BTC (Testnet)."""
    pas_qte, _ = regles_symbole(symbole)
    return requete_signee(
        "POST",
        "/v3/order",
        {
            "symbol": symbole,
            "side": "BUY",
            "type": "MARKET",
            "quantity": arrondir(quantite, pas_qte),
        },
    )


def poser_stop_loss(symbole, quantite, prix_stop, ecart_limite_pct=0.5):
    """Ordre de vente déclenché si le prix tombe à `prix_stop`."""
    pas_qte, pas_prix = regles_symbole(symbole)
    prix_limite = prix_stop * (1 - ecart_limite_pct / 100)
    return requete_signee(
        "POST",
        "/v3/order",
        {
            "symbol": symbole,
            "side": "SELL",
            "type": "STOP_LOSS_LIMIT",
            "timeInForce": "GTC",
            "quantity": arrondir(quantite, pas_qte),
            "stopPrice": arrondir(prix_stop, pas_prix),
            "price": arrondir(prix_limite, pas_prix),
        },
    )


def annuler_ordre(symbole, order_id):
    return requete_signee(
        "DELETE", "/v3/order", {"symbol": symbole, "orderId": order_id}
    )

def annuler_tous_les_ordres(symbole):
    return requete_signee("DELETE", "/v3/openOrders", {"symbol": symbole})

if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        raise SystemExit("Clés introuvables : vérifie le fichier .env")
    for monnaie, quantite in lire_soldes().items():
        print(f"{monnaie} : {quantite}")
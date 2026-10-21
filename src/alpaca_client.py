import os
import time
from decimal import Decimal, ROUND_DOWN

import requests
from dotenv import load_dotenv

load_dotenv()

URL_TRADING = "https://paper-api.alpaca.markets/v2"
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")


def fmt_qte(quantite):
    """Arrondit toujours vers le bas, jusqu'à 9 décimales."""
    d = Decimal(str(quantite)).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
    return format(d, "f")


def requete(methode, chemin, params=None, json=None):
    """Envoie une requête authentifiée au compte PAPER d'Alpaca."""
    reponse = requests.request(
        methode,
        f"{URL_TRADING}{chemin}",
        headers={
            "APCA-API-KEY-ID": API_KEY,
            "APCA-API-SECRET-KEY": API_SECRET,
        },
        params=params,
        json=json,
        timeout=15,
    )
    if not reponse.ok and reponse.status_code != 404:
        print("Réponse d'Alpaca :", reponse.text)
    reponse.raise_for_status()
    if reponse.status_code == 204 or not reponse.text:
        return None
    return reponse.json()


def lire_compte():
    return requete("GET", "/account")


def lire_liquidites():
    return float(lire_compte()["cash"])


def quantite_detenue(symbole):
    """Quantité réellement détenue (après frais). 0 si aucune position."""
    code = symbole.replace("/", "")
    try:
        return float(requete("GET", f"/positions/{code}")["qty"])
    except requests.exceptions.HTTPError:
        return 0.0


def attendre_execution(order_id, delai=30):
    """Attend que l'ordre soit exécuté et renvoie l'ordre final."""
    debut = time.time()
    while time.time() - debut < delai:
        ordre = requete("GET", f"/orders/{order_id}")
        if ordre["status"] in ("filled", "canceled", "rejected", "expired"):
            return ordre
        time.sleep(1)
    return requete("GET", f"/orders/{order_id}")


def acheter_quantite(symbole, quantite):
    """Achat au marché. Renvoie l'ordre exécuté."""
    ordre = requete("POST", "/orders", json={
        "symbol": symbole,
        "side": "buy",
        "type": "market",
        "time_in_force": "gtc",
        "qty": fmt_qte(quantite),
    })
    return attendre_execution(ordre["id"])


def poser_stop_loss(symbole, quantite, prix_stop, ecart_limite_pct=0.5):
    """Ordre de vente déclenché si le prix tombe à `prix_stop`."""
    prix_limite = prix_stop * (1 - ecart_limite_pct / 100)
    return requete("POST", "/orders", json={
        "symbol": symbole,
        "side": "sell",
        "type": "stop_limit",
        "time_in_force": "gtc",
        "qty": fmt_qte(quantite),
        "stop_price": f"{prix_stop:.0f}",
        "limit_price": f"{prix_limite:.0f}",
    })


def annuler_ordre(order_id):
    requete("DELETE", f"/orders/{order_id}")


def etat_ordre(order_id):
    return requete("GET", f"/orders/{order_id}")["status"]


def vendre_quantite(symbole, quantite):
    """Vente au marché. Renvoie l'ordre exécuté."""
    ordre = requete("POST", "/orders", json={
        "symbol": symbole,
        "side": "sell",
        "type": "market",
        "time_in_force": "gtc",
        "qty": fmt_qte(quantite),
    })
    return attendre_execution(ordre["id"])


if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        raise SystemExit("Clés introuvables : vérifie le fichier .env")
    compte = lire_compte()
    print("Statut :", compte["status"])
    print("Liquidités :", compte["cash"])
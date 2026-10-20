import json
import requests
import pandas as pd

URL_PRIX = "https://data-api.binance.vision/api/v3/klines"


def charger_config(chemin="config/crypto.json"):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def recuperer_bougies(symbole, intervalle, nombre=200):
    params = {"symbol": symbole, "interval": intervalle, "limit": nombre}
    reponse = requests.get(URL_PRIX, params=params, timeout=15)
    reponse.raise_for_status()
    colonnes = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_base", "taker_quote", "ignore",
    ]
    df = pd.DataFrame(reponse.json(), columns=colonnes)
    df["close"] = df["close"].astype(float)
    df["date"] = pd.to_datetime(df["close_time"], unit="ms")
    return df[["date", "close"]]


def calculer_ema(prix, periode):
    return prix.ewm(span=periode, adjust=False).mean()


def calculer_rsi(prix, periode=14):
    variation = prix.diff()
    gains = variation.clip(lower=0)
    pertes = -variation.clip(upper=0)
    moy_gains = gains.ewm(alpha=1 / periode, adjust=False).mean()
    moy_pertes = pertes.ewm(alpha=1 / periode, adjust=False).mean()
    rs = moy_gains / moy_pertes
    return 100 - (100 / (1 + rs))


def analyser():
    cfg = charger_config()
    df = recuperer_bougies(cfg["symbol"], cfg["interval"])
    df["ema_rapide"] = calculer_ema(df["close"], cfg["ema_fast"])
    df["ema_lente"] = calculer_ema(df["close"], cfg["ema_slow"])
    df["rsi"] = calculer_rsi(df["close"], cfg["rsi_period"])
    return df


if __name__ == "__main__":
    donnees = analyser()
    print(donnees.tail(5).to_string(index=False))
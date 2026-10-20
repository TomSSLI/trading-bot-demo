from binance_client import prix_actuel, acheter_au_marche, lire_soldes

SYMBOLE = "BTCUSDT"

print("Prix BTC (Testnet) :", prix_actuel(SYMBOLE))
print("USDT avant :", lire_soldes().get("USDT"))

ordre = acheter_au_marche(SYMBOLE, 10)
print("Ordre :", ordre["status"], "| quantité achetée :", ordre["executedQty"], "BTC")

print("USDT après :", lire_soldes().get("USDT"))
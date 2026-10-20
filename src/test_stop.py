from analyse import charger_config
from binance_client import acheter_quantite, poser_stop_loss, annuler_ordre
from risque import prix_stop_loss

cfg = charger_config()
symbole = cfg["symbol"]

achat = acheter_quantite(symbole, 0.0002)
qte = float(achat["executedQty"])
prix_entree = float(achat["cummulativeQuoteQty"]) / qte
print(f"Achat : {achat['status']} | {qte} BTC à {prix_entree:.2f}")

stop = prix_stop_loss(prix_entree, cfg)
ordre_stop = poser_stop_loss(symbole, qte, stop)
print("Réponse stop :", ordre_stop)
print(f"Stop loss posé | déclenchement à {stop}")

annuler_ordre(symbole, ordre_stop["orderId"])
print("Stop de test annulé.")
import time

from alpaca_client import (
    acheter_quantite, quantite_detenue, poser_stop_loss,
    annuler_ordre, vendre_quantite, lire_liquidites,
)

SYMBOLE = "BTC/USD"

print("Liquidités avant :", lire_liquidites())

achat = acheter_quantite(SYMBOLE, 0.0002)
prix_entree = float(achat["filled_avg_price"])
print(f"Achat : {achat['status']} | demandé 0.0002 | prix {prix_entree:.2f}")

time.sleep(2)
detenu = quantite_detenue(SYMBOLE)
print("Quantité réellement détenue :", detenu)

stop = prix_entree * 0.98
ordre_stop = poser_stop_loss(SYMBOLE, detenu, stop)
print("Stop posé :", ordre_stop["status"], "| déclenchement à", round(stop))

annuler_ordre(ordre_stop["id"])
print("Stop de test annulé.")

time.sleep(2)
vente = vendre_quantite(SYMBOLE, quantite_detenue(SYMBOLE))
print("Vente :", vente["status"])

time.sleep(2)
print("Quantité restante :", quantite_detenue(SYMBOLE))
print("Liquidités après :", lire_liquidites())
from analyse import analyser, charger_config
from strategie import decider
from risque import calculer_quantite, prix_stop_loss, peut_acheter
from etat import position_ouverte, ouvrir_position, fermer_position
from binance_client import (
    lire_soldes, acheter_quantite, poser_stop_loss, annuler_ordre,
    etat_ordre, vendre_quantite,
)


def executer():
    cfg = charger_config()
    symbole = cfg["symbol"]
    position = position_ouverte()
    df = analyser()
    signal = decider(df, cfg)
    prix = float(df.iloc[-2]["close"])
    compte_rendu = [f"Marché {symbole} | prix {prix:.2f} | signal {signal}"]

    if position is None:
        capital = lire_soldes().get("USDT", 0.0)
        quantite = calculer_quantite(capital, prix, cfg)
        if signal == "ACHAT" and peut_acheter(False, quantite):
            achat = acheter_quantite(symbole, quantite)
            qte = float(achat["executedQty"])
            entree = float(achat["cummulativeQuoteQty"]) / qte
            stop = prix_stop_loss(entree, cfg)
            ordre_stop = poser_stop_loss(symbole, qte, stop)
            ouvrir_position(symbole, qte, entree, stop, ordre_stop["orderId"])
            compte_rendu.append(
                f"ACHAT {qte} BTC à {entree:.2f} | stop loss {stop}"
            )
        else:
            compte_rendu.append("Aucune action (hors position).")
    else:
        statut = etat_ordre(symbole, position["id_stop"])
        if statut == "FILLED":
            fermer_position()
            compte_rendu.append(
                f"Stop loss déclenché à {position['prix_stop']} : position fermée."
            )
        elif signal == "VENTE":
            annuler_ordre(symbole, position["id_stop"])
            vente = vendre_quantite(symbole, position["quantite"])
            sortie = float(vente["cummulativeQuoteQty"]) / float(vente["executedQty"])
            fermer_position()
            compte_rendu.append(
                f"VENTE à {sortie:.2f} (entrée {position['prix_entree']:.2f})."
            )
        else:
            compte_rendu.append(
                f"En position ({position['quantite']} BTC, stop {position['prix_stop']}) : on garde."
            )

    return "\n".join(compte_rendu)


if __name__ == "__main__":
    from email_recap import envoyer_recap

    try:
        resultat = executer()
        print(resultat)
        # E-mail uniquement quand le bot a agi (achat, vente, stop déclenché)
        if "ACHAT " in resultat or "VENTE à" in resultat or "Stop loss déclenché" in resultat:
            envoyer_recap(resultat)
    except Exception as erreur:
        message = f"ERREUR du bot : {erreur}"
        print(message)
        envoyer_recap(message)
        raise
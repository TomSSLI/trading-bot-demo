from analyse import analyser, charger_config
from strategie import decider
from etat import position_ouverte
from alpaca_client import lire_compte
from email_recap import envoyer_recap


def construire_bilan():
    cfg = charger_config()
    compte = lire_compte()
    df = analyser()
    prix = float(df.iloc[-2]["close"])
    rsi = float(df.iloc[-2]["rsi"])
    signal = decider(df, cfg)

    valeur = float(compte["equity"])
    veille = float(compte["last_equity"])
    variation = valeur - veille
    pct = variation / veille * 100 if veille else 0.0

    lignes = [
        "BILAN QUOTIDIEN (compte démo, argent fictif)",
        "",
        f"Portefeuille : {valeur:,.2f} $".replace(",", " "),
        f"Variation depuis la veille : {variation:+.2f} $ ({pct:+.2f} %)",
        f"Liquidités : {float(compte['cash']):,.2f} $".replace(",", " "),
        "",
        f"Marché {cfg['symbol']} : {prix:,.2f} $".replace(",", " "),
        f"RSI : {rsi:.1f} | signal actuel : {signal}",
        "",
    ]

    position = position_ouverte()
    if position is None:
        lignes.append("Position : aucune (le bot attend un signal d'achat).")
    else:
        latent = (prix - position["prix_entree"]) * position["quantite"]
        lignes.append(
            f"Position : {position['quantite']} BTC, entrée à "
            f"{position['prix_entree']:.2f} $, stop loss à {position['prix_stop']} $."
        )
        lignes.append(f"Gain / perte latent : {latent:+.2f} $.")

    return "\n".join(lignes)


if __name__ == "__main__":
    texte = construire_bilan()
    print(texte)
    envoyer_recap(texte, sujet="Bilan quotidien bot trading")
    print("\nBilan envoyé.")
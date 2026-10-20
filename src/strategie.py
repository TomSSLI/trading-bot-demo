from analyse import analyser, charger_config


def decider(df, cfg):
    """Retourne 'ACHAT', 'VENTE' ou 'ATTENTE' selon la dernière bougie terminée."""
    # -2 = dernière bougie terminée, -3 = celle d'avant
    actuelle = df.iloc[-2]
    precedente = df.iloc[-3]

    croisement_haussier = (
        precedente["ema_rapide"] <= precedente["ema_lente"]
        and actuelle["ema_rapide"] > actuelle["ema_lente"]
    )
    croisement_baissier = (
        precedente["ema_rapide"] >= precedente["ema_lente"]
        and actuelle["ema_rapide"] < actuelle["ema_lente"]
    )

    if croisement_haussier and actuelle["rsi"] < cfg["rsi_buy_max"]:
        return "ACHAT"
    if croisement_baissier or actuelle["rsi"] < cfg["rsi_sell_min"]:
        return "VENTE"
    return "ATTENTE"


if __name__ == "__main__":
    cfg = charger_config()
    donnees = analyser()
    derniere = donnees.iloc[-2]
    print(f"Prix : {derniere['close']:.2f}")
    print(f"EMA rapide : {derniere['ema_rapide']:.2f} | EMA lente : {derniere['ema_lente']:.2f}")
    print(f"RSI : {derniere['rsi']:.1f}")
    print(f"Décision : {decider(donnees, cfg)}")